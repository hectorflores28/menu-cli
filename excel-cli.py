import os
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
import openpyxl
from openpyxl.styles import PatternFill, Font
from openpyxl.utils import get_column_letter

class ExcelCLI:
    def __init__(self):
        self.current_file = None
        self.df = None
        self.template_dir = Path('templates')
        self.output_dir = Path('output')
        self.initialize_dirs()

    def initialize_dirs(self):
        self.template_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)

    def load_file(self, filepath):
        try:
            self.current_file = filepath
            self.df = pd.read_excel(filepath)
            print(f"✓ Archivo cargado: {filepath}")
            return True
        except Exception as e:
            print(f"Error cargando archivo: {str(e)}")
            return False

def print_menu():
    print("""
888~~                             888        e88~-_  888     888
888___ Y88b  /   e88~~\  e88~~8e  888       d888   \ 888     888
888     Y88b/   d888    d888  88b 888       8888     888     888
888      Y88b   8888    8888__888 888       8888     888     888
888      /Y88b  Y888    Y888    , 888       Y888   / 888     888
888___  /  Y88b  "88__/  "88___/  888        "88_-~  888____ 888
""")
    print(""" Hecho por: Hector Flores \n""")
    print("╔══════════════════════════════════╗")
    print("║        MENÚ PRINCIPAL EXCEL      ║")
    print("╠══════════════════════════════════╣")
    print("║ 1. Cargar archivo Excel          ║")
    print("║ 2. Análisis de datos             ║")
    print("║ 3. Generar fórmulas              ║")
    print("║ 4. Procesar reportes             ║")
    print("║ 5. Exportar resultados           ║")
    print("║ 6. Salir                         ║")
    print("╚══════════════════════════════════╝")
    print("""\n""")

def analyze_data():
    print("\n=== Análisis de Datos ===")
    print("1. Análisis de duplicados")
    print("2. Análisis de valores únicos")
    print("3. Estadísticas descriptivas")
    print("4. Análisis de fechas")
    print("5. Volver al menú principal")
    
    choice = input("Selección: ")
    
    if choice == "1":
        column = input("Columna a analizar: ")
        duplicates = cli.df[column].duplicated()
        print(f"\nTotal duplicados: {duplicates.sum()}")
        print("\nEjemplos de duplicados:")
        print(cli.df[cli.df[column].duplicated(keep=False)].head())
    
    elif choice == "2":
        column = input("Columna a analizar: ")
        unique_values = cli.df[column].nunique()
        print(f"\nTotal valores únicos: {unique_values}")
        print("\nPrimeros 5 valores únicos:")
        print(cli.df[column].unique()[:5])
    
    elif choice == "3":
        print("\nEstadísticas descriptivas:")
        print(cli.df.describe())
    
    elif choice == "4":
        date_columns = cli.df.select_dtypes(include=['datetime64']).columns
        if len(date_columns) > 0:
            print("\nColumnas de fecha encontradas:")
            for col in date_columns:
                print(f"\n{col}:")
                print(f"Rango: {cli.df[col].min()} a {cli.df[col].max()}")
        else:
            print("No se encontraron columnas de fecha")

def generate_formulas():
    print("\n=== Generador de Fórmulas ===")
    print("1. Fórmula de duplicados")
    print("2. Fórmula de valores únicos")
    print("3. Fórmula de estado")
    print("4. Fórmula de fechas")
    print("5. Volver al menú principal")
    
    choice = input("Selección: ")
    
    if choice == "1":
        print("\nFórmula para detectar duplicados:")
        print("=IF(COUNTIF($A$2:$A2, A2) > 1, \"Duplicado\", \"Único\")")
    
    elif choice == "2":
        print("\nFórmula para valores únicos:")
        print("=IFERROR(INDEX($A$2:$A$1000, MATCH(0, COUNTIF($D$1:D1, $A$2:$A$1000), 0)), \"\")")
    
    elif choice == "3":
        print("\nFórmula de estado:")
        print("=IF(ISBLANK(A2), \"\", IF(COUNTIF($A$2:$A2, A2) > 1, \"Duplicado\", IF(ISNUMBER(MATCH(A2, $B$2:$B$1000, 0)), \"Existente\", \"Nuevo\")))")
    
    elif choice == "4":
        print("\nFórmula para fechas:")
        print("=IF(AND(A2>=DATE(2024,1,1), A2<=DATE(2024,12,31)), \"2024\", \"Otro Año\")")

