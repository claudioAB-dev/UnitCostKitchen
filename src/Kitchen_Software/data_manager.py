import sqlite3



def Key_Search(key):
    try:
        conexion = sqlite3.connect('data/Catalogo1')
        cursor = conexion.cursor()

        cursor.execute(f"SELECT * FROM Catalogo WHERE CLAVE =  {key}")
        resultados = cursor.fetchall()
        for fila in resultados:
            print(fila)

    except sqlite3.Error as error:
        print(f"Error con la base de datos: {error}")

    finally:
        if conexion:
            conexion.close()    


Key_Search("AE57")