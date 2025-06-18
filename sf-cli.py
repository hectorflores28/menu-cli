import os
import webbrowser
import json
from simple_salesforce.api import Salesforce
from pathlib import Path
from typing import Optional, Dict, Any

class SalesforceSession:
    def __init__(self, username: str, instance_type: str, instance_url: str, access_token: str):
        self.username = username
        self.instance_type = instance_type
        self.instance_url = instance_url
        self.access_token = access_token

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SalesforceSession':
        return cls(
            username=data['username'],
            instance_type=data['instance_type'],
            instance_url=data['instance_url'],
            access_token=data['access_token']
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            'username': self.username,
            'instance_type': self.instance_type,
            'instance_url': self.instance_url,
            'access_token': self.access_token
        }

class SalesforceCLI:
    def __init__(self):
        self.config_dir = Path.home() / '.sf-cli'
        self.config_file = self.config_dir / 'config.json'
        self.sessions: Dict[str, SalesforceSession] = {}
        self.current_session: Optional[str] = None
        self.initialize_config()

    def initialize_config(self):
        if not self.config_dir.exists():
            self.config_dir.mkdir(parents=True)
        if not self.config_file.exists():
            self.save_config()
        else:
            self.load_config()

    def save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump({
                'sessions': {name: session.to_dict() for name, session in self.sessions.items()},
                'current_session': self.current_session
            }, f, indent=4)

    def load_config(self):
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                data = json.load(f)
                self.sessions = {
                    name: SalesforceSession.from_dict(session_data)
                    for name, session_data in data.get('sessions', {}).items()
                }
                self.current_session = data.get('current_session')

    def get_current_sf(self) -> Optional[Salesforce]:
        if not self.current_session or self.current_session not in self.sessions:
            return None
        
        session = self.sessions[self.current_session]
        return Salesforce(
            instance_url=session.instance_url,
            session_id=session.access_token
        )

class SessionManager:
    def __init__(self, cli: SalesforceCLI):
        self.cli = cli

    def login(self) -> Optional[Salesforce]:
        print("=== Login a Salesforce ===")
        instance_type = input("Tipo de instancia (prod/test): ").lower()
        username = input("Username: ")
        password = input("Password: ")
        security_token = input("Security Token: ")
        session_name = input("Nombre para esta sesión: ")

        try:
            sf = Salesforce(
                username=username,
                password=password,
                security_token=security_token,
                domain='test' if instance_type == 'test' else 'login'
            )
            
            session = SalesforceSession(
                username=username,
                instance_type=instance_type,
                instance_url=sf.base_url,
                access_token=sf.session_id
            )
            
            self.cli.sessions[session_name] = session
            self.cli.current_session = session_name
            self.cli.save_config()
            
            print(f"✓ Sesión '{session_name}' iniciada correctamente")
            return sf
        except Exception as e:
            print(f"Error en login: {str(e)}")
            return None

    def logout(self):
        session_name = input("Nombre de la sesión a cerrar: ")
        if session_name in self.cli.sessions:
            del self.cli.sessions[session_name]
            if self.cli.current_session == session_name:
                self.cli.current_session = None
            self.cli.save_config()
            print(f"✓ Sesión '{session_name}' cerrada correctamente")
        else:
            print("Sesión no encontrada")

    def switch_session(self):
        if not self.cli.sessions:
            print("No hay sesiones guardadas")
            return
        
        print("\nSesiones disponibles:")
        for name in self.cli.sessions.keys():
            print(f"- {name}")
        
        session_name = input("\nSelecciona una sesión: ")
        if session_name in self.cli.sessions:
            self.cli.current_session = session_name
            self.cli.save_config()
            print(f"✓ Cambiado a sesión '{session_name}'")
        else:
            print("Sesión no encontrada")

class UserManager:
    def __init__(self, cli: SalesforceCLI):
        self.cli = cli

    def reset_password(self):
        username = input("Username: ")
        new_password = input("Nueva contraseña: ")
        soql_code = f"""
User userToReset = [SELECT Id FROM User WHERE username='{username}' LIMIT 1];
System.setPassword(userToReset.Id, '{new_password}');
System.debug('Contraseña restablecida para: {username}');"""
 
        print("\nCódigo SOQL generado:")
        print("═"*50)
        print(soql_code)
        print("═"*50)
        save_to_file(soql_code, "password_reset.soql")

