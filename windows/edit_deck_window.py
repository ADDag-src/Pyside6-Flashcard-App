from PySide6.QtGui import QStandardItemModel, QStandardItem, QTextDocument
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QSizePolicy, QPushButton, QMessageBox,
                               QHBoxLayout, QTableView, QAbstractItemView, QInputDialog, QHeaderView)
from PySide6.QtCore import Qt, Signal, QTimer
from datetime import datetime


class EditDeckWindow(QWidget):
    # ---------------| Custom signal to update list in main window |--------------- #
    deck_edited = Signal()

    def __init__(self, deck_name, deck_id, database_manager):
        super().__init__()
        self.deck_id = deck_id
        self.deck_name = deck_name
        self.database_manager = database_manager
        self.setWindowTitle("Edit a deck")
        self.setMinimumSize(805, 550)
        self.layout = QVBoxLayout()

    # -------------------------|layout setup|------------------------- #
        self.deck_name_label = QLabel(f"Editing deck: {self.deck_name}")
        self.deck_name_label.setContentsMargins(0, 0, 0, 20)
        self.deck_name_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.deck_name_label.setStyleSheet("font-size: 25px")

        self.layout.addWidget(self.deck_name_label)

        # -------------------------|card list label|------------------------- #
        self.card_list_label = QLabel("Cards in deck:")
        self.card_list_label.setContentsMargins(0, 0, 0, 20)
        self.card_list_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.card_list_label.setStyleSheet("font-size: 20px")

        self.layout.addWidget(self.card_list_label)

        # -------------------------|card list setup|------------------------- #
        self.card_list = QTableView()
        self.card_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.card_list.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.card_list.setSelectionMode(QAbstractItemView.SingleSelection)

        self.card_list.setStyleSheet("""
        QTableView::indicator {
            border: 1px solid white;
            background-color: transparent;
            width: 14px;
            height: 14px;
            border-radius: 3px;
        }

        QTableView::indicator:checked {
            background-color: red;           /* red fill when checked */
            border: 2px solid white;         /* white outline */
        }
        """)

        self.layout.addWidget(self.card_list, stretch=1)

    # -------------------------|bottom button options|------------------------- #
        self.button_group = QWidget()
        self.button_layout = QHBoxLayout(self.button_group)
        self.button_layout.addStretch()

        # -------------------------|rename deck button|------------------------- #
        self.rename_deck_button = QPushButton("Rename deck")
        self.rename_deck_button.setMaximumWidth(200)
        self.rename_deck_button.setStyleSheet("""
                QPushButton {
                    color: white;
                    background-color: #1e5bbf;
                    font-size: 15px;
                }
                QPushButton:hover {
                    background-color: #5ab0ff;
                }
            """)
        self.button_layout.addWidget(self.rename_deck_button)
        self.button_layout.addSpacing(20)

        # -------------------------|delete cards button|------------------------- #
        self.del_card_button = QPushButton("Delete selected card(s)")
        self.del_card_button.setMaximumWidth(200)
        self.del_card_button.setStyleSheet("""
                QPushButton {
                    color: white;
                    background-color: #8b0000;
                    font-size: 15px;
                }
                QPushButton:hover {
                    background-color: #ff4d4d;
                }
            """)
        self.button_layout.addWidget(self.del_card_button)
        self.button_layout.addSpacing(20)

        # -------------------------|close button|------------------------- #
        self.close_button = QPushButton("Close")
        self.close_button.setMaximumWidth(200)
        self.close_button.setStyleSheet("""
                        QPushButton {
                            color: white;
                            background-color: #1e5bbf;
                            font-size: 15px;
                        }
                        QPushButton:hover {
                            background-color: #5ab0ff;
                        }
                    """)
        self.button_layout.addWidget(self.close_button)
        self.button_layout.addStretch()

        self.layout.addWidget(self.button_group)

        self.setLayout(self.layout)
        self.refresh_card_list()

    # -------------------------|button connections|------------------------- #
        self.close_button.clicked.connect(self.close_clicked)
        self.rename_deck_button.clicked.connect(self.rename_deck)
        self.del_card_button.clicked.connect(self.delete_cards)

    @staticmethod
    def html_to_plaintext(html_string):
        doc = QTextDocument()
        doc.setHtml(html_string)
        return doc.toPlainText()

    def close_clicked(self):
        self.deck_edited.emit()
        self.close()

    def rename_deck(self):
        name, ok = QInputDialog.getText(self, "Rename Deck", "Enter new deck name:")
        name = name.strip()

        if not ok:
            return

        if not (0 < len(name) < 50):
            QMessageBox.warning(self, "Invalid Name", "Deck name cannot be empty or longer than 50 characters.")
            return

        if name == self.deck_name:
            QMessageBox.information(self, "No Change", "The new name is the same as the current name.")
            return

        if self.database_manager.check_existing(name):
            QMessageBox.warning(self, "Invalid Name", "A deck with that name already exists in the database.")
            return

        self.database_manager.rename_deck(name, self.deck_id)
        self.deck_name = name
        self.deck_name_label.setText("Deck renamed!")
        self.deck_edited.emit()
        QTimer.singleShot(1500, lambda: self.deck_name_label.setText(f"Editing deck: {self.deck_name}"))

    # -------------------------|refresh or populate card list|------------------------- #
    def refresh_card_list(self):
        cards = self.database_manager.get_deck_cards(self.deck_id)
        header = self.card_list.horizontalHeader()
        header.setSectionsClickable(False)
        header.setHighlightSections(False)

        if cards:
            model = QStandardItemModel(len(cards), 4)
            model.setHorizontalHeaderLabels(["Select", "Front", "Back", "Created"])
            for row, (card_id, front, back, created) in enumerate(cards):

                checkbox_item = QStandardItem(" ")
                checkbox_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
                checkbox_item.setCheckState(Qt.Unchecked)
                checkbox_item.setData(card_id, Qt.UserRole)

                front_text = self.html_to_plaintext(front)
                back_text = self.html_to_plaintext(back)
                creation_dt = datetime.strptime(created, "%Y-%m-%dT%H:%M:%S.%f")
                formatted_time = creation_dt.strftime("%b %d, %Y %H:%M")
                items = [
                    checkbox_item,
                    QStandardItem(front_text),
                    QStandardItem(back_text),
                    QStandardItem(formatted_time),
                ]
                for col, item in enumerate(items):
                    item.setTextAlignment(Qt.AlignCenter)
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                    model.setItem(row, col, item)

        else:
            model = QStandardItemModel(0, 4)
            model.setHorizontalHeaderLabels(["Select", "Front", "Back", "Created"])

        self.card_list.setModel(model)

        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Checkbox column
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)

    def delete_cards(self):
        pass
