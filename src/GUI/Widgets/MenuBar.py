from PyQt6.QtWidgets import QMenuBar
from PyQt6.QtGui import QIcon, QAction,QDesktopServices
from PyQt6.QtCore import QUrl

class MenuBar(QMenuBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Crear menú 
        file_menu = self.addMenu('&Archivo')
        project_menu = self.addMenu('&Proyecto') # Considera mover aquí acciones específicas del proyecto
        config_menu = self.addMenu('&Configuración')
        help_menu = self.addMenu('&Ayuda')

        #file menú
        # Acción New
        new_action = QAction(QIcon('new.png'), '&Nuevo', self) # Asume que tienes 'new.png' o quita el QIcon
        new_action.setShortcut('Ctrl+N')
        new_action.setStatusTip('Crear un nuevo proyecto')
        new_action.triggered.connect(self.new_project_trigger)
        file_menu.addAction(new_action)
        
        # Acción Open
        open_action = QAction(QIcon('open.png'), '&Abrir', self) # Asume que tienes 'open.png'
        open_action.setShortcut('Ctrl+O')
        open_action.setStatusTip('Abrir un proyecto existente')
        open_action.triggered.connect(self.open_project_trigger)
        file_menu.addAction(open_action)

        # Acción Save
        save_action = QAction(QIcon('save.png'), '&Guardar', self) # Asume que tienes 'save.png' o usa texto
        save_action.setShortcut('Ctrl+S')
        save_action.setStatusTip('Guardar el proyecto actual')
        save_action.triggered.connect(self.save_project_trigger)
        file_menu.addAction(save_action)       

        # Acción Save As
        save_as_action = QAction('&Guardar Como...', self)
        save_as_action.setShortcut('Ctrl+Shift+S')
        save_as_action.setStatusTip('Guardar el proyecto actual en un nuevo archivo')
        save_as_action.triggered.connect(self.save_project_as_trigger)
        file_menu.addAction(save_as_action)

        file_menu.addSeparator()

        # Acción Exit
        exit_action = QAction(QIcon('exit.png'), '&Salir', self) # Asume que tienes 'exit.png'
        exit_action.setShortcut('Ctrl+Q')
        exit_action.setStatusTip('Salir de la aplicación')
        exit_action.triggered.connect(self.exit_call)
        file_menu.addAction(exit_action)

        #proyect menu
        new_item_action = QAction('Nuevo item global', self)
        new_item_action.setStatusTip("Agregar nuevo producto a la base de datos")
        new_item_action.triggered.connect(self.new_item_call)
        project_menu.addAction(new_item_action)
        #config menu

        #help menu
        instructive_action = QAction('&Instructivo', self) # Corregido "Instruvtivo"
        instructive_action.triggered.connect(self.instructive_call)
        help_menu.addAction(instructive_action)

    def new_project_trigger(self):
        if hasattr(self.parent(), 'on_new_project_action'):
            self.parent().on_new_project_action()
    
    def open_project_trigger(self):
        if hasattr(self.parent(), 'on_open_project_action'):
            self.parent().on_open_project_action()
    
    def save_project_trigger(self):
        if hasattr(self.parent(), 'on_save_project_action'):
            self.parent().on_save_project_action()

    def save_project_as_trigger(self):
        if hasattr(self.parent(), 'on_save_project_as_action'):
            self.parent().on_save_project_as_action()

    def exit_call(self):
        # print('Exit app') # El print es para depuración, puede removerse
        if hasattr(self.parent(), 'close'):
            self.parent().close() # Esto invocará el closeEvent de MainWindow

    def darkmode_call(self):
        print("Darkmode") # Mantener si es funcional o implementar

    def instructive_call(self):
        # Define la URL que quieres abrir
        url = QUrl('https://github.com/claudioAB-dev/UnitCostKitchen')
        QDesktopServices.openUrl(url)
    def new_item_call(self):
        print("New Item")