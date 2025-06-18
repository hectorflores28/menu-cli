import os
import webbrowser
import json
from simple_salesforce import Salesforce
from pathlib import Path

class SalesforceCLI:
    def __init__(self):
        self.config_dir = Path.home() / '.sf-cli'
        self.config_file = self.config_dir / 'config.json'
        self.sessions = {}
        self.current_session = None
        self.initialize_config()

    def initialize_config(self):
        if not self.config_dir.exists():
            self.config_dir.mkdir(parents=True)
        if not self.config_file.exists():
            self.save_config()

    def save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump({
                'sessions': self.sessions,
                'current_session': self.current_session
            }, f, indent=4)

    def load_config(self):
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                data = json.load(f)
                self.sessions = data.get('sessions', {})
                self.current_session = data.get('current_session')

def print_menu():
    print("""
.▄▄ ·  ▄▄▄· ▄▄▌  ▄▄▄ ..▄▄ · ·▄▄▄      ▄▄▄   ▄▄· ▄▄▄ .     ▄▄· ▄▄▌  ▪  
▐█ ▀. ▐█ ▀█ ██•  ▀▄.▀·▐█ ▀. ▐▄▄·▪     ▀▄ █·▐█ ▌▪▀▄.▀·    ▐█ ▌▪██•  ██ 
▄▀▀▀█▄▄█▀▀█ ██▪  ▐▀▀▪▄▄▀▀▀█▄██▪  ▄█▀▄ ▐▀▀▄ ██ ▄▄▐▀▀▪▄    ██ ▄▄██▪  ▐█·
▐█▄▪▐█▐█ ▪▐▌▐█▌▐▌▐█▄▄▌▐█▄▪▐███▌.▐█▌.▐▌▐█•█▌▐███▌▐█▄▄▌    ▐███▌▐█▌▐▌▐█▌
 ▀▀▀▀  ▀  ▀ .▀▀▀  ▀▀▀  ▀▀▀▀ ▀▀▀  ▀█▄▀▪.▀  ▀·▀▀▀  ▀▀▀     ·▀▀▀ .▀▀▀ ▀▀▀
""")
    print(""" Hecho por: Hector Flores \n""")
    print("╔══════════════════════════════════╗")
    print("║        MENÚ PRINCIPAL SF         ║")
    print("╠══════════════════════════════════╣")
    print("║ 1. Login                         ║")
    print("║ 2. Logout                        ║")
    print("║ 3. Cambiar sesión                ║")
    print("║ 4. Resetear contraseña usuario   ║")
    print("║ 5. Eliminar registro             ║")
    print("║ 6. Eliminación en cascada        ║")
    print("║ 7. Reemplazar Advisor            ║")
    print("║ 8. Ejecutar SOQL personalizado   ║")
    print("║ 9. Ver organización              ║")
    print("║ 10. Gestionar componentes        ║")
    print("║ 11. Push cambios                 ║")
    print("║ 12. Abrir navegador              ║")
    print("║ 13. Salir                        ║")
    print("╚══════════════════════════════════╝")
    print("""\n""")

def login():
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
        
        # Guardar sesión
        session_data = {
            'username': username,
            'instance_type': instance_type,
            'instance_url': sf.base_url,
            'access_token': sf.session_id
        }
        
        cli.sessions[session_name] = session_data
        cli.current_session = session_name
        cli.save_config()
        
        print(f"✓ Sesión '{session_name}' iniciada correctamente")
        return sf
    except Exception as e:
        print(f"Error en login: {str(e)}")
        return None

def logout():
    session_name = input("Nombre de la sesión a cerrar: ")
    if session_name in cli.sessions:
        del cli.sessions[session_name]
        if cli.current_session == session_name:
            cli.current_session = None
        cli.save_config()
        print(f"✓ Sesión '{session_name}' cerrada correctamente")
    else:
        print("Sesión no encontrada")

def switch_session():
    if not cli.sessions:
        print("No hay sesiones guardadas")
        return
    
    print("\nSesiones disponibles:")
    for name in cli.sessions.keys():
        print(f"- {name}")
    
    session_name = input("\nSelecciona una sesión: ")
    if session_name in cli.sessions:
        cli.current_session = session_name
        cli.save_config()
        print(f"✓ Cambiado a sesión '{session_name}'")
    else:
        print("Sesión no encontrada")

def reset_password():
    username = input("Username: ")
    new_password = input("Nueva contraseña: ")
    soql_code = f"""
User userToReset = [SELECT Id FROM User WHERE username='{username}' LIMIT 1];
System.setPassword(userToReset.Id, '{new_password}');
System.debug('Contraseña restablecida para: {username}');"""
 
    print("\\nCódigo SOQL generado:")
    print("═"*50)
    print(soql_code)
    print("═"*50)
    save_to_file(soql_code, "password_reset.soql")

