import csv
import sqlite3
import re
import os

def sanitize_name(name, is_table_name=False):
    """
    Clean a name to make it a valid SQL identifier.

        Replace spaces and non-alphanumeric characters with underscores.
        Ensure it doesn't start with a number.
        Avoid empty names.
    """
    if not isinstance(name, str):
        name = str(name)

    name = re.sub(r'[^\w]', '_', name)
    # Reemplazar múltiples guiones bajos con uno solo
    name = re.sub(r'_+', '_', name)
    name = name.strip('_')

    # Si el nombre es para una columna o tabla y comienza con un dígito, anteponer un guion bajo
    if name and name[0].isdigit():
        name = '_' + name
    
    # Si el nombre quedó vacío, usar un placeholder
    if not name:
        return 'columna_sin_nombre' if not is_table_name else 'tabla_sin_nombre'
    return name

def infer_column_type(values):
    """
    Determines the data type of a column (INTEGER, REAL, TEXT) from a sample of its values.
    """
    is_int = True
    is_real = True

    
    has_any_value = False
    for value in values:
        if value is None or value.strip() == '': 
            continue
        has_any_value = True 

        if is_int:
            try:
                int(value)
            except ValueError:
                is_int = False
        
        if is_real:
            try:
                float(value)
            except ValueError:
                is_real = False
        
        if not is_int and not is_real: 
            break 
            
    if not has_any_value: 
        return "TEXT" # Por defecto TEXT si no hay datos para inferir
        
    if is_int:
        return "INTEGER"
    if is_real:
        return "REAL"
    return "TEXT"

