import sys
import os # Necesario para trabajar con nombres de archivo
import json # Necesario para guardar y cargar datos del proyecto
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QFrame, QSplitter, QLineEdit, QPushButton, 
                             QTreeWidget, QTreeWidgetItem, QMessageBox, QFileDialog) # Agregados QMessageBox y QFileDialog
from PyQt6.QtGui import QPalette, QColor, QIcon, QCloseEvent # Agregado QCloseEvent
from PyQt6.QtCore import Qt, pyqtSignal # Agregado pyqtSignal si fuera necesario para comunicación más compleja
import sqlite3

from src.GUI.Widgets.MenuBar import MenuBar
# from src.GUI.Widgets.seccion_2_function import IndividualConfigurationWidget # No se usa directamente en este ejemplo
from src.GUI.Widgets.welcome_page import WelcomePage


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Estado del proyecto
        self.current_project_path = None
        self.project_modified = False
        self.base_title = "Unit Cost Kitchen"

        self.setWindowTitle(self.base_title + " - Nuevo Proyecto") # Título inicial
        self.setGeometry(100, 100, 1000, 700) # Ajustado para más espacio
        # Asegúrate que la ruta al ícono sea correcta o remueve la línea si no existe
        # self.setWindowIcon(QIcon('Kitchen_software/src/images/app_ico.ico'))  
        try:
            # Intenta cargar el ícono desde una ruta relativa al script de main_window.py
            # Esto asume que images/app_ico.ico existe en src/GUI/images/app_ico.ico
            icon_path = os.path.join(os.path.dirname(__file__), 'images', 'app_ico.ico')
            if os.path.exists(icon_path):
                self.setWindowIcon(QIcon(icon_path))
            else:
                # Fallback si no se encuentra, o puedes simplemente omitir el ícono
                print(f"Advertencia: Ícono no encontrado en {icon_path}")
        except Exception as e:
            print(f"Error al cargar ícono: {e}")


        menu_bar = MenuBar(self)
        self.setMenuBar(menu_bar)
        
        main_splitter = QSplitter(Qt.Orientation.Horizontal)

        # Sección 1: Muebles disponibles
        furniture_available = QFrame()
        furniture_available.setFrameShape(QFrame.Shape.StyledPanel)
        layout1 = QVBoxLayout(furniture_available)
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Buscar mueble...")
        layout1.addWidget(self.search_box)
        self.search_box.textChanged.connect(self.filter_tree_by_model)
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Modelo", "Descripción", "Precio"])
        layout1.addWidget(self.tree)
        self.tree.itemSelectionChanged.connect(self.update_section2_info)
        self.populate_tree_from_db()

        # Sección 2: Configuración individual del mueble
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
        self.door_tree.setSelectionMode(QTreeWidget.SelectionMode.SingleSelection)
        layout2.addWidget(self.door_tree)
        self.door_search_box.textChanged.connect(self.populate_door_tree)
        self.selected_door1_label = QLabel("Puerta seleccionada T1: Ninguna")
        layout2.addWidget(self.selected_door1_label)
        self.add_t1_button = QPushButton("Agregar T1")
        layout2.addWidget(self.add_t1_button)
        self.delete_t1_button = QPushButton("Eliminar T1")
        layout2.addWidget(self.delete_t1_button)
        self.selected_door2_label = QLabel("Puerta seleccionada T2: Ninguna")
        layout2.addWidget(self.selected_door2_label)
        self.selected_door2_label.hide()
        self.add_t2_button = QPushButton("Agregar T2")
        layout2.addWidget(self.add_t2_button)
        self.add_t2_button.hide()
        self.delete_t2_button = QPushButton("Eliminar T2")
        layout2.addWidget(self.delete_t2_button)
        self.delete_t2_button.hide()
        self.add_t1_button.clicked.connect(self.assign_t1_door)
        self.delete_t1_button.clicked.connect(self.delete_t1_door)
        self.add_t2_button.clicked.connect(self.assign_t2_door)
        self.delete_t2_button.clicked.connect(self.delete_t2_door)
        self.select_furniture_button = QPushButton("Agregar mueble al proyecto") # Texto más claro
        layout2.addWidget(self.select_furniture_button)
        self.select_furniture_button.clicked.connect(self.add_selected_furniture_to_list)
        layout2.addStretch()

        # Sección 3: Muebles usados en el proyecto
        used_furniture = QFrame()
        used_furniture.setFrameShape(QFrame.Shape.StyledPanel)
        layout3 = QVBoxLayout(used_furniture)
        layout3.addWidget(QLabel("Muebles en el Proyecto Actual")) # Título más claro
        self.selected_furniture = []  
        self.selected_furniture_list = QTreeWidget()
        self.selected_furniture_list.setHeaderLabels(["Modelo", "Puerta T1", "Puerta T2", "Precio Total"])
        layout3.addWidget(self.selected_furniture_list)        
        # layout3.setStretch(1, 1) # Puede no ser necesario o deseado
        self.delete_selected_furniture_button = QPushButton("Eliminar mueble del proyecto") # Texto más claro
        layout3.addWidget(self.delete_selected_furniture_button)
        self.delete_selected_furniture_button.clicked.connect(self.delete_selected_furniture)

        main_splitter.addWidget(furniture_available)
        main_splitter.addWidget(individual_configuration)
        main_splitter.addWidget(used_furniture)
        main_splitter.setSizes([250, 350, 400]) # Tamaños iniciales de las secciones
        main_splitter.setCollapsible(0, False)
        main_splitter.setCollapsible(1, False)
        main_splitter.setCollapsible(2, False)
        self.setCentralWidget(main_splitter)

        self._clear_project_state() # Asegura estado inicial limpio
        self.set_project_modified(False) # Actualiza título y estado
        self.selected_t1_door = None # Inicializar explícitamente
        self.selected_t2_door = None # Inicializar explícitamente

    def set_project_modified(self, modified):
        if self.project_modified == modified:
            return
        self.project_modified = modified
        self.update_window_title()

    def update_window_title(self):
        title = self.base_title
        if self.current_project_path:
            title += f" - {os.path.basename(self.current_project_path)}"
        else:
            title += " - Nuevo Proyecto"
        if self.project_modified:
            title += "*"
        self.setWindowTitle(title)

    def _clear_project_state(self):
        """Limpia el estado del proyecto actual y la UI relacionada."""
        self.selected_furniture.clear()
        self.selected_furniture_list.clear()
        
        self.section2_label.setText("Configuración del mueble")
        self.section2_doors_label.setText("")
        self.door_tree.clear() # Limpiar árbol de puertas también
        self.selected_door1_label.setText("Puerta seleccionada T1: Ninguna")
        self.selected_door2_label.setText("Puerta seleccionada T2: Ninguna")
        self.selected_door2_label.hide()
        self.add_t2_button.hide()
        self.delete_t2_button.hide()
        
        self.selected_t1_door = None
        self.selected_t2_door = None
        
        # Deseleccionar cualquier item en el árbol de muebles
        self.tree.clearSelection()
        # También podrías querer limpiar los campos de búsqueda
        self.search_box.clear()
        self.door_search_box.clear()

    def on_new_project_action(self):
        if self.project_modified: # Solo preguntar si hay cambios
            if not self.check_unsaved_changes():
                return False # El usuario canceló
        
        self._clear_project_state()
        self.current_project_path = None
        self.set_project_modified(False) # Esto actualiza el título
        # self.update_window_title() # Ya se llama en set_project_modified
        return True

    def on_open_project_action(self):
        if self.project_modified: # Solo preguntar si hay cambios
            if not self.check_unsaved_changes():
                return False # El usuario canceló

        # Rutas relativas para bases de datos (ejemplo, ajustar según tu estructura)
        # Asumiendo que los proyectos se guardan en una carpeta 'projects' a nivel del directorio raíz del repo
        # projects_dir = os.path.join(os.path.dirname(sys.argv[0]), '..', 'projects') # Navega un nivel arriba desde src/GUI
        # if not os.path.exists(projects_dir):
        #    os.makedirs(projects_dir)
        # initial_dir = projects_dir

        # O un directorio más genérico como el home del usuario o el último usado
        initial_dir = self.current_project_path if self.current_project_path else os.path.expanduser("~")


        filePath, _ = QFileDialog.getOpenFileName(self, "Abrir Proyecto", initial_dir, 
                                                  "Archivos de Proyecto (*.json);;Todos los Archivos (*)")
        if not filePath:
            return False # El usuario canceló

        try:
            with open(filePath, 'r', encoding='utf-8') as f:
                loaded_data = json.load(f)
            
            self._clear_project_state() # Limpiar antes de cargar
            
            # Validar que loaded_data es una lista (formato esperado)
            if not isinstance(loaded_data, list):
                raise ValueError("El archivo de proyecto no tiene el formato esperado (debe ser una lista).")

            self.selected_furniture = loaded_data
            
            self.selected_furniture_list.clear()
            for item_data in self.selected_furniture:
                # Asegurarse que item_data es un diccionario
                if not isinstance(item_data, dict):
                    print(f"Advertencia: Elemento en proyecto no es un diccionario: {item_data}")
                    continue

                item_widget = QTreeWidgetItem([
                    item_data.get("modelo", "N/A"),
                    item_data.get("puerta_t1", "N/A"),
                    item_data.get("puerta_t2", "N/A"),
                    f"{item_data.get('precio_total', 0.0):.2f}"
                ])
                self.selected_furniture_list.addTopLevelItem(item_widget)
            
            self.current_project_path = filePath
            self.set_project_modified(False)
            return True
        except Exception as e:
            QMessageBox.critical(self, "Error al Abrir", f"No se pudo abrir el archivo del proyecto:\n{e}")
            self.on_new_project_action() # Volver a un estado limpio si falla la carga
            return False

    def _save_data_to_file(self, filePath):
        try:
            with open(filePath, 'w', encoding='utf-8') as f:
                json.dump(self.selected_furniture, f, indent=4, ensure_ascii=False)
            self.set_project_modified(False) # Marcar como no modificado después de guardar
            # self.update_window_title() # Ya se llama en set_project_modified
            QMessageBox.information(self, "Guardado", f"Proyecto guardado en:\n{filePath}")
            return True
        except Exception as e:
            QMessageBox.critical(self, "Error al Guardar", f"No se pudo guardar el archivo del proyecto:\n{e}")
            return False

    def on_save_project_action(self):
        if not self.current_project_path:
            return self.on_save_project_as_action()
        else:
            return self._save_data_to_file(self.current_project_path)

    def on_save_project_as_action(self):
        # initial_dir = os.path.dirname(self.current_project_path) if self.current_project_path else os.path.expanduser("~")
        # default_filename = os.path.basename(self.current_project_path) if self.current_project_path else "nuevo_proyecto.json"
        # full_initial_path = os.path.join(initial_dir, default_filename)

        # Simplificado:
        initial_path = self.current_project_path if self.current_project_path else os.path.join(os.path.expanduser("~"), "proyecto_cocina.json")

        filePath, _ = QFileDialog.getSaveFileName(self, "Guardar Proyecto Como...", initial_path,
                                                  "Archivos de Proyecto (*.json);;Todos los Archivos (*)")
        if not filePath:
            return False # El usuario canceló
        
        # Asegurar la extensión .json
        if not filePath.lower().endswith(".json"):
            filePath += ".json"
            
        self.current_project_path = filePath # Actualizar la ruta actual
        return self._save_data_to_file(filePath)

    def check_unsaved_changes(self):
        """Pregunta al usuario si desea guardar cambios si el proyecto ha sido modificado."""
        if not self.project_modified:
            return True # No hay cambios, continuar

        reply = QMessageBox.question(self, 'Guardar Cambios',
                                     "El proyecto actual tiene cambios sin guardar.\n¿Desea guardar los cambios?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel)

        if reply == QMessageBox.StandardButton.Yes:
            return self.on_save_project_action() # Guardar; devuelve True si tiene éxito, False si falla/cancela
        elif reply == QMessageBox.StandardButton.No:
            return True # Continuar sin guardar
        else: # Cancel
            return False # No continuar con la acción original

    def closeEvent(self, event: QCloseEvent): # Especificar tipo del evento
        """Maneja el evento de cierre de la ventana."""
        if self.check_unsaved_changes():
            event.accept() # Permitir cierre
        else:
            event.ignore() # Cancelar cierre

    def populate_tree_from_db(self):
        # Ruta corregida asumiendo que 'data' está en 'src'
        db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'kitchen_main_db') #
        if not os.path.exists(db_path):
            QMessageBox.critical(self, "Error de Base de Datos", f"La base de datos principal no se encontró en: {db_path}")
            return
        try:
            conexion = sqlite3.connect(db_path)
            cursor = conexion.cursor()
            # ... (resto del código sin cambios)
            cursor.execute("SELECT DISTINCT Tipo FROM dbKitchen") #
            tipos = [row[0] for row in cursor.fetchall()]
            self.tree.clear()
            for tipo in tipos:
                tipo_item = QTreeWidgetItem(self.tree)
                tipo_item.setText(0, tipo)
                cursor.execute("SELECT Modelo, Descripcion_Catalogo, Precio FROM dbKitchen WHERE Tipo = ?", (tipo,)) #
                modelos = cursor.fetchall()
                for modelo, descripcion, precio in modelos:
                    modelo_item = QTreeWidgetItem(tipo_item)
                    modelo_item.setText(0, str(modelo))
                    modelo_item.setText(1, str(descripcion))
                    modelo_item.setText(2, str(precio))
        except sqlite3.Error as error:
            print(f"Error con la base de datos: {error}")
            QMessageBox.warning(self, "Error de Base de Datos", f"No se pudo leer la base de datos de muebles: {error}")
        finally:
            if 'conexion' in locals() and conexion:
                conexion.close()

    def filter_tree_by_model(self, text): #
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

    def update_section2_info(self): #
        selected = self.tree.selectedItems()
        if selected and selected[0].parent(): # Asegura que es un item de mueble, no de tipo
            modelo = selected[0].text(0)
            descripcion = selected[0].text(1)
            precio = selected[0].text(2)
            db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'kitchen_main_db') #
            
            # Resetear selección de puertas al cambiar de mueble
            self.selected_t1_door = None
            self.selected_t2_door = None
            self.selected_door1_label.setText("Puerta seleccionada T1: Ninguna")
            self.selected_door2_label.setText("Puerta seleccionada T2: Ninguna")
            self.door_tree.clearSelection() # Deseleccionar en el árbol de puertas
            self.populate_door_tree() # Repoblar (y filtrar si hay texto en door_search_box)

            try:
                conexion = sqlite3.connect(db_path)
                cursor = conexion.cursor()
                # ... (query y obtención de datos sin cambios)
                cursor.execute(
                    """SELECT Ancho_Mueble_LadoA_cm, Altura_Mueble_cm, Fondo_Mueble_cm,
                            Num_Puertas_T1, Ancho_Puerta_T1_cm, Alto_Puerta_T1_cm,
                            Num_Puertas_T2, Ancho_Puerta_T2_cm, Alto_Puerta_T2_cm,
                            Num_Cajones_T1, Ancho_Frente_Cajon_T1_cm, Alto_Frente_Cajon_T1_cm,
                            Num_Cajones_T2, Ancho_Frente_Cajon_T2_cm, Alto_Frente_Cajon_T2_cm,
                            Observaciones_Mueble
                    FROM dbKitchen WHERE Modelo = ? LIMIT 1""", (modelo,) #
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
                    observaciones) = ("N/A",)*16 #
                self.section2_label.setText(
                    f"<b>Modelo:</b> {modelo}<br>"
                    f"<b>Descripción:</b> {descripcion}<br>"
                    f"<b>Precio:</b> {precio}<br>"
                    f"<b>Medidas:</b> {ancho} x {alto} x {fondo} cm"
                )
            except sqlite3.Error as error:
                (ancho, alto, fondo,
                num_puertas_t1, ancho_puerta_t1, alto_puerta_t1,
                num_puertas_t2, ancho_puerta_t2, alto_puerta_t2,
                num_cajones_t1, ancho_cajon_t1, alto_cajon_t1,
                num_cajones_t2, ancho_cajon_t2, alto_cajon_t2,
                observaciones) = ("Error",)*16 #
                print(f"Error con la base de datos: {error}")
            finally:
                if 'conexion' in locals() and conexion:
                    conexion.close()
            
            self.num_puertas_t2_actual = num_puertas_t2 # Guardar para referencia
            if num_puertas_t2 and str(num_puertas_t2).isdigit() and int(num_puertas_t2) > 0: #
                self.selected_door2_label.setVisible(True)
                self.add_t2_button.setVisible(True)
                self.delete_t2_button.setVisible(True)
            else:
                self.selected_door2_label.setVisible(False)
                self.add_t2_button.setVisible(False)
                self.delete_t2_button.setVisible(False)
            
            # ... (resto de la construcción de puertas_info y section2_label.setText sin cambios)
            puertas_info = ""
            if num_puertas_t1 and str(num_puertas_t1).isdigit() and int(num_puertas_t1) > 0: #
                puertas_info += f"<b>Puertas T1:</b> {num_puertas_t1} ({ancho_puerta_t1}x{alto_puerta_t1} cm)<br>"
            if num_puertas_t2 and str(num_puertas_t2).isdigit() and int(num_puertas_t2) > 0: #
                puertas_info += f"<b>Puertas T2:</b> {num_puertas_t2} ({ancho_puerta_t2}x{alto_puerta_t2} cm)<br>"
            # ... (cajones)

            self.section2_doors_label.setText(puertas_info) #


        else: # Nada seleccionado o un item de tipo
            self._clear_project_state() # Reutilizar para limpiar sección 2
            # self.section2_label.setText("Configuración de muebles") #
            # self.section2_doors_label.setText("") #
            # self.door_tree.clear() #
            # self.selected_door1_label.setText("Puerta seleccionada T1: Ninguna") #
            # self.selected_door2_label.setText("Puerta seleccionada T2: Ninguna") #
            # self.selected_door2_label.hide() #
            # self.selected_t1_door = None #
            # self.selected_t2_door = None #
            # self.add_t2_button.hide() #
            # self.delete_t2_button.hide() #

    def populate_door_tree(self, search_text=""): #
        self.door_tree.clear()
        db_path_doors = os.path.join(os.path.dirname(__file__), '..', 'data', 'dbdoor') #
        if not os.path.exists(db_path_doors):
            QMessageBox.warning(self, "Advertencia", f"La base de datos de puertas no se encontró en: {db_path_doors}")
            return
        try:
            conexion = sqlite3.connect(db_path_doors)
            cursor = conexion.cursor()
            # ... (resto del código de populate_door_tree sin cambios)
            cursor.execute("SELECT DISTINCT Linea FROM db_doors") #
            tipos = [row[0] for row in cursor.fetchall()]
            for tipo in tipos:
                tipo_item = QTreeWidgetItem(self.door_tree)
                tipo_item.setText(0, tipo)
                query = """SELECT Modelo_Puerta, Color_Puerta, Precio_M2_Marco, Precio_M2_Puerta_Frente, Precio_M2_Mullion
                           FROM db_doors WHERE Linea = ?""" #
                params = [tipo]
                if search_text: #
                    query += " AND (Modelo_Puerta LIKE ? OR Color_Puerta LIKE ?)"
                    params.extend([f"%{search_text}%", f"%{search_text}%"])
                
                cursor.execute(query, tuple(params))
                puertas = cursor.fetchall()
                # ...
                for modelo_puerta, color, precio_marco, precio_frente, precio_mullion in puertas:
                    puerta_item = QTreeWidgetItem(tipo_item)
                    puerta_item.setText(0, modelo_puerta)
                    puerta_item.setText(1, color)
                    puerta_item.setText(2, str(precio_marco))
                    puerta_item.setText(3, str(precio_frente)) #
                    puerta_item.setText(4, str(precio_mullion)) #

        except sqlite3.Error as error:
            print(f"Error con la base de datos de puertas: {error}")
            QMessageBox.warning(self, "Error de Base de Datos", f"No se pudo leer la base de datos de puertas: {error}")
        finally:
            if 'conexion' in locals() and conexion:
                conexion.close()

    def assign_t1_door(self): #
        selected_items = self.door_tree.selectedItems()
        if selected_items and selected_items[0].parent(): # Asegurarse que es una puerta, no una línea
            door = selected_items[0]
            self.selected_t1_door = door # Guardar el QTreeWidgetItem completo
            self.selected_door1_label.setText(f"Puerta T1: {door.text(0)} ({door.text(1)}) | Marco: {door.text(2)}")
            self.set_project_modified(True) # Modificación potencial si se añade al proyecto
        else:
            QMessageBox.information(self, "Selección", "Por favor, seleccione un modelo de puerta específico.")

    def delete_t1_door(self): #
        self.selected_t1_door = None
        self.selected_door1_label.setText("Puerta seleccionada T1: Ninguna")
        self.set_project_modified(True)

    def assign_t2_door(self): #
        selected_items = self.door_tree.selectedItems()
        if selected_items and selected_items[0].parent():
            door = selected_items[0]
            self.selected_t2_door = door
            self.selected_door2_label.setText(f"Puerta T2: {door.text(0)} ({door.text(1)}) | Marco: {door.text(2)}")
            self.set_project_modified(True)
        else:
            QMessageBox.information(self, "Selección", "Por favor, seleccione un modelo de puerta específico.")

    def delete_t2_door(self): #
        self.selected_t2_door = None
        self.selected_door2_label.setText("Puerta seleccionada T2: Ninguna")
        self.set_project_modified(True)

    def add_selected_furniture_to_list(self): #
        selected_furniture_items = self.tree.selectedItems()
        if not selected_furniture_items or not selected_furniture_items[0].parent():
            QMessageBox.warning(self, "Selección Requerida", "Por favor, seleccione un modelo de mueble de la lista.")
            return

        modelo = selected_furniture_items[0].text(0)
        precio_mueble_str = selected_furniture_items[0].text(2)

        # Obtener detalles de las puertas seleccionadas
        puerta_t1_modelo = "Ninguna"
        puerta_t1_precio_marco = 0.0
        if self.selected_t1_door:
            puerta_t1_modelo = f"{self.selected_t1_door.text(0)} ({self.selected_t1_door.text(1)})"
            try:
                # Asumir que el precio del marco es el relevante aquí o ajustar lógica
                precio_str = str(self.selected_t1_door.text(2)).replace(",", "") # Limpiar comas
                puerta_t1_precio_marco = float(precio_str if precio_str and precio_str != "ND" else 0.0)
            except ValueError:
                puerta_t1_precio_marco = 0.0
                print(f"Advertencia: Precio de marco T1 no válido: {self.selected_t1_door.text(2)}")


        puerta_t2_modelo = "Ninguna"
        puerta_t2_precio_marco = 0.0
        # Verificar si el mueble usa puertas T2 (basado en num_puertas_t2_actual obtenido en update_section2_info)
        # y si se ha seleccionado una puerta T2
        if (hasattr(self, 'num_puertas_t2_actual') and self.num_puertas_t2_actual and 
            str(self.num_puertas_t2_actual).isdigit() and int(self.num_puertas_t2_actual) > 0 and 
            self.selected_t2_door):
            puerta_t2_modelo = f"{self.selected_t2_door.text(0)} ({self.selected_t2_door.text(1)})"
            try:
                precio_str = str(self.selected_t2_door.text(2)).replace(",", "")
                puerta_t2_precio_marco = float(precio_str if precio_str and precio_str != "ND" else 0.0)
            except ValueError:
                puerta_t2_precio_marco = 0.0
                print(f"Advertencia: Precio de marco T2 no válido: {self.selected_t2_door.text(2)}")


        try:
            precio_mueble = float(str(precio_mueble_str).replace(",", ""))
        except ValueError:
            precio_mueble = 0.0
            QMessageBox.critical(self, "Error de Precio", f"El precio base del mueble '{modelo}' no es válido: {precio_mueble_str}")
            return
        
        # Aquí necesitarás una lógica más compleja para calcular el precio total
        # basado en las dimensiones de las puertas del mueble y el Precio_M2 de las puertas seleccionadas.
        # Por ahora, sumamos el precio base del mueble y el precio de marco (si aplica).
        # Este cálculo es una SIMPLIFICACIÓN y debe ser revisado.
        precio_total = precio_mueble + puerta_t1_precio_marco + puerta_t2_precio_marco # Simplificación

        furniture_data = {
            "modelo": modelo,
            "descripcion_mueble": selected_furniture_items[0].text(1), # Guardar descripción
            "precio_base_mueble": precio_mueble,
            "puerta_t1": puerta_t1_modelo,
            "precio_puerta_t1": puerta_t1_precio_marco, # O el precio calculado real
            "puerta_t2": puerta_t2_modelo,
            "precio_puerta_t2": puerta_t2_precio_marco, # O el precio calculado real
            "precio_total": precio_total 
        }
        self.selected_furniture.append(furniture_data)

        item_widget = QTreeWidgetItem([
            modelo,
            puerta_t1_modelo,
            puerta_t2_modelo,
            f"{precio_total:.2f}"
        ])
        self.selected_furniture_list.addTopLevelItem(item_widget)
        self.set_project_modified(True)

    def delete_selected_furniture(self): #
        selected_items = self.selected_furniture_list.selectedItems()
        if not selected_items:
            # Si no hay selección, opcionalmente eliminar el último o mostrar mensaje
            if self.selected_furniture_list.topLevelItemCount() > 0:
                 # Preguntar antes de eliminar el último sin selección explícita
                reply = QMessageBox.question(self, "Confirmar Eliminación",
                                             "No hay ningún mueble seleccionado. ¿Desea eliminar el último mueble añadido a la lista?",
                                             QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                if reply == QMessageBox.StandardButton.Yes:
                    item_to_delete = self.selected_furniture_list.topLevelItem(self.selected_furniture_list.topLevelItemCount() - 1)
                    if item_to_delete: selected_items = [item_to_delete] # Proceder a eliminar este
                else:
                    return # No hacer nada si el usuario dice No
            else:
                QMessageBox.information(self, "Información", "No hay muebles en la lista para eliminar.")
                return


        for item in selected_items:
            index = self.selected_furniture_list.indexOfTopLevelItem(item)
            if index != -1:
                self.selected_furniture_list.takeTopLevelItem(index)
                if index < len(self.selected_furniture):
                    del self.selected_furniture[index]
                    self.set_project_modified(True)


def main_GUI_window(): #
    app = QApplication(sys.argv)
    welcome = WelcomePage() #
    mainWin = None # Para mantener referencia a MainWindow

    def show_main_window_new():
        nonlocal mainWin
        if mainWin is None or not mainWin.isVisible(): # Evitar múltiples ventanas principales
            mainWin = MainWindow()
            # MainWindow ya inicia en un estado de "nuevo proyecto"
        mainWin.show()
        mainWin.activateWindow() # Asegurar que esté al frente
        welcome.close()

    def show_main_window_open():
        nonlocal mainWin
        if mainWin is None or not mainWin.isVisible():
            mainWin = MainWindow()
        mainWin.show()
        mainWin.activateWindow()
        mainWin.on_open_project_action() # Llamar a la acción de abrir
        welcome.close()

    welcome.new_btn.clicked.connect(show_main_window_new) #
    welcome.open_btn.clicked.connect(show_main_window_open) #

    welcome.show()
    sys.exit(app.exec())