class RecordManager:
    def __init__(self, cli: SalesforceCLI):
        self.cli = cli

    def delete_record(self):
        object_type = input("Tipo de objeto (Lead/Account/Opportunity): ")
        record_id = input("ID del registro: ")

        soql_code = f"""
{object_type} recordToDelete = [SELECT Id FROM {object_type} WHERE Id = '{record_id}'];
delete recordToDelete;
System.debug('{object_type} eliminado: {record_id}');"""

        print("\nCódigo SOQL generado:")
        print("═"*50)
        print(soql_code)
        print("═"*50)
        save_to_file(soql_code, "delete_record.soql")

    def replace_advisor(self):
        old_id = input("ID antiguo advisor: ")
        new_id = input("ID nuevo advisor: ")
        limit = input("Límite registros (default 200): ") or "200"
        date_range = input("Rango fechas (YYYYMMDD to YYYYMMDD): ")

        soql_code = f"""
        String ANTIGUO_ADVISOR = '{old_id}';
        String NUEVO_ADVISOR = '{new_id}';
        Integer REGISTROS_LIMITE = {limit};

        List<Opportunity> oportunidades = [
            SELECT Id, Advisor_Pre_Arrival__c
            FROM Opportunity
            WHERE Arrival__c >= {date_range.split(' to ')[0]}
            AND Arrival__c <= {date_range.split(' to ')[1]}
            AND Advisor_Pre_Arrival__c = :ANTIGUO_ADVISOR
            LIMIT :REGISTROS_LIMITE
        ];

        for(Opportunity opp : oportunidades) {{
            opp.Advisor_Pre_Arrival__c = NUEVO_ADVISOR;
        }}

        update oportunidades;
        """

        print("\nCódigo SOQL generado:")
        print("═"*50)
        print(soql_code)
        print("═"*50)
        save_to_file(soql_code, "replace_advisor.soql")

class QueryManager:
    def __init__(self, cli: SalesforceCLI):
        self.cli = cli

    def custom_soql(self):
        print("\nTipos de consulta disponibles:")
        print("1. Leads por rango de fechas")
        print("2. Oportunidades por advisor")
        print("3. Personalizado")
        choice = input("Selección: ")

        if choice == "1":
            start_date = input("Fecha inicio (YYYY-MM-DD): ")
            end_date = input("Fecha fin (YYYY-MM-DD): ")
            soql = f"SELECT Id, Email, Email2__c FROM Lead WHERE CreatedDate >= {start_date}T00:00:00Z AND CreatedDate <= {end_date}T23:59:59Z"
        elif choice == "2":
            advisor_id = input("ID del advisor: ")
            soql = f"SELECT Id, Name, StageName FROM Opportunity WHERE Advisor_Pre_Arrival__c = '{advisor_id}'"
        else:
            soql = input("Ingresa tu consulta SOQL: ")

        print("\nConsulta generada:")
        print("═"*50)
        print(soql)
        print("═"*50)
        save_to_file(soql, "custom_query.soql")

class OrganizationManager:
    def __init__(self, cli: SalesforceCLI):
        self.cli = cli

    def get_organization_info(self):
        if not self.cli.current_session:
            print("No hay sesión activa")
            return
        
        try:
            sf = self.cli.get_current_sf()
            if not sf:
                print("Error: No se pudo obtener la sesión de Salesforce")
                return

            org_info = sf.describe()
            if not org_info:
                print("Error: No se pudo obtener información de la organización")
                return

            print("\nInformación de la organización:")
            print(f"Nombre: {org_info.get('name', 'N/A')}")
            print(f"Edición: {org_info.get('edition', 'N/A')}")
            print(f"Organización ID: {org_info.get('organizationId', 'N/A')}")
            print(f"Instancia: {org_info.get('instanceName', 'N/A')}")
        except Exception as e:
            print(f"Error obteniendo información: {str(e)}")

    def open_browser(self):
        if not self.cli.current_session:
            print("No hay sesión activa")
            return
        
        session = self.cli.sessions[self.cli.current_session]
        webbrowser.open(session.instance_url)
        print("✓ Navegador abierto")

