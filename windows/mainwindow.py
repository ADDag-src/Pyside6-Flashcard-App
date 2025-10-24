from PySide6.QtWidgets import QPushButton,  QVBoxLayout, QHBoxLayout, QTableView, QLabel
from PySide6.QtCore import Qt


def build_ui():
    # -------------------------|defining layouts|------------------------- #
    master_layout = QVBoxLayout()
    label_layout = QHBoxLayout()
    button_layout = QHBoxLayout()
    deck_list_layout = QHBoxLayout()

    # -------------------------|defining buttons|------------------------- #
    new_deck_button = QPushButton("New deck")
    new_deck_button.setStyleSheet("color: white; background-color: #3d99f5; font-size: 15px;")

    edit_deck = QPushButton("Edit deck")
    edit_deck.setStyleSheet("color: white; background-color: #3d99f5; font-size: 15px;")

    add_card_to_deck = QPushButton("Add card to selected")
    add_card_to_deck.setStyleSheet("color: white; background-color: #3d99f5; font-size: 15px;")

    review_deck = QPushButton("Review Deck")
    review_deck.setStyleSheet("color: white; background-color: #3d99f5; font-size: 15px;")

    # -------------------------|adding buttons to layout|------------------------- #
    button_layout.addWidget(new_deck_button)
    button_layout.addWidget(edit_deck)
    button_layout.addWidget(add_card_to_deck)
    button_layout.addWidget(review_deck)

    # -------------------------|defining and adding label widget to layout|------------------------- #
    deck_list_label = QLabel("Deck List")
    deck_list_label.setAlignment(Qt.AlignCenter)
    deck_list_label.setStyleSheet("color: white; background-color: #3d99f5; font-size: 25px;")
    label_layout.addWidget(deck_list_label)
    # -------------------------|defining and adding list widget to layout|------------------------- #

    deck_list = QTableView()
    deck_list_layout.addWidget(deck_list)

    # -------------------------|putting the layouts together and returning|------------------------- #
    master_layout.addLayout(label_layout)
    master_layout.addLayout(deck_list_layout)
    master_layout.addLayout(button_layout)

    return master_layout, {
        "deck_list": deck_list,
        "new_deck": new_deck_button,
        "edit_deck": edit_deck,
        "add_card": add_card_to_deck,
        "review": review_deck
    }
