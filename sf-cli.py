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

    def validate_current_session(self) -> bool:
        """Valida si la sesión actual es válida"""
        if not self.current_session or self.current_session not in self.sessions:
            return False
        
        try:
            sf = self.get_current_sf()
            if not sf:
                return False
            
            # Intentar una operación simple para validar la sesión
            sf.describe()
            return True
        except Exception:
            return False

    def refresh_session(self) -> bool:
        """Intenta refrescar la sesión actual"""
        if not self.current_session or self.current_session not in self.sessions:
            return False
        
        session = self.sessions[self.current_session]
        print(f"Intentando refrescar sesión '{self.current_session}'...")
        
        # Para refrescar, necesitaríamos las credenciales originales
        # Por ahora, solo marcamos la sesión como inválida
        print("La sesión ha expirado. Por favor, haz login nuevamente.")
        return False

class SessionManager:
    def __init__(self, cli: SalesforceCLI):
        self.cli = cli

    def quick_trailhead_login(self) -> Optional[Salesforce]:
        """Login rápido para organizaciones de Trailhead"""
        print("=== Login Rápido Trailhead ===")
        print("Este modo está optimizado para organizaciones de Trailhead")
        print("El security token se generará automáticamente\n")
        
        username = input("Username de Trailhead: ").strip()
        password = input("Password: ").strip()
        session_name = input("Nombre para esta sesión: ").strip()
        
        # Para Trailhead, el security token suele ser la contraseña + números específicos
        trailhead_tokens = [
            password + "123456",
            password + "123456789", 
            password + "000000",
            password + "111111",
            password + "222222",
            password + "333333",
            password + "444444",
            password + "555555",
            password + "666666",
            password + "777777",
            password + "888888",
            password + "999999",
            password + "123123",
            password + "456456",
            password + "789789",
        ]
        
        print(f"\nIntentando conectar a Trailhead...")
        
        for i, token in enumerate(trailhead_tokens):
            try:
                print(f"Intento {i+1}/{len(trailhead_tokens)}...")
                
                sf = Salesforce(
                    username=username,
                    password=password,
                    security_token=token,
                    domain="test"
                )
                
                session = SalesforceSession(
                    username=username,
                    instance_type="trailhead",
                    instance_url=sf.base_url,
                    access_token=sf.session_id
                )
                
                self.cli.sessions[session_name] = session
                self.cli.current_session = session_name
                self.cli.save_config()
                
                print(f"✓ Sesión Trailhead '{session_name}' iniciada correctamente")
                print(f"✓ URL: {sf.base_url}")
                print(f"✓ Token usado: {token[-6:] if len(token) > 6 else token}")
                return sf
                
            except Exception as e:
                error_msg = str(e)
                if "INVALID_LOGIN" in error_msg or "INVALID_GRANT" in error_msg:
                    continue
                else:
                    print(f"Error inesperado: {error_msg}")
                    break
        
        print("❌ No se pudo conectar a Trailhead")
        print("Sugerencias:")
        print("- Verifica que el username y password sean correctos")
        print("- Asegúrate de que la organización de Trailhead esté activa")
        print("- Intenta con el modo de login completo")
        return None

    def login(self) -> Optional[Salesforce]:
        print("=== Login a Salesforce ===")
        print("Tipos de instancia disponibles:")
        print("1. Producción (login.salesforce.com)")
        print("2. Sandbox (test.salesforce.com)")
        print("3. Trailhead (test.salesforce.com)")
        print("4. Login rápido Trailhead")
        
        instance_choice = input("Selecciona el tipo de instancia (1/2/3/4): ").strip()
        
        if instance_choice == "4":
            return self.quick_trailhead_login()
        elif instance_choice == "1":
            instance_type = "prod"
            domain = "login"
        elif instance_choice in ["2", "3"]:
            instance_type = "test"
            domain = "test"
        else:
            print("Opción inválida")
            return None

        username = input("Username: ").strip()
        password = input("Password: ").strip()
        
        # Para Trailhead y sandboxes, el security token suele ser la contraseña + un número
        # Intentamos diferentes combinaciones automáticamente
        security_tokens = [
            "",  # Sin token
            password + "123456",
            password + "123456789",
            password + "000000",
            password + "111111",
            password + "222222",
            password + "333333",
            password + "444444",
            password + "555555",
            password + "666666",
            password + "777777",
            password + "888888",
            password + "999999",
        ]
        
        # También preguntamos si el usuario quiere ingresar un token manual
        manual_token = input("¿Tienes un security token específico? (s/n): ").strip().lower()
        if manual_token == 's':
            custom_token = input("Ingresa tu security token: ").strip()
            security_tokens.insert(0, custom_token)
        
        session_name = input("Nombre para esta sesión: ").strip()
        
        print(f"\nIntentando conectar a {instance_type}...")
        
        # Intentar conectar con diferentes tokens
        for i, token in enumerate(security_tokens):
            try:
                print(f"Intento {i+1}/{len(security_tokens)}...")
                
                sf = Salesforce(
                    username=username,
                    password=password,
                    security_token=token,
                    domain=domain
                )
                
                # Si llegamos aquí, la conexión fue exitosa
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
                print(f"✓ URL de la instancia: {sf.base_url}")
                print(f"✓ Token usado: {'(sin token)' if not token else '(token personalizado)' if i == 0 and manual_token == 's' else f'(token automático {i})'}")
                return sf
                
            except Exception as e:
                error_msg = str(e)
                if "INVALID_LOGIN" in error_msg:
                    continue  # Intentar con el siguiente token
                elif "INVALID_GRANT" in error_msg:
                    continue  # Intentar con el siguiente token
                else:
                    print(f"Error inesperado: {error_msg}")
                    break
        
        print("❌ No se pudo conectar con ninguna combinación de credenciales")
        print("Sugerencias:")
        print("- Verifica que el username y password sean correctos")
        print("- Para Trailhead: el security token suele ser la contraseña + números")
        print("- Para producción: verifica que tengas el security token correcto")
        print("- Asegúrate de que la cuenta no esté bloqueada")
        print("- Intenta con el login rápido de Trailhead (opción 4)")
        return None

    def logout(self):
        if not self.cli.sessions:
            print("No hay sesiones guardadas")
            return
            
        print("\nSesiones disponibles:")
        for i, name in enumerate(self.cli.sessions.keys(), 1):
            session = self.cli.sessions[name]
            current_marker = " (ACTUAL)" if name == self.cli.current_session else ""
            print(f"{i}. {name} - {session.username}@{session.instance_type}{current_marker}")
        
        try:
            choice = input("\nSelecciona el número de sesión a cerrar: ").strip()
            session_names = list(self.cli.sessions.keys())
            if choice.isdigit() and 1 <= int(choice) <= len(session_names):
                session_name = session_names[int(choice) - 1]
            else:
                session_name = choice
                
            if session_name in self.cli.sessions:
                del self.cli.sessions[session_name]
                if self.cli.current_session == session_name:
                    self.cli.current_session = None
                self.cli.save_config()
                print(f"✓ Sesión '{session_name}' cerrada correctamente")
            else:
                print("Sesión no encontrada")
        except (ValueError, IndexError):
            print("Selección inválida")

    def switch_session(self):
        if not self.cli.sessions:
            print("No hay sesiones guardadas")
            return
        
        print("\nSesiones disponibles:")
        for i, name in enumerate(self.cli.sessions.keys(), 1):
            session = self.cli.sessions[name]
            current_marker = " (ACTUAL)" if name == self.cli.current_session else ""
            print(f"{i}. {name} - {session.username}@{session.instance_type}{current_marker}")
        
        try:
            choice = input("\nSelecciona el número de sesión: ").strip()
            session_names = list(self.cli.sessions.keys())
            if choice.isdigit() and 1 <= int(choice) <= len(session_names):
                session_name = session_names[int(choice) - 1]
            else:
                session_name = choice
                
            if session_name in self.cli.sessions:
                self.cli.current_session = session_name
                self.cli.save_config()
                session = self.cli.sessions[session_name]
                print(f"✓ Cambiado a sesión '{session_name}' ({session.username}@{session.instance_type})")
            else:
                print("Sesión no encontrada")
        except (ValueError, IndexError):
            print("Selección inválida")

    def list_sessions(self):
        if not self.cli.sessions:
            print("No hay sesiones guardadas")
            return
            
        print("\n=== Sesiones Guardadas ===")
        for i, name in enumerate(self.cli.sessions.keys(), 1):
            session = self.cli.sessions[name]
            current_marker = " (ACTUAL)" if name == self.cli.current_session else ""
            print(f"{i}. {name} - {session.username}@{session.instance_type}{current_marker}")
            print(f"   URL: {session.instance_url}")

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
            print("❌ No hay sesión activa")
            print("💡 Ve a 'Gestión de Sesiones' para hacer login")
            return
        
        # Validar la sesión actual
        if not self.cli.validate_current_session():
            print("❌ La sesión actual ha expirado")
            print("💡 Ve a 'Gestión de Sesiones' para refrescar la sesión")
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

            print("\n📊 Información de la organización:")
            print("═" * 50)
            print(f"🏢 Nombre: {org_info.get('name', 'N/A')}")
            print(f"📋 Edición: {org_info.get('edition', 'N/A')}")
            print(f"🆔 Organización ID: {org_info.get('organizationId', 'N/A')}")
            print(f"🌐 Instancia: {org_info.get('instanceName', 'N/A')}")
            print(f"📅 Fecha de creación: {org_info.get('createdDate', 'N/A')}")
            print(f"🔧 URL de la API: {org_info.get('urls', {}).get('sobjects', 'N/A')}")
            print("═" * 50)
        except Exception as e:
            print(f"❌ Error obteniendo información: {str(e)}")
            print("💡 La sesión puede haber expirado. Intenta refrescar la sesión.")

    def open_browser(self):
        if not self.cli.current_session:
            print("❌ No hay sesión activa")
            print("💡 Ve a 'Gestión de Sesiones' para hacer login")
            return
        
        session = self.cli.sessions[self.cli.current_session]
        try:
            webbrowser.open(session.instance_url)
            print(f"✓ Navegador abierto en: {session.instance_url}")
        except Exception as e:
            print(f"❌ Error abriendo navegador: {str(e)}")
            print(f"💡 Puedes abrir manualmente: {session.instance_url}")

    def test_connection(self):
        """Prueba la conexión actual"""
        if not self.cli.current_session:
            print("❌ No hay sesión activa")
            return False
        
        print(f"🔍 Probando conexión a '{self.cli.current_session}'...")
        
        if self.cli.validate_current_session():
            print("✅ Conexión exitosa")
            return True
        else:
            print("❌ Conexión fallida - La sesión puede haber expirado")
            return False

