from PySide6.QtWidgets import QApplication, QMainWindow, QWidget
from windows.mainwindow import build_ui


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Flashcard App")
        self.setMinimumSize(800, 600)
        self.setStyleSheet("background-color: #31363F;")

        # -------------------------|building main window|------------------------- #
        layout, widgets = build_ui()
        self.layout = layout
        self.deck_list = widgets["deck_list"]
        self.main_buttons = widgets

        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)


app = QApplication([])
window = MainWindow()
window.show()
app.exec()
