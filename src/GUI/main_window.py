import sys
from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem, QVBoxLayout, QApplication, QMainWindow, QWidget, QHBoxLayout, QLabel, QFrame, QSplitter, QLineEdit
from PyQt6.QtGui import QPalette, QColor,QIcon
from PyQt6.QtCore import Qt
import sqlite3

from src.GUI.Widgets.MenuBar import MenuBar
from src.GUI.Widgets.seccion_2_function import IndividualConfigurationWidget
from src.GUI.Widgets.welcome_page import WelcomePage



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Unit Cost Kitchen")
        self.setGeometry(100, 100, 800, 600)
        self.setWindowIcon(QIcon('Kitchen_software/src/images/app_ico.ico'))  

        menu_bar = MenuBar(self)
        self.setMenuBar(menu_bar)
        main_splitter = QSplitter(Qt.Orientation.Horizontal)

        furniture_available = QFrame()
        furniture_available.setFrameShape(QFrame.Shape.StyledPanel)
        layout1 = QVBoxLayout(furniture_available)

        # Buscador
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Buscar mueble...")
        layout1.addWidget(self.search_box)
        self.search_box.textChanged.connect(self.filter_tree_by_model)
        # QTreeWidget para mostrar los muebles
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Modelo", "Descripción", "Precio"])
        layout1.addWidget(self.tree)

        self.tree.itemSelectionChanged.connect(self.update_section2_info)
        # Poblar el árbol con la base de datos
        self.populate_tree_from_db()

        # Sección 2
        individual_configuration = QFrame()
        individual_configuration.setFrameShape(QFrame.Shape.StyledPanel)
        layout2 = QVBoxLayout(individual_configuration)

        self.section2_label = QLabel("Configuracíon del mueble")
        layout2.addWidget(self.section2_label)


        layout2.addStretch() 
        # Sección 3
        used_furniture = QFrame()
        used_furniture.setFrameShape(QFrame.Shape.StyledPanel)
        layout3 = QHBoxLayout(used_furniture)
        layout3.addWidget(QLabel("Sección 3 (Redimensionable)"))

        # Añadir las secciones al splitter
        main_splitter.addWidget(furniture_available)
        main_splitter.addWidget(individual_configuration)
        main_splitter.addWidget(used_furniture)

        main_splitter.setCollapsible(0, False)
        main_splitter.setCollapsible(1, False)
        main_splitter.setCollapsible(2, False)

        self.setCentralWidget(main_splitter)

    def populate_tree_from_db(self):
        db_path = 'src/data/kitchen_main_db'
        try:
            conexion = sqlite3.connect(db_path)
            cursor = conexion.cursor()
            cursor.execute("SELECT DISTINCT Tipo FROM dbKitchen")
            tipos = [row[0] for row in cursor.fetchall()]

            self.tree.clear()
            for tipo in tipos:
                tipo_item = QTreeWidgetItem(self.tree)
                tipo_item.setText(0, tipo)
                cursor.execute("SELECT Modelo, Descripcion_Catalogo, Precio FROM dbKitchen WHERE Tipo = ?", (tipo,))
                modelos = cursor.fetchall()
                for modelo, descripcion, precio in modelos:
                    modelo_item = QTreeWidgetItem(tipo_item)
                    modelo_item.setText(0, str(modelo))
                    modelo_item.setText(1, str(descripcion))
                    modelo_item.setText(2, str(precio))
        except sqlite3.Error as error:
            print(f"Error con la base de datos: {error}")
        finally:
            if conexion:
                conexion.close()
    def filter_tree_by_model(self, text):
        text = text.lower()
        root = self.tree.invisibleRootItem()
        for i in range(root.childCount()):
            tipo_item = root.child(i)
            visible = False
            for j in range(tipo_item.childCount()):
                modelo_item = tipo_item.child(j)
                modelo = modelo_item.text(0).lower()
                match = text in modelo
                modelo_item.setHidden(not match)
                if match:
                    visible = True
            tipo_item.setHidden(not visible)

    def update_section2_info(self):
        selected = self.tree.selectedItems()
        if selected and selected[0].parent():  # Solo si es un mueble, no la categoría
            modelo = selected[0].text(0)
            descripcion = selected[0].text(1)
            precio = selected[0].text(2)

            # Consultar la base de datos para alto, ancho y fondo
            db_path = 'src/data/kitchen_main_db'
            try:
                conexion = sqlite3.connect(db_path)
                cursor = conexion.cursor()
                cursor.execute(
                    "SELECT Altura_Mueble_cm, Ancho_Mueble_LadoA_cm, Fondo_Mueble_cm FROM dbKitchen WHERE Modelo = ? LIMIT 1", (modelo,)
                )
                result = cursor.fetchone()
                if result:
                    Altura_Mueble_cm, Ancho_Mueble_LadoA_cm, Fondo_Mueble_cm = result
                else:
                    Altura_Mueble_cm = Ancho_Mueble_LadoA_cm = Fondo_Mueble_cm = "N/A"
            except sqlite3.Error as error:
                Altura_Mueble_cm = Ancho_Mueble_LadoA_cm = Fondo_Mueble_cm = "Error"
                print(f"Error con la base de datos: {error}")
            finally:
                if 'conexion' in locals():
                    conexion.close()

            self.section2_label.setText(
                f"<b>Modelo:</b> {modelo}<br>"
                f"<b>Descripción:</b> {descripcion}<br>"
                f"<b>Precio:</b> {precio}<br>"
                f"<b>Alto:</b> {Altura_Mueble_cm} <b>cm</b> &nbsp;&nbsp; <b>Ancho:</b> {Ancho_Mueble_LadoA_cm} <b>cm</b> &nbsp;&nbsp; <b>Fondo:</b> {Fondo_Mueble_cm} <b>cm</b>"
            )
        else:
            self.section2_label.setText("Configuración de muebles")  
def main_GUI_window():
    app = QApplication(sys.argv)
    welcome = WelcomePage()
    mainWin = None

    def open_main_window():
        nonlocal mainWin
        mainWin = MainWindow()
        mainWin.show()
        welcome.close()

    welcome.new_btn.clicked.connect(open_main_window)
    welcome.open_btn.clicked.connect(open_main_window)  # Aquí puedes poner lógica para abrir archivo

    welcome.show()
    sys.exit(app.exec())

