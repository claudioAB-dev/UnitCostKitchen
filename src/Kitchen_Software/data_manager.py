import sqlite3

def key_search(key):
    try:
        conexion = sqlite3.connect('src/data/kitchen_main_db')
        cursor = conexion.cursor()

        cursor.execute("SELECT * FROM dbKitchen WHERE Modelo = ?", (key,))        
        resultados = cursor.fetchall()
        for fila in resultados:
            print(fila)

    except sqlite3.Error as error:
        print(f"Error con la base de datos: {error}")

    finally:
        if conexion:
            conexion.close()    

def kind_search(kind):
    try:
        conexion = sqlite3.connect('src/data/kitchen_main_db')
        cursor = conexion.cursor()

        cursor.execute("SELECT * FROM dbKitchen WHERE Tipo = ?", (kind,))
        resultados = cursor.fetchall()
        for fila in resultados:
            print(fila)
    except sqlite3.Error as error:
        print(f"Error con la base de datos: {error}")

    finally:
        if conexion:
            conexion.close()    