def create_sqlite_db_from_csv(csv_file_path, db_file_path, table_name):
    """
    Reads a CSV file and imports its data into an SQLite database table. Infers column types from the first 100 rows.
    """
    print(f"Procesando archivo CSV: {csv_file_path}")
    print(f"Base de datos SQLite a crear/actualizar: {db_file_path}")
    print(f"Nombre de la tabla: {table_name}")

    try:
        with open(csv_file_path, 'r', newline='', encoding='utf-8-sig') as csvfile:
            reader = csv.reader(csvfile)
            try:
                header = next(reader)
            except StopIteration:
                print("Error: El archivo CSV está vacío o no tiene encabezado.")
                return

            sanitized_headers = [sanitize_name(h) for h in header]
            if not any(sanitized_headers): #
                print("Error: Los encabezados del CSV no son válidos o están vacíos después de sanitizar.")
                return

    
            sample_data = []
            for i, row in enumerate(reader):
                if i < 100: # Usar hasta 100 filas para la muestra
                    if len(row) == len(sanitized_headers):
                        sample_data.append(row)
                   
                else:
                    break
            
            column_types = []
            if sample_data:
                for col_idx in range(len(sanitized_headers)):
                    values = [row[col_idx] for row in sample_data if len(row) > col_idx]
                    column_types.append(infer_column_type(values))
            else: 
                print("Advertencia: No se encontraron filas de datos para inferir tipos. Se usará TEXT para todas las columnas.")
                column_types = ["TEXT"] * len(sanitized_headers)

            # Conectar/Crear base de datos SQLite
            conn = sqlite3.connect(db_file_path)
            cursor = conn.cursor()

            safe_table_name = sanitize_name(table_name, is_table_name=True)

  
            # Crear tabla
            cols_with_types = [f'"{col_name}" {col_type}' for col_name, col_type in zip(sanitized_headers, column_types)]
            create_table_query = f"CREATE TABLE IF NOT EXISTS \"{safe_table_name}\" ({', '.join(cols_with_types)})"
            
            try:
                cursor.execute(create_table_query)
            except sqlite3.Error as e:
                print(f"Error al crear la tabla '{safe_table_name}': {e}")
                conn.close()
                return

            # Volver al inicio del archivo y saltar encabezado para insertar datos
            csvfile.seek(0)
            next(reader) 

            # Insertar datos
            placeholders = ", ".join(["?"] * len(sanitized_headers))
            insert_query = f"INSERT INTO \"{safe_table_name}\" ({', '.join(f'\"{h}\"' for h in sanitized_headers)}) VALUES ({placeholders})"
            
            rows_inserted = 0
            rows_skipped = 0
            for row_idx, row in enumerate(reader):
                if not any(field.strip() for field in row): 
                    rows_skipped +=1
                    continue
                
                if len(row) != len(sanitized_headers):
                    print(f"Advertencia: Fila {row_idx + 2} tiene {len(row)} columnas, se esperaban {len(sanitized_headers)}. Omitiendo fila: {row}")
                    rows_skipped +=1
                    continue

                processed_row = []
                for i, value in enumerate(row):
                    col_type = column_types[i]
                    original_value = value
                    value = value.strip() 
                    if value == '': # Tratar strings vacíos como NULL
                        processed_row.append(None)
                    elif col_type == "INTEGER":
                        try:
                            processed_row.append(int(value))
                        except ValueError:
                            print(f"Advertencia: No se pudo convertir '{original_value}' a INTEGER para la columna '{sanitized_headers[i]}' en la fila CSV {row_idx + 2}. Se insertará como NULL.")
                            processed_row.append(None)
                    elif col_type == "REAL":
                        try:
                            processed_row.append(float(value))
                        except ValueError:
                            print(f"Advertencia: No se pudo convertir '{original_value}' a REAL para la columna '{sanitized_headers[i]}' en la fila CSV {row_idx + 2}. Se insertará como NULL.")
                            processed_row.append(None)
                    else: # TEXT
                        processed_row.append(original_value) 
                
                try:
                    cursor.execute(insert_query, processed_row)
                    rows_inserted += 1
                except sqlite3.InterfaceError as e: # Error en datos pasados a execute
                    print(f"Error de interfaz SQLite insertando fila {row_idx + 2}: {row}. Error: {e}")
                    rows_skipped += 1
                except sqlite3.Error as e: # Otros errores de SQLite
                     print(f"Error de SQLite insertando fila {row_idx + 2} ({row}): {e}")
                     rows_skipped += 1

            conn.commit()
            conn.close()

            print(f"\n¡Proceso completado!")
            print(f"Base de datos SQLite '{db_file_path}' creada/actualizada con la tabla '{safe_table_name}'.")
            print(f"Se insertaron {rows_inserted} filas.")
            if rows_skipped > 0:
                print(f"Se omitieron {rows_skipped} filas debido a inconsistencias o errores de conversión.")
            
            print("\nEstructura de la tabla creada:")
            print(f"Nombre de la tabla: {safe_table_name}")
            for col_name, col_type in zip(sanitized_headers, column_types):
                print(f"  - Columna: \"{col_name}\", Tipo SQL inferido: {col_type}")

    except FileNotFoundError:
        print(f"Error: El archivo CSV '{csv_file_path}' no fue encontrado.")
    except Exception as e:
        print(f"Ocurrió un error inesperado durante el procesamiento: {e}")
        import traceback
        traceback.print_exc()

