import os
import sys

from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QInputDialog, QMessageBox, QHeaderView
from PySide6.QtGui import QStandardItemModel, QStandardItem, QIcon
from PySide6.QtCore import Qt, QTimer
from windows.mainwindow import build_ui
from database_manager.db_manager import DBManager
from windows.card_editor_window import CardEditorWindow
from windows.edit_deck_window import EditDeckWindow
from windows.study_window import StudyWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Flashcard App")
        self.setMinimumSize(800, 600)
        self.database_manager = DBManager()
        self.new_card_window = None
        self.deck_edit_window = None
        self.learn_window = None
        self.review_window = None

        status = self.statusBar()
        status.setStyleSheet("color: #3B3B3B;")
        status.showMessage("Flashcard App by ADDag-src")

        # -------------------------|timer to refresh list periodically|------------------------- #

        self.stats_timer = QTimer(self)
        self.stats_timer.timeout.connect(self.refresh_all_deck_stats)
        self.stats_timer.start(2000)

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
        widgets["learn_deck"].clicked.connect(self.learn_deck_window)
        widgets["review"].clicked.connect(self.review_deck_window)

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
        deck_details = self.get_selected_deck()
        if not deck_details:
            return

        deck_name, deck_id = deck_details

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

        model = self.deck_list.model()

        if not model or model.rowCount() != len(decks):
            model = QStandardItemModel(len(decks), 4)
            model.setHorizontalHeaderLabels(["Deck Name", "Total Cards", "Cards to Learn", "Reviews Due"])
            self.deck_list.setModel(model)

        for row, (deck_id, name, created, total, learn, due) in enumerate(decks):
            values = [name, str(total), str(learn), str(due)]
            for col, val in enumerate(values):
                item = model.item(row, col)
                if item is None:
                    item = QStandardItem(val)
                    item.setTextAlignment(Qt.AlignCenter)
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                    model.setItem(row, col, item)
                else:
                    item.setText(val)

    def refresh_all_deck_stats(self):
        decks = self.database_manager.get_all_decks()
        for deck in decks:
            deck_id = deck[0]
            self.database_manager.update_deck_stats(deck_id)
        self.refresh_deck_list()

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

        deck_name, deck_id = deck_details
        self.new_card_window = CardEditorWindow(deck_name, deck_id, self.database_manager)

        # -------------------------|signal that a card was added in the add card window|------------------------- #
        self.new_card_window.card_added.connect(self.refresh_deck_list)
        self.new_card_window.show()

    def edit_deck_window(self):
        deck_details = self.get_selected_deck()
        if not deck_details:
            return

        deck_name, deck_id = deck_details
        self.deck_edit_window = EditDeckWindow(deck_name, deck_id, self.database_manager)

        # -------------------------|signal that an edit happened in deck edit window|------------------------- #
        self.deck_edit_window.deck_edited.connect(self.refresh_deck_list)
        self.deck_edit_window.show()

    def learn_deck_window(self):
        deck_details = self.get_selected_deck()
        if not deck_details:
            return

        deck_name, deck_id = deck_details

        cards = self.database_manager.get_new_cards(deck_id)
        if not cards:
            QMessageBox.information(self, "No Cards", f"No new cards to learn in '{deck_name}'.")
            return

        self.learn_window = StudyWindow(deck_name, deck_id, self.database_manager, "learn", cards)

        # -------------------------|signal that an card status changed in learn window|------------------------- #
        self.learn_window.card_stats_changed.connect(self.refresh_deck_list)

        self.learn_window.show()

    def review_deck_window(self):
        deck_details = self.get_selected_deck()
        if not deck_details:
            return

        deck_name, deck_id = deck_details

        cards = self.database_manager.get_due_cards(deck_id)
        if not cards:
            QMessageBox.information(self, "No Cards", f"No cards are due for review in '{deck_name}'.")
            return

        self.review_window = StudyWindow(deck_name, deck_id, self.database_manager, "review", cards)
        self.review_window.show()


# -------------------------|Icon path handling for packaging|------------------------- #
if getattr(sys, "_MEIPASS", None):
    base_path = sys._MEIPASS
else:
    base_path = os.path.abspath(os.path.dirname(__file__))

icon_file = "app-icon.ico" if sys.platform.startswith("win") else "app-icon.png"
icon_path = os.path.join(base_path, "icons", icon_file)


app = QApplication([])
app.setStyle("Fusion")
app.setWindowIcon(QIcon(icon_path))
window = MainWindow()
window.show()
app.exec()
