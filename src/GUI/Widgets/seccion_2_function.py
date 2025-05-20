from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel

class IndividualConfigurationWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.layout = QVBoxLayout(self)
        self.title_label = QLabel("Sección 2 (Redimensionable)")
        self.layout.addWidget(self.title_label)

    def set_title(self, text):
        self.title_label.setText(text)