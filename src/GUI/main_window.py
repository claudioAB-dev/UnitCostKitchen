import sys
from PyQt6.QtWidgets import QPushButton, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QApplication, QMainWindow, QWidget, QHBoxLayout, QLabel, QFrame, QSplitter, QLineEdit
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

        self.section2_label = QLabel("Configuración del mueble")
        self.section2_label.setTextFormat(Qt.TextFormat.RichText)
        layout2.addWidget(self.section2_label)

        self.section2_doors_label = QLabel("")
        self.section2_doors_label.setTextFormat(Qt.TextFormat.RichText)
        layout2.addWidget(self.section2_doors_label)
        self.door_search_box = QLineEdit()
        self.door_search_box.setPlaceholderText("Buscar puerta...")
        layout2.addWidget(self.door_search_box)

        self.door_tree = QTreeWidget()
        self.door_tree.setHeaderLabels(["Modelo Puerta", "Color", "Precio Marco", "Precio Frente", "Precio Mullion"])
        layout2.addWidget(self.door_tree)

        self.door_search_box.textChanged.connect(self.populate_door_tree)
        self.selected_door1_label = QLabel("Puerta seleccionada T1: Ninguna")
        layout2.addWidget(self.selected_door1_label)

        self.selected_door2_label = QLabel("Puerta seleccionada T2: Ninguna")
        layout2.addWidget(self.selected_door2_label)
        self.selected_door2_label.hide()  # Oculta por defecto
        self.door_tree.itemSelectionChanged.connect(self.update_selected_doors)
        self.add_button = QPushButton("Agregar")
        layout2.addWidget(self.add_button)


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
        if selected and selected[0].parent():
            modelo = selected[0].text(0)
            descripcion = selected[0].text(1)
            precio = selected[0].text(2)
            db_path = 'src/data/kitchen_main_db'
            try:
                conexion = sqlite3.connect(db_path)
                cursor = conexion.cursor()
                cursor.execute(
                    """SELECT Ancho_Mueble_LadoA_cm, Altura_Mueble_cm, Fondo_Mueble_cm,
                            Num_Puertas_T1, Ancho_Puerta_T1_cm, Alto_Puerta_T1_cm,
                            Num_Puertas_T2, Ancho_Puerta_T2_cm, Alto_Puerta_T2_cm,
                            Num_Cajones_T1, Ancho_Frente_Cajon_T1_cm, Alto_Frente_Cajon_T1_cm,
                            Num_Cajones_T2, Ancho_Frente_Cajon_T2_cm, Alto_Frente_Cajon_T2_cm,
                            Observaciones_Mueble
                    FROM dbKitchen WHERE Modelo = ? LIMIT 1""", (modelo,)
                )
                result = cursor.fetchone()
                if result:
                    (ancho, alto, fondo,
                    num_puertas_t1, ancho_puerta_t1, alto_puerta_t1,
                    num_puertas_t2, ancho_puerta_t2, alto_puerta_t2,
                    num_cajones_t1, ancho_cajon_t1, alto_cajon_t1,
                    num_cajones_t2, ancho_cajon_t2, alto_cajon_t2,
                    observaciones) = result
                else:
                    (ancho, alto, fondo,
                    num_puertas_t1, ancho_puerta_t1, alto_puerta_t1,
                    num_puertas_t2, ancho_puerta_t2, alto_puerta_t2,
                    num_cajones_t1, ancho_cajon_t1, alto_cajon_t1,
                    num_cajones_t2, ancho_cajon_t2, alto_cajon_t2,
                    observaciones) = ("N/A",)*16
            except sqlite3.Error as error:
                (ancho, alto, fondo,
                num_puertas_t1, ancho_puerta_t1, alto_puerta_t1,
                num_puertas_t2, ancho_puerta_t2, alto_puerta_t2,
                num_cajones_t1, ancho_cajon_t1, alto_cajon_t1,
                num_cajones_t2, ancho_cajon_t2, alto_cajon_t2,
                observaciones) = ("Error",)*16
                print(f"Error con la base de datos: {error}")
            finally:
                if 'conexion' in locals():
                    conexion.close()
            puertas_info = ""
            self.num_puertas_t2 = num_puertas_t2
            if num_puertas_t1 and str(num_puertas_t1).isdigit() and int(num_puertas_t1) > 0:
                puertas_info += f"<b>Puertas T1:</b> {num_puertas_t1} ({ancho_puerta_t1}x{alto_puerta_t1} cm)<br>"
            if num_puertas_t2 and str(num_puertas_t2).isdigit() and int(num_puertas_t2) > 0:
                puertas_info += f"<b>Puertas T2:</b> {num_puertas_t2} ({ancho_puerta_t2}x{alto_puerta_t2} cm)<br>"
            if num_cajones_t1 and str(num_cajones_t1).isdigit() and int(num_cajones_t1) > 0:
                puertas_info += f"<b>Cajones T1:</b> {num_cajones_t1} ({ancho_cajon_t1}x{alto_cajon_t1} cm)<br>"
            if num_cajones_t2 and str(num_cajones_t2).isdigit() and int(num_cajones_t2) > 0:
                puertas_info += f"<b>Cajones T2:</b> {num_cajones_t2} ({ancho_cajon_t2}x{alto_cajon_t2} cm)<br>"
            if not puertas_info:
                puertas_info = "Este mueble no lleva puertas ni cajones.<br>"
            if observaciones and observaciones != "NULL":
                puertas_info += f"<b>Observaciones:</b> {observaciones}<br>"
            self.section2_label.setText(
                f"<b>Modelo:</b> {modelo}<br>"
                f"<b>Descripción:</b> {descripcion}<br>"
                f"<b>Precio:</b> {precio}<br>"
                f"<b>Medidas:</b> {ancho} x {alto} x {fondo} cm"
            )
            self.section2_doors_label.setText(puertas_info)
            self.populate_door_tree()
        else:
            self.section2_label.setText("Configuración de muebles")
            self.section2_doors_label.setText("")
            self.door_tree.clear()
            self.selected_door1_label.setText("Puerta seleccionada T1: Ninguna")
            self.selected_door2_label.setText("Puerta seleccionada T2: Ninguna")
            self.selected_door2_label.hide()


    def populate_door_tree(self, search_text=""):
        self.door_tree.clear()
        db_path = 'src/data/dbdoor'
        try:
            conexion = sqlite3.connect(db_path)
            cursor = conexion.cursor()
            # Obtener tipos únicos de puerta
            cursor.execute("SELECT DISTINCT Linea FROM db_doors")
            tipos = [row[0] for row in cursor.fetchall()]
            for tipo in tipos:
                tipo_item = QTreeWidgetItem(self.door_tree)
                tipo_item.setText(0, tipo)
                # Buscar por texto si hay filtro
                if search_text:
                    cursor.execute(
                        """SELECT Modelo_Puerta, Color_Puerta, Precio_M2_Marco, Precio_M2_Puerta_Frente, Precio_M2_Mullion
                        FROM db_doors WHERE Linea = ? AND Modelo_Puerta LIKE ?""",
                        (tipo, f"%{search_text}%")
                    )
                else:
                    cursor.execute(
                        """SELECT Modelo_Puerta, Color_Puerta, Precio_M2_Marco, Precio_M2_Puerta_Frente, Precio_M2_Mullion
                        FROM db_doors WHERE Linea = ?""",
                        (tipo,)
                    )
                puertas = cursor.fetchall()
                for modelo_puerta, color, precio_marco, precio_frente, precio_mullion in puertas:
                    puerta_item = QTreeWidgetItem(tipo_item)
                    puerta_item.setText(0, modelo_puerta)
                    puerta_item.setText(1, color)
                    puerta_item.setText(2, str(precio_marco))
                    puerta_item.setText(3, str(precio_frente))
                    puerta_item.setText(4, str(precio_mullion))
        except sqlite3.Error as error:
            print(f"Error con la base de datos de puertas: {error}")
        finally:
            if 'conexion' in locals():
                conexion.close()


    def update_selected_doors(self):
        selected_items = self.door_tree.selectedItems()
        num_puertas_t2 = 0
        if not selected_items:
            self.selected_door1_label.setText("Puerta seleccionada T1: Ninguna")
            self.selected_door2_label.setText("Puerta seleccionada T2: Ninguna")
            self.selected_door2_label.hide()
            return

        # Si hay dos tipos de puerta, permite seleccionar dos
        if hasattr(self, 'num_puertas_t2') and self.num_puertas_t2 and str(self.num_puertas_t2).isdigit() and int(self.num_puertas_t2) > 0:
            self.selected_door2_label.show()
            if len(selected_items) >= 2:
                door1 = selected_items[0]
                door2 = selected_items[1]
                self.selected_door1_label.setText(f"Puerta seleccionada T1: {door1.text(0)} | Precio Marco: {door1.text(2)}")
                self.selected_door2_label.setText(f"Puerta seleccionada T2: {door2.text(0)} | Precio Marco: {door2.text(2)}")
            elif len(selected_items) == 1:
                door1 = selected_items[0]
                self.selected_door1_label.setText(f"Puerta seleccionada T1: {door1.text(0)} | Precio Marco: {door1.text(2)}")
                self.selected_door2_label.setText("Puerta seleccionada T2: Ninguna")
            else:
                self.selected_door1_label.setText("Puerta seleccionada T1: Ninguna")
                self.selected_door2_label.setText("Puerta seleccionada T2: Ninguna")
        else:
            self.selected_door2_label.hide()
            door = selected_items[0]
            self.selected_door1_label.setText(f"Puerta seleccionada: {door.text(0)} | Precio Marco: {door.text(2)}")


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

