from PyQt6.QtWidgets import QMenuBar
from PyQt6.QtGui import QIcon, QAction

class MenuBar(QMenuBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Crear menú 
        file_menu = self.addMenu('&Archivo')
        project_menu = self.addMenu('&Proyecto')
        config_menu = self.addMenu('&Configuración')
        help_menu = self.addMenu('&Ayuda')

        #file menú
        # Acción New
        new_action = QAction(QIcon('new.png'), '&Nuevo', self)
        new_action.setShortcut('Ctrl+N')
        new_action.setStatusTip('New document')
        new_action.triggered.connect(self.new_call)
        file_menu.addAction(new_action)
        
        # Acción Open
        open_action = QAction(QIcon('open.png'), '&Abrir', self)
        open_action.setShortcut('Ctrl+O')
        open_action.setStatusTip('Open document')
        open_action.triggered.connect(self.open_call)
        file_menu.addAction(open_action)
        # Acción Save
        save_action = QAction(QIcon('exit.png'), '&Guardar', self)
        save_action.setShortcut('Ctrl+G')
        save_action.triggered.connect(self.exit_call)
        file_menu.addAction(save_action)       
        # Acción Exit
        exit_action = QAction(QIcon('exit.png'), '&Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.exit_call)
        file_menu.addAction(exit_action)

        #config menu
        #Dark mode
        darkmode_action = QAction('&Modo Obscuro', self)
        darkmode_action.triggered.connect(self.darkmode_call)
        config_menu.addAction(darkmode_action)




        #help menu
        instructive_action = QAction('&Instruvtivo', self)
        instructive_action.triggered.connect(self.instructive_call)
        help_menu.addAction(instructive_action)

    
    def new_call(self):
        print('New')
    
    def open_call(self):
        print('Open')
    
    def exit_call(self):
        print('Exit app')
        self.parent().close()


    def darkmode_call(self):
        print("Darkmode")

    def instructive_call(self):
        print("Instructive")