def generate_sql_statements_from_csv(csv_file_path, table_name):
    """
    Reads a CSV file and outputs SQL statements (CREATE TABLE and INSERT) to the console.
    """
    print(f"-- Generando sentencias SQL para el archivo CSV: {csv_file_path}")
    print(f"-- Nombre de la tabla SQL: {table_name}\n")

    try:
        with open(csv_file_path, 'r', newline='', encoding='utf-8-sig') as csvfile:
            reader = csv.reader(csvfile)
            try:
                header = next(reader)
            except StopIteration:
                print("-- Error: El archivo CSV está vacío o no tiene encabezado.")
                return

            sanitized_headers = [sanitize_name(h) for h in header]
            if not any(sanitized_headers):
                print("-- Error: Encabezados no válidos o vacíos después de sanitizar.")
                return

            sample_data = []
            for i, row in enumerate(reader):
                if i < 100:
                    if len(row) == len(sanitized_headers):
                        sample_data.append(row)
                else:
                    break
            
            column_types = []
            if sample_data:
                for col_idx in range(len(sanitized_headers)):
                    values = [row[col_idx] for row in sample_data if len(row) > col_idx]
                    column_types.append(infer_column_type(values))
            else:
                column_types = ["TEXT"] * len(sanitized_headers)

            # Volver al inicio y saltar encabezado
            csvfile.seek(0)
            next(reader)

            safe_table_name = sanitize_name(table_name, is_table_name=True)
            
            # Sentencia CREATE TABLE
            print(f"-- Sentencia CREATE TABLE para la tabla '{safe_table_name}':")
            create_table_sql = f"CREATE TABLE IF NOT EXISTS \"{safe_table_name}\" (\n"
            for i, col_name in enumerate(sanitized_headers):
                create_table_sql += f"  \"{col_name}\" {column_types[i]}"
                create_table_sql += ",\n" if i < len(sanitized_headers) - 1 else "\n"
            create_table_sql += ");\n"
            print(create_table_sql)

            # Sentencias INSERT
            print(f"-- Sentencias INSERT para la tabla '{safe_table_name}':")
            for row_idx, row in enumerate(reader):
                if not any(field.strip() for field in row):
                    continue # Omitir filas vacías
                if len(row) != len(sanitized_headers):
                    print(f"-- ADVERTENCIA: Omitiendo fila {row_idx+2} con número incorrecto de columnas: {row}")
                    continue

                values_sql_parts = []
                for i, value in enumerate(row):
                    original_value = value
                    value = value.strip() 

                    if value == '':
                        values_sql_parts.append("NULL")
                    elif column_types[i] == "INTEGER":
                        try:
                            int(value)
                            values_sql_parts.append(value) # Sin comillas para números
                        except ValueError:
                            values_sql_parts.append(f"'{original_value.replace("'", "''")}'") # O NULL
                    elif column_types[i] == "REAL":
                        try:
                            float(value) # Validar
                            values_sql_parts.append(value) # Sin comillas para números
                        except ValueError:
                            values_sql_parts.append(f"'{original_value.replace("'", "''")}'") # O NULL
                    else: # TEXT
                        values_sql_parts.append(f"'{original_value.replace("'", "''")}'") # Escapar comillas simples

                insert_sql = f"INSERT INTO \"{safe_table_name}\" ({', '.join(f'\"{h}\"' for h in sanitized_headers)}) VALUES ({', '.join(values_sql_parts)});"
                print(insert_sql)
        
        print(f"\n-- Generación de sentencias SQL completada.")
        print("-- Puedes copiar estas sentencias y ejecutarlas en tu cliente de base de datos SQL.")
        print("-- Nota: La sintaxis de tipos de datos (INTEGER, REAL, TEXT) es común, pero podría necesitar ajustes para SGBDs específicos.")

    except FileNotFoundError:
        print(f"-- Error: El archivo CSV '{csv_file_path}' no fue encontrado.")
    except Exception as e:
        print(f"-- Ocurrió un error inesperado: {e}")
        import traceback
        traceback.print_exc()

def sql_generator_main(csv_file, dbname):
    # Reemplaza con la ruta real a tu archivo CSV
    csv_file_path_actual = csv_file
    
    # Nombre para el archivo de base de datos SQLite (se creará si no existe)
    db_file_name = dbname
    
    # Puedes derivarlo del nombre del CSV o elegir uno específico
    csv_base_name = os.path.splitext(os.path.basename(csv_file_path_actual))[0]
    table_name_for_db = sanitize_name(csv_base_name if csv_base_name else "datos_kitchen", is_table_name=True)
    create_sqlite_db_from_csv(csv_file_path_actual, db_file_name, table_name_for_db)

if __name__ == "__main__":
    sql_generator_main("src/Data_Creator/db_doors.csv", "src/data/dbdoor" )