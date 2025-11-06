from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QInputDialog, QMessageBox, QHeaderView
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtCore import Qt
from windows.mainwindow import build_ui
from database_manager.db_manager import DBManager
from windows.new_card_window import NewCardWindow
from windows.edit_deck_window import EditDeckWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Flashcard App")
        self.setMinimumSize(800, 600)
        self.database_manager = DBManager()
        self.new_card_window = None
        self.deck_edit_window = None

        # -------------------------|building main window|------------------------- #
        layout, widgets = build_ui()
        self.layout = layout
        self.deck_list = widgets["deck_list"]
        self.refresh_deck_list()
        self.main_buttons = widgets

        # -------------------------|connect buttons functionality|------------------------- #

        widgets["new_deck"].clicked.connect(self.add_new_deck)
        widgets["del_deck_button"].clicked.connect(self.del_deck)
        widgets["add_card"].clicked.connect(self.add_cards_window)
        widgets["edit_deck"].clicked.connect(self.edit_deck_window)

        # -------------------------|main container definition|------------------------- #
        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)

    # -------------------------|add deck method|------------------------- #
    def add_new_deck(self):
        name, ok = QInputDialog.getText(self, "New Deck", "Enter deck name:")
        name = name.strip()

        if not ok:
            return

        if not (0 < len(name) < 50):
            QMessageBox.warning(self, "Invalid Name", "Deck name cannot be empty or longer than 50 characters.")
            return

        if self.database_manager.check_existing(name):
            QMessageBox.warning(self, "Invalid Name", "A deck with that name already exists in the database.")
            return

        self.database_manager.add_deck(name)
        self.refresh_deck_list()

    # -------------------------|delete deck method|------------------------- #
    def del_deck(self):
        selected_indexes = self.deck_list.selectionModel().selectedRows()
        if not selected_indexes:
            QMessageBox.information(self, "No Selection", "Please select a deck to delete.")
            return
        selected_row = selected_indexes[0].row()
        deck_name = self.deck_list.model().item(selected_row, 0).text()
        deck_id = self.database_manager.get_deck_id_by_name(deck_name)
        if deck_id is None:
            QMessageBox.warning(self, "Error", f"Deck '{deck_name}' not found in database.")
            return
        reply = QMessageBox.question(
            self,
            "Delete Deck",
            f"Are you sure you want to delete the deck '{deck_name}'?\nAll associated cards will be removed.",
            QMessageBox.Yes | QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            self.database_manager.del_deck(deck_id)
            self.refresh_deck_list()

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
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                    model.setItem(row, col, item)
            self.deck_list.setModel(model)
        else:
            model = QStandardItemModel(0, 4)
            model.setHorizontalHeaderLabels(["Deck Name", "Total Cards", "Cards to learn", "Due"])
            self.deck_list.setModel(model)

    def get_selected_deck(self):
        selected_indexes = self.deck_list.selectionModel().selectedRows()
        if not selected_indexes:
            QMessageBox.information(self, "No Selection", "Please select a deck to perform the action on.")
            return
        selected_row = selected_indexes[0].row()
        deck_name = self.deck_list.model().item(selected_row, 0).text()
        deck_id = self.database_manager.get_deck_id_by_name(deck_name)
        return deck_name, deck_id

    def add_cards_window(self):
        deck_details = self.get_selected_deck()
        if not deck_details:
            return

        self.new_card_window = NewCardWindow(deck_details[0], deck_details[1], self.database_manager)

        # -------------------------|signal that a card was added in the add card window|------------------------- #
        self.new_card_window.card_added.connect(self.refresh_deck_list)
        self.new_card_window.show()

    def edit_deck_window(self):
        deck_details = self.get_selected_deck()
        if not deck_details:
            return

        self.deck_edit_window = EditDeckWindow(deck_details[0], deck_details[1], self.database_manager)

        # -------------------------|signal that an edit happened in deck edit window|------------------------- #
        self.deck_edit_window.deck_edited.connect(self.refresh_deck_list)
        self.deck_edit_window.show()


app = QApplication([])
app.setStyle("Fusion")
window = MainWindow()
window.show()
app.exec()