def print_menu():
    print("""
.▄▄ ·  ▄▄▄· ▄▄▌  ▄▄▄ ..▄▄ · ·▄▄▄      ▄▄▄   ▄▄· ▄▄▄ .     ▄▄· ▄▄▌  ▪  
▐█ ▀. ▐█ ▀█ ██•  ▀▄.▀·▐█ ▀. ▐▄▄·▪     ▀▄ █·▐█ ▌▪▀▄.▀·    ▐█ ▌▪██•  ██ 
▄▀▀▀█▄▄█▀▀█ ██▪  ▐▀▀▪▄▄▀▀▀█▄██▪  ▄█▀▄ ▐▀▀▄ ██ ▄▄▐▀▀▪▄    ██ ▄▄██▪  ▐█·
▐█▄▪▐█▐█ ▪▐▌▐█▌▐▌▐█▄▄▌▐█▄▪▐███▌.▐█▌.▐▌▐█•█▌▐███▌▐█▄▄▌    ▐███▌▐█▌▐▌▐█▌
 ▀▀▀▀  ▀  ▀ .▀▀▀  ▀▀▀  ▀▀▀▀ ▀▀▀  ▀█▄▀▪.▀  ▀·▀▀▀  ▀▀▀     ·▀▀▀ .▀▀▀ ▀▀▀
""")
    # print(""" Hecho por: Hector Flores \n""")
    print("╔══════════════════════════════════╗")
    print("║        MENÚ PRINCIPAL SF         ║")
    print("╠══════════════════════════════════╣")
    print("║ 1. Gestión de Sesiones           ║")
    print("║ 2. Gestión de Usuarios           ║")
    print("║ 3. Gestión de Registros          ║")
    print("║ 4. Consultas SOQL                ║")
    print("║ 5. Información de Organización   ║")
    print("║ 6. Salir                         ║")
    print("╚══════════════════════════════════╝\n")

def print_submenu(menu_type: str):
    if menu_type == "sesiones":
        print("\n=== Gestión de Sesiones ===")
        print("1. Login")
        print("2. Logout")
        print("3. Cambiar sesión")
        print("4. Volver al menú principal")
    elif menu_type == "usuarios":
        print("\n=== Gestión de Usuarios ===")
        print("1. Resetear contraseña")
        print("2. Volver al menú principal")
    elif menu_type == "registros":
        print("\n=== Gestión de Registros ===")
        print("1. Eliminar registro")
        print("2. Reemplazar Advisor")
        print("3. Volver al menú principal")
    elif menu_type == "consultas":
        print("\n=== Consultas SOQL ===")
        print("1. Ejecutar SOQL personalizado")
        print("2. Volver al menú principal")
    elif menu_type == "organizacion":
        print("\n=== Información de Organización ===")
        print("1. Ver organización")
        print("2. Abrir navegador")
        print("3. Volver al menú principal")

def save_to_file(content: str, filename: str):
    output_dir = Path("outputs")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = output_dir / filename
    try:
        with open(file_path, 'w') as f:
            f.write(content)
        print(f"✓ Archivo guardado: {filename}")
        print(f"✓ Ubicación: {os.path.abspath(file_path)}")
    except Exception as e:
        print(f"Error guardando archivo: {str(e)}")

def main():
    cli = SalesforceCLI()
    session_manager = SessionManager(cli)
    user_manager = UserManager(cli)
    record_manager = RecordManager(cli)
    query_manager = QueryManager(cli)
    org_manager = OrganizationManager(cli)
    
    while True:
        print_menu()
        choice = input("Selecciona una opción: ")

        if choice == "1":  # Gestión de Sesiones
            while True:
                print_submenu("sesiones")
                subchoice = input("Selección: ")
                if subchoice == "1": session_manager.login()
                elif subchoice == "2": session_manager.logout()
                elif subchoice == "3": session_manager.switch_session()
                elif subchoice == "4": break

        elif choice == "2":  # Gestión de Usuarios
            while True:
                print_submenu("usuarios")
                subchoice = input("Selección: ")
                if subchoice == "1": user_manager.reset_password()
                elif subchoice == "2": break

        elif choice == "3":  # Gestión de Registros
            while True:
                print_submenu("registros")
                subchoice = input("Selección: ")
                if subchoice == "1": record_manager.delete_record()
                elif subchoice == "2": record_manager.replace_advisor()
                elif subchoice == "3": break

        elif choice == "4":  # Consultas SOQL
            while True:
                print_submenu("consultas")
                subchoice = input("Selección: ")
                if subchoice == "1": query_manager.custom_soql()
                elif subchoice == "2": break

        elif choice == "5":  # Información de Organización
            while True:
                print_submenu("organizacion")
                subchoice = input("Selección: ")
                if subchoice == "1": org_manager.get_organization_info()
                elif subchoice == "2": org_manager.open_browser()
                elif subchoice == "3": break

        elif choice == "6":
            print("¡Hasta pronto! ✨")
            break
        else:
            print("Opción inválida, intenta nuevamente")

        input("\nPresiona Enter para continuar...")
        os.system('cls' if os.name == 'nt' else 'clear')

if __name__ == "__main__":
    main()