def delete_record():
    object_type = input("Tipo de objeto (Lead/Account/Opportunity): ")
    record_id = input("ID del registro: ")

    soql_code = f"""
{object_type} recordToDelete = [SELECT Id FROM {object_type} WHERE Id = '{record_id}'];
delete recordToDelete;
System.debug('{object_type} eliminado: {record_id}');"""

    print("\\nCódigo SOQL generado:")
    print("═"*50)
    print(soql_code)
    print("═"*50)
    save_to_file(soql_code, "delete_record.soql")

# Queda pendiente
def cascade_delete():
    print("queda pendiente")

def replace_advisor():
    old_id = input("ID antiguo advisor: ")
    new_id = input("ID nuevo advisor: ")
    limit = input("Límite registros (default 200): ") or "200"
    date_range = input("Rango fechas (YYYY-MM-DD to YYYY-MM-DD): ")

    soql_code = f"""
String ANTIGUO_ADVISOR = '{old_id}';
String NUEVO_ADVISOR = '{new_id}';
Integer REGISTROS_LIMITE = {limit};

// Obtener oportunidades
List<Opportunity> oportunidades = [
    SELECT Id, Advisor_Pre_Arrival__c
    FROM Opportunity
    WHERE Arrival__c >= {date_range.split(' to ')[0]}
    AND Arrival__c <= {date_range.split(' to ')[1]}
    AND Advisor_Pre_Arrival__c = :ANTIGUO_ADVISOR
    LIMIT :REGISTROS_LIMITE
];

// Realizar reemplazos
for(Opportunity opp : oportunidades) {{
    opp.Advisor_Pre_Arrival__c = NUEVO_ADVISOR;
}}

update oportunidades;"""

    print("\\nCódigo SOQL generado:")
    print("═"*50)
    print(soql_code)
    print("═"*50)
    save_to_file(soql_code, "replace_advisor.soql")

def custom_soql():
    print("\\nTipos de consulta disponibles:")
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

    print("\\nConsulta generada:")
    print("═"*50)
    print(soql)
    print("═"*50)
    save_to_file(soql, "custom_query.soql")

def open_browser():
    if not cli.current_session:
        print("No hay sesión activa")
        return
    
    session = cli.sessions[cli.current_session]
    instance_url = session['instance_url']
    webbrowser.open(instance_url)
    print("✓ Navegador abierto")

def get_organization():
    if not cli.current_session:
        print("No hay sesión activa")
        return
    
    try:
        sf = Salesforce(
            instance_url=cli.sessions[cli.current_session]['instance_url'],
            session_id=cli.sessions[cli.current_session]['access_token']
        )
        
        org_info = sf.describe()
        print("\nInformación de la organización:")
        print(f"Nombre: {org_info['name']}")
        print(f"Edición: {org_info['edition']}")
        print(f"Organización ID: {org_info['organizationId']}")
        print(f"Instancia: {org_info['instanceName']}")
    except Exception as e:
        print(f"Error obteniendo información: {str(e)}")

def save_to_file(content, filename):
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

def manage_components():
    print("\n=== Gestión de Componentes ===")
    print("1. Listar componentes")
    print("2. Crear componente")
    print("3. Eliminar componente")
    
    choice = input("Selección: ")
    # Implementar lógica de componentes aquí

def push_changes():
    print("\n=== Push de Cambios ===")
    print("1. Push a test")
    print("2. Push a producción")
    
    choice = input("Selección: ")
    # Implementar lógica de push aquí

def main():
    global cli
    cli = SalesforceCLI()
    
    while True:
        print_menu()
        choice = input("Selecciona una opción: ")

        if choice == "1": login()
        elif choice == "2": logout()
        elif choice == "3": switch_session()
        elif choice == "4": reset_password()
        elif choice == "5": delete_record()
        elif choice == "6": cascade_delete()
        elif choice == "7": replace_advisor()
        elif choice == "8": custom_soql()
        elif choice == "9": get_organization()
        elif choice == "10": manage_components()
        elif choice == "11": push_changes()
        elif choice == "12": open_browser()
        elif choice == "13":
            print("¡Hasta pronto! ✨")
            break
        else:
            print("Opción inválida, intenta nuevamente")

        input("\nPresiona Enter para continuar...")
        os.system('cls' if os.name == 'nt' else 'clear')

if __name__ == "__main__":
    main()