def process_reports():
    print("\n=== Procesamiento de Reportes ===")
    print("1. Generar reporte acumulativo")
    print("2. Actualizar coordenadas")
    print("3. Combinar reportes")
    print("4. Volver al menú principal")
    
    choice = input("Selección: ")
    
    if choice == "1":
        template = input("Ruta del template: ")
        past_data = input("Ruta de datos pasados: ")
        current_data = input("Ruta de datos actuales: ")
        
        try:
            # Cargar datos
            past_df = pd.read_excel(past_data)
            current_df = pd.read_excel(current_data)
            
            # Combinar datos
            combined_df = pd.concat([past_df, current_df], ignore_index=True)
            
            # Guardar resultado
            output_path = cli.output_dir / f"reporte_acumulativo_{datetime.now().strftime('%Y%m%d')}.xlsx"
            combined_df.to_excel(output_path, index=False)
            print(f"✓ Reporte generado: {output_path}")
            
        except Exception as e:
            print(f"Error procesando reporte: {str(e)}")

def export_results():
    if cli.df is None:
        print("No hay datos cargados")
        return
    
    print("\n=== Exportar Resultados ===")
    print("1. Exportar a Excel")
    print("2. Exportar a CSV")
    print("3. Exportar a SQL")
    print("4. Volver al menú principal")
    
    choice = input("Selección: ")
    
    if choice == "1":
        output_path = cli.output_dir / f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        cli.df.to_excel(output_path, index=False)
        print(f"✓ Datos exportados a: {output_path}")
    
    elif choice == "2":
        output_path = cli.output_dir / f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        cli.df.to_csv(output_path, index=False)
        print(f"✓ Datos exportados a: {output_path}")
    
    elif choice == "3":
        print("\nGenerando script SQL...")
        table_name = input("Nombre de la tabla: ")
        
        # Generar CREATE TABLE
        create_table = f"CREATE TABLE {table_name} (\n"
        for col in cli.df.columns:
            dtype = cli.df[col].dtype
            if dtype == 'int64':
                sql_type = 'INT'
            elif dtype == 'float64':
                sql_type = 'FLOAT'
            elif dtype == 'datetime64[ns]':
                sql_type = 'DATETIME'
            else:
                sql_type = 'VARCHAR(255)'
            create_table += f"    {col} {sql_type},\n"
        create_table = create_table.rstrip(",\n") + "\n);"
        
        # Guardar script
        output_path = cli.output_dir / f"create_table_{table_name}.sql"
        with open(output_path, 'w') as f:
            f.write(create_table)
        print(f"✓ Script SQL generado: {output_path}")

def main():
    global cli
    cli = ExcelCLI()
    
    while True:
        print_menu()
        choice = input("Selecciona una opción: ")

        if choice == "1":
            filepath = input("Ruta del archivo Excel: ")
            cli.load_file(filepath)
        elif choice == "2": analyze_data()
        elif choice == "3": generate_formulas()
        elif choice == "4": process_reports()
        elif choice == "5": export_results()
        elif choice == "6":
            print("¡Hasta pronto! ✨")
            break
        else:
            print("Opción inválida, intenta nuevamente")

        input("\nPresiona Enter para continuar...")
        os.system('cls' if os.name == 'nt' else 'clear')

if __name__ == "__main__":
    main()