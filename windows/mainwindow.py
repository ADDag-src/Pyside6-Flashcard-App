from PySide6.QtWidgets import QPushButton,  QVBoxLayout, QHBoxLayout, QTableView, QLabel, QSizePolicy, QAbstractItemView
from PySide6.QtCore import Qt


def build_ui():
    # -------------------------|defining layouts|------------------------- #
    master_layout = QVBoxLayout()
    label_layout = QHBoxLayout()
    button_layout = QHBoxLayout()
    deck_list_layout = QHBoxLayout()

    # -------------------------|defining buttons|------------------------- #
    new_deck_button = QPushButton("New deck")
    new_deck_button.setStyleSheet("""
        QPushButton {
            color: white;
            background-color: #1e5bbf;
            font-size: 15px;
        }
        QPushButton:hover {
            background-color: #5ab0ff;
        }
    """)

    del_deck_button = QPushButton("Delete deck")
    del_deck_button.setStyleSheet("""
        QPushButton {
            color: white;
            background-color: #8b0000;
            font-size: 15px;
        }
        QPushButton:hover {
            background-color: #ff4d4d;
        }
    """)

    edit_deck = QPushButton("Edit deck")
    edit_deck.setStyleSheet("""
        QPushButton {
            color: white;
            background-color: #1e5bbf;
            font-size: 15px;
        }
        QPushButton:hover {
            background-color: #5ab0ff;
        }
    """)

    add_card_to_deck = QPushButton("Add card(s) to selected")
    add_card_to_deck.setStyleSheet("""
        QPushButton {
            color: white;
            background-color: #1e5bbf;
            font-size: 15px;
        }
        QPushButton:hover {
            background-color: #5ab0ff;
        }
    """)

    learn_deck = QPushButton("Learn new cards")
    learn_deck.setStyleSheet("""
            QPushButton {
                color: white;
                background-color: #1e5bbf;
                font-size: 15px;
            }
            QPushButton:hover {
                background-color: #5ab0ff;
            }
        """)

    review_deck = QPushButton("Review Deck")
    review_deck.setStyleSheet("""
        QPushButton {
            color: white;
            background-color: #1e5bbf;
            font-size: 15px;
        }
        QPushButton:hover {
            background-color: #5ab0ff;
        }
    """)

    # -------------------------|adding buttons to layout|------------------------- #
    button_layout.addStretch()
    button_layout.addWidget(new_deck_button)
    button_layout.addSpacing(10)
    button_layout.addWidget(del_deck_button)
    button_layout.addSpacing(10)
    button_layout.addWidget(edit_deck)
    button_layout.addSpacing(10)
    button_layout.addWidget(add_card_to_deck)
    button_layout.addSpacing(10)
    button_layout.addWidget(learn_deck)
    button_layout.addSpacing(10)
    button_layout.addWidget(review_deck)
    button_layout.addStretch()

    # -------------------------|defining and adding label widget to layout|------------------------- #
    deck_list_label = QLabel("Deck List")
    deck_list_label.setAlignment(Qt.AlignCenter)
    deck_list_label.setStyleSheet("color: white; background-color: #3d99f5; font-size: 25px;")
    label_layout.addWidget(deck_list_label)
    # -------------------------|defining and adding list widget to layout|------------------------- #

    deck_list = QTableView()
    deck_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    deck_list.setSelectionBehavior(QAbstractItemView.SelectRows)
    deck_list.setSelectionMode(QAbstractItemView.SingleSelection)
    deck_list_layout.addWidget(deck_list, stretch=1)

    # -------------------------|putting the layouts together and returning|------------------------- #
    master_layout.addLayout(label_layout)
    master_layout.addLayout(deck_list_layout)
    master_layout.addLayout(button_layout)

    return master_layout, {
        "deck_list": deck_list,
        "del_deck_button": del_deck_button,
        "new_deck": new_deck_button,
        "edit_deck": edit_deck,
        "add_card": add_card_to_deck,
        "learn_deck": learn_deck,
        "review": review_deck
    }