def show_help():
    print("\n" + "═" * 60)
    print("🔧 AYUDA - SF CLI TOOL")
    print("═" * 60)
    print("Esta herramienta te ayuda a gestionar Salesforce de forma eficiente.")
    print("\n📋 FUNCIONES PRINCIPALES:")
    print("• Gestión de Sesiones: Conecta a múltiples organizaciones")
    print("• Gestión de Usuarios: Operaciones con usuarios")
    print("• Gestión de Registros: Operaciones CRUD")
    print("• Consultas SOQL: Ejecutar consultas personalizadas")
    print("• Información de Organización: Ver detalles de la org")
    print("\n🚀 CONSEJOS DE USO:")
    print("• Para Trailhead: Usa 'Login rápido Trailhead'")
    print("• Para producción: Usa 'Login' con tu security token")
    print("• Puedes tener múltiples sesiones activas")
    print("• Los archivos SOQL se guardan en la carpeta 'outputs'")
    print("\n🔐 SEGURIDAD:")
    print("• Las credenciales se guardan localmente")
    print("• Usa 'Logout' para eliminar sesiones")
    print("• Los tokens se prueban automáticamente")
    print("═" * 60)

def show_current_session(cli: SalesforceCLI):
    if cli.current_session and cli.current_session in cli.sessions:
        session = cli.sessions[cli.current_session]
        print(f"🔗 Sesión activa: {cli.current_session} ({session.username}@{session.instance_type})")
        
        # Validar la sesión
        if cli.validate_current_session():
            print("✅ Conexión válida")
        else:
            print("⚠️  Sesión expirada - Considera refrescar")
    else:
        print("❌ No hay sesión activa")
    print()

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
    print("║ 6. Ayuda                         ║")
    print("║ 7. Salir                         ║")
    print("╚══════════════════════════════════╝\n")

def print_submenu(menu_type: str):
    if menu_type == "sesiones":
        print("\n=== Gestión de Sesiones ===")
        print("1. Login")
        print("2. Logout")
        print("3. Cambiar sesión")
        print("4. Listar sesiones")
        print("5. Volver al menú principal")
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
        print("3. Probar conexión")
        print("4. Volver al menú principal")

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
        show_current_session(cli)
        choice = input("Selecciona una opción: ")

        if choice == "1":  # Gestión de Sesiones
            while True:
                print_submenu("sesiones")
                subchoice = input("Selección: ")
                if subchoice == "1": session_manager.login()
                elif subchoice == "2": session_manager.logout()
                elif subchoice == "3": session_manager.switch_session()
                elif subchoice == "4": session_manager.list_sessions()
                elif subchoice == "5": break

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
                elif subchoice == "3": org_manager.test_connection()
                elif subchoice == "4": break

        elif choice == "6":  # Ayuda
            show_help()

        elif choice == "7":
            print("¡Hasta pronto! ✨")
            break
        else:
            print("Opción inválida, intenta nuevamente")

        input("\nPresiona Enter para continuar...")
        os.system('cls' if os.name == 'nt' else 'clear')

if __name__ == "__main__":
    main()