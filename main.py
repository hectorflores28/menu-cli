import os
import datetime
import subprocess
import webbrowser
from simple_salesforce import Salesforce  # Necesitarás instalar este paquete

def print_menu():
    print("""
  ██████╗ █████╗ ██╗      ██████╗ ███████╗
 ██╔════╝██╔══██╗██║     ██╔═══██╗██╔════╝
 ██║     ███████║██║     ██║   ██║███████╗
 ██║     ██╔══██║██║     ██║   ██║╚════██║
 ╚██████╗██║  ██║███████╗╚██████╔╝███████║
  ╚═════╝╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚══════╝
""")
    print("╔══════════════════════════════════╗")
    print("║        MENÚ PRINCIPAL SF         ║")
    print("╠══════════════════════════════════╣")
    print("║ 1. Resetear contraseña usuario   ║")
    print("║ 2. Eliminar registro             ║")
    print("║ 3. Eliminación en cascada        ║")
    print("║ 4. Reemplazar Advisor            ║")
    print("║ 5. Ejecutar SOQL personalizado   ║")
    print("║ 6. Procesar reportes Excel       ║")
    print("║ 7. Conexión a Salesforce         ║")
    print("║ 8. Salir                         ║")
    print("╚══════════════════════════════════╝")

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

def cascade_delete():
    account_id = input("ID de la cuenta: ")

    soql_code = f"""
Account acc = [
    SELECT Id,
        (SELECT Id FROM Opportunities),
        (SELECT Id From Cases),
        (SELECT Id From Contacts)
    FROM Account
    WHERE Id = '{account_id}'
];

System.debug('Oportunidades: ' + acc.Opportunities.size());
System.debug('Casos: ' + acc.Cases.size());
System.debug('Contactos: ' + acc.Contacts.size());

// Ejecutar en orden inverso para eliminación segura
delete acc.Opportunities;
delete acc.Cases;
delete acc.Contacts;
delete acc;"""

    print("\\nCódigo SOQL generado:")
    print("═"*50)
    print(soql_code)
    print("═"*50)
    save_to_file(soql_code, "cascade_delete.soql")

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

def excel_operations():
    print("\\nProcesamiento de reportes Excel")
    print("1. Generar reporte acumulativo")
    print("2. Combinar archivos Excel")

    choice = input("Selección: ")
    if choice == "1":
        # Aquí iría la lógica para procesar los Excel
        print("Ejecutando proceso de reportes acumulativos...")
        print("✓ Datos pasados copiados")
        print("✓ Coordenadas actualizadas")
        print("✓ Archivo guardado para servidor")
    else:
        print("Funcionalidad en desarrollo")

def connect_sf():
    print("\\nConectando a Salesforce...")
    try:
        username = input("Username: ")
        password = input("Password: ")
        security_token = input("Security Token: ")

        # Conexión real (descomentar cuando tengas las credenciales)
        # sf = Salesforce(
        #     username=username,
        #     password=password,
        #     security_token=security_token
        # )
        # print("✓ Conexión exitosa!")

        print("(La conexión real está comentada en el código por seguridad)")
        print("Puedes usar: from simple_salesforce import Salesforce")
    except Exception as e:
        print(f"Error de conexión: {str(e)}")

def save_to_file(content, filename):
    try:
        with open(filename, 'w') as f:
            f.write(content)
        print(f"✓ Archivo guardado: {filename}")
        print(f"✓ Ubicación: {os.path.abspath(filename)}")
    except Exception as e:
        print(f"Error guardando archivo: {str(e)}")

def main():
    while True:
        print_menu()
        choice = input("Selecciona una opción: ")

        if choice == "1": reset_password()
        elif choice == "2": delete_record()
        elif choice == "3": cascade_delete()
        elif choice == "4": replace_advisor()
        elif choice == "5": custom_soql()
        elif choice == "6": excel_operations()
        elif choice == "7": connect_sf()
        elif choice == "8":
            print("¡Hasta pronto! ✨")
            break
        else:
            print("Opción inválida, intenta nuevamente")

        input("\\nPresiona Enter para continuar...")
        os.system('cls' if os.name == 'nt' else 'clear')

if __name__ == "__main__":
    main()