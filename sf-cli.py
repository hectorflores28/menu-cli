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
    instance_type = input("Tipo de instancia (prod/sandbox): ").lower()
    username = input("Username: ")
    password = input("Password: ")
    security_token = input("Security Token: ")
    session_name = input("Nombre para esta sesión: ")

    try:
        sf = Salesforce(
            username=username,
            password=password,
            security_token=security_token,
            domain='test' if instance_type == 'sandbox' else 'login'
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

def manage_components():
    print("\n=== Gestión de Componentes ===")
    print("1. Listar componentes")
    print("2. Crear componente")
    print("3. Eliminar componente")
    
    choice = input("Selección: ")
    # Implementar lógica de componentes aquí

def push_changes():
    print("\n=== Push de Cambios ===")
    print("1. Push a sandbox")
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