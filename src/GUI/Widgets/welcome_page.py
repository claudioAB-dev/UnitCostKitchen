from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QSpacerItem, QSizePolicy
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

class WelcomePage(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bienvenido a Kitchen Software")
        self.setMinimumSize(400, 300) # Establecer un tamaño mínimo

        # Paleta de colores sugerida (puedes ajustarla)
        primary_color = "#3498db"  # Azul
        secondary_color = "#2ecc71" # Verde
        text_color_light = "#ecf0f1" # Casi blanco
        background_color = "#2c3e50" # Azul oscuro/gris

        self.setStyleSheet(f"""
            QWidget {{
                background-color: {background_color};
                color: {text_color_light};
                font-family: Arial, sans-serif; /* Fuente más moderna */
            }}
            QLabel#TitleLabel {{
                font-size: 28px; /* Tamaño más grande para el título */
                font-weight: bold;
                color: {primary_color}; /* Color primario para el título */
                padding-bottom: 10px; /* Espacio debajo del título */
            }}
            QLabel#SubtitleLabel {{
                font-size: 16px;
                color: {text_color_light};
                padding-bottom: 20px; /* Espacio debajo del subtítulo */
            }}
            QPushButton {{
                background-color: {primary_color};
                color: {text_color_light};
                border: none;
                padding: 12px 25px; /* Más padding para botones más grandes */
                font-size: 16px;
                border-radius: 5px; /* Bordes redondeados */
                min-width: 150px; /* Ancho mínimo para los botones */
            }}
            QPushButton:hover {{
                background-color: #2980b9; /* Azul un poco más oscuro al pasar el mouse */
            }}
            QPushButton:pressed {{
                background-color: #1f618d; /* Azul aún más oscuro al presionar */
            }}
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30) # Márgenes alrededor de todo
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter) # Centrar contenido verticalmente

        # Título
        title_label = QLabel("Kitchen Software & control + n")
        title_label.setObjectName("TitleLabel") # Para aplicar estilos específicos
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)

        # Subtítulo
        subtitle_label = QLabel("Selecciona una opción para continuar:")
        subtitle_label.setObjectName("SubtitleLabel")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(subtitle_label)

        # Espaciador
        main_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # Layout para los botones (horizontal para que estén uno al lado del otro o vertical si prefieres)
        buttons_layout = QVBoxLayout() # Cambiado a QVBoxLayout para apilarlos con espacio
        buttons_layout.setSpacing(15) # Espacio entre los botones
        buttons_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)


        self.new_btn = QPushButton("Nuevo archivo")
        buttons_layout.addWidget(self.new_btn)

        self.open_btn = QPushButton("Abrir archivo")
        buttons_layout.addWidget(self.open_btn)

        main_layout.addLayout(buttons_layout)

        # Espaciador inferior
        main_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        self.setLayout(main_layout)

