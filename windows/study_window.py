import os
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QTextBrowser, QComboBox, QSizePolicy,
                               QPushButton, QMessageBox, QHBoxLayout, QFontComboBox)
from PySide6.QtCore import Qt, QUrl


class StudyWindow(QWidget):
    def __init__(self, deck_name, deck_id, database_manager, mode, cards):
        super().__init__()
        self.deck_id = deck_id
        self.deck_name = deck_name
        self.database_manager = database_manager
        self.mode = mode
        self.cards = cards
        self.total_cards = len(self.cards)
        self.counter = 0
        self.showing_front = True

        self.setMinimumSize(805, 550)

        # ----|text modularity setup for learn/review |---- #
        if self.mode == "learn":
            self.setWindowTitle(f"Learning new cards")
            self.label_text = f"Learning new cards in deck: {self.deck_name}"
            self.remaining_cards_text = f"{self.counter}/{self.total_cards} remaining to learn"
        else:
            self.setWindowTitle(f"Reviewing cards")
            self.label_text = f"Reviewing cards in deck: {self.deck_name}"
            self.remaining_cards_text = f"{self.counter}/{self.total_cards} remaining to review"

        # ----| UI layout |---- #
        self.layout = QVBoxLayout()

        self.top_label = QLabel(self.label_text)
        self.top_label.setAlignment(Qt.AlignCenter)
        self.top_label.setStyleSheet("color: white; background-color: #3d99f5; font-size: 25px;")
        self.layout.addWidget(self.top_label)

        self.remaining_label = QLabel(self.remaining_cards_text)
        self.remaining_label.setAlignment(Qt.AlignCenter)
        self.remaining_label.setStyleSheet("color: white; background-color: #3d99f5; font-size: 19px;")
        self.layout.addWidget(self.remaining_label)

        self.side_label = QLabel("Front")
        self.side_label.setAlignment(Qt.AlignRight)
        self.side_label.setStyleSheet("color: gray; font-size: 14px;")
        self.layout.addWidget(self.side_label)

        self.card_screen = QTextBrowser()
        self.layout.addWidget(self.card_screen)

        self.show_answer_button = QPushButton("Show Answer")
        self.show_answer_button.clicked.connect(self.flip_card)
        self.layout.addWidget(self.show_answer_button)

        # ----| button modularity for learning/reviewing |---- #

        self.choice_widget = QWidget()
        choice_layout = QHBoxLayout(self.choice_widget)
        choice_layout.addStretch()

        if self.mode == "learn":
            self.again_button = QPushButton("Show me again")
            choice_layout.addWidget(self.again_button)

            self.learned_button = QPushButton("Learned it")
            choice_layout.addWidget(self.learned_button)
        else:
            self.choice_label = QLabel("How well did you remember this card?:")
            choice_layout.addWidget(self.choice_label)

            self.again_button = QPushButton("Wrong, show me again")
            choice_layout.addWidget(self.again_button)

            self.hard_button = QPushButton("Hard")
            choice_layout.addWidget(self.hard_button)

            self.good_button = QPushButton("Good")
            choice_layout.addWidget(self.good_button)

            self.easy_button = QPushButton("Easy")
            choice_layout.addWidget(self.easy_button)

        choice_layout.addStretch()
        choice_layout.setSpacing(20)
        
        self.layout.addWidget(self.choice_widget)
        self.choice_widget.hide()

        self.setLayout(self.layout)
        self.show_card()

    def show_card(self):
        if self.counter < self.total_cards:
            card = self.cards[self.counter]
            front_html = self.patch_image_paths(card["front"], card.get("front_image"))
            self.card_screen.setHtml(front_html)
            self.show_answer_button.setText("Show Answer")
            self.choice_widget.hide()
            self.side_label.setText("Front")
            self.showing_front = True
        else:
            self.card_screen.setHtml("""
                <div style="text-align:center; margin-top:40px; font-size:24px; color:#3d99f5;">
                    <b>All cards completed! Well Done!</b>
                </div>
            """)
            self.show_answer_button.setEnabled(False)
            self.choice_widget.hide()

    def flip_card(self):
        if self.counter < self.total_cards:
            card = self.cards[self.counter]
            if self.showing_front:
                back_html = self.patch_image_paths(card["back"], card.get("back_image"))
                self.show_answer_button.setText("Show Question")
                self.card_screen.setHtml(back_html)
                self.choice_widget.show()
                self.side_label.setText("Back")
            else:
                front_html = self.patch_image_paths(card["front"], card.get("front_image"))
                self.show_answer_button.setText("Show Answer")
                self.card_screen.setHtml(front_html)
                self.choice_widget.hide()
                self.side_label.setText("Front")
            self.showing_front = not self.showing_front

    # --------| method that fixes the html images to correctly show|------------- #
    def patch_image_paths(self, html, image_filename):
        if not html:
            return ""
        if image_filename:
            image_path = os.path.join(self.database_manager.image_folder_path, image_filename)
            if os.path.exists(image_path):
                image_url = QUrl.fromLocalFile(image_path).toString()
                html = html.replace(image_filename, image_url)
            else:
                html += f"<p><i>Image file '{image_filename}' not found</i></p>"
        return html
