from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QSizePolicy, QPushButton, QMessageBox,
                               QHBoxLayout, QTableView, QAbstractItemView)
from PySide6.QtCore import Qt


class EditDeckWindow(QWidget):
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

    # -------------------------|button connections|------------------------- #
        self.close_button.clicked.connect(self.close_clicked)

    def close_clicked(self):
        self.close()
