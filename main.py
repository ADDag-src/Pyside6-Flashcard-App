from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QInputDialog, QMessageBox, QHeaderView
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtCore import Qt
from windows.mainwindow import build_ui
from database_manager.db_manager import DBManager


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Flashcard App")
        self.setMinimumSize(800, 600)
        self.database_manager = DBManager()

        # -------------------------|building main window|------------------------- #
        layout, widgets = build_ui()
        self.layout = layout
        self.deck_list = widgets["deck_list"]
        self.refresh_deck_list()
        self.main_buttons = widgets

        # -------------------------|connect buttons functionality|------------------------- #

        widgets["new_deck"].clicked.connect(self.add_new_deck)

        # -------------------------|main container definition|------------------------- #
        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)

    # -------------------------|add deck method|------------------------- #
    def add_new_deck(self):
        name, ok = QInputDialog.getText(self, "New Deck", "Enter deck name:")
        name = name.strip()

        if ok and 0 < len(name) < 50:
            if not self.database_manager.check_existing(name):
                self.database_manager.add_deck(name)
                self.refresh_deck_list()
            else:
                QMessageBox.warning(self, "Invalid Name", "A deck with that name already exists in the database.")
        elif ok:
            QMessageBox.warning(self, "Invalid Name", "Deck name cannot be empty or longer than 50 characters.")

    # -------------------------|delete deck method|------------------------- #
    def del_deck(self):
        pass

    # -------------------------|refresh or populate deck method|------------------------- #
    def refresh_deck_list(self):
        decks = self.database_manager.get_all_decks()
        header = self.deck_list.horizontalHeader()
        header.setSectionsClickable(False)
        header.setHighlightSections(False)
        header.setSectionResizeMode(QHeaderView.Stretch)
        if decks:
            model = QStandardItemModel(len(decks), 4)
            model.setHorizontalHeaderLabels(["Deck Name", "Total Cards", "Cards to learn", "Due"])
            for row, (deck_id, name, created, total, learn, due) in enumerate(decks):
                items = [
                    QStandardItem(name),
                    QStandardItem(str(total)),
                    QStandardItem(str(learn)),
                    QStandardItem(str(due))
                ]
                for col, item in enumerate(items):
                    item.setTextAlignment(Qt.AlignCenter)
                    model.setItem(row, col, item)
            self.deck_list.setModel(model)
        else:
            model = QStandardItemModel(0, 5)
            model.setHorizontalHeaderLabels(["Deck Name", "Created", "Total Cards", "Learning", "Due"])
            self.deck_list.setModel(model)


app = QApplication([])
app.setStyle("Fusion")
window = MainWindow()
window.show()
app.exec()
