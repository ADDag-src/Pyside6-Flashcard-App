import os
from collections import deque
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QTextBrowser,
                               QPushButton, QHBoxLayout)
from PySide6.QtCore import Qt, QUrl, Signal


class StudyWindow(QWidget):
    # ---------------| Custom signal to update list in main window |--------------- #
    card_stats_changed = Signal()

    def __init__(self, deck_name, deck_id, database_manager, mode, cards):
        super().__init__()
        self.setWindowModality(Qt.ApplicationModal)
        self.deck_id = deck_id
        self.deck_name = deck_name
        self.database_manager = database_manager
        self.mode = mode
        self.cards = deque(cards)
        self.total_cards = len(self.cards)
        self.completed_count = 0
        self.showing_front = True
        self.setMinimumSize(805, 550)

        # ----|text modularity setup for learn/review |---- #
        if self.mode == "learn":
            self.setWindowTitle(f"Learning new cards")
            self.label_text = f"Learning new cards in deck: {self.deck_name}"
            self.remaining_cards_text = f"{self.completed_count}/{self.total_cards} cards learned"
        else:
            self.setWindowTitle(f"Reviewing cards")
            self.label_text = f"Reviewing cards in deck: {self.deck_name}"
            self.remaining_cards_text = f"{self.completed_count}/{self.total_cards} cards reviewed"

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
        self.side_label.setAlignment(Qt.AlignCenter)
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
            self.again_button.clicked.connect(lambda: self.next_card(repeat=True))

            self.learned_button = QPushButton("Learned it")
            choice_layout.addWidget(self.learned_button)
            self.learned_button.clicked.connect(self.next_card)
        else:
            self.choice_label = QLabel("How well did you remember this card?:")
            choice_layout.addWidget(self.choice_label)

            self.again_button = QPushButton("Wrong, show me again")
            choice_layout.addWidget(self.again_button)
            self.again_button.clicked.connect(lambda: self.next_card(repeat=True))

            self.hard_button = QPushButton("Hard")
            choice_layout.addWidget(self.hard_button)
            self.hard_button.clicked.connect(lambda: self.next_card(grade=3))

            self.good_button = QPushButton("Good")
            choice_layout.addWidget(self.good_button)
            self.good_button.clicked.connect(lambda: self.next_card(grade=4))

            self.easy_button = QPushButton("Easy")
            choice_layout.addWidget(self.easy_button)
            self.easy_button.clicked.connect(lambda: self.next_card(grade=5))

        choice_layout.addStretch()
        choice_layout.setSpacing(20)
        
        self.layout.addWidget(self.choice_widget)

        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.close_clicked)
        self.close_button.hide()
        self.layout.addWidget(self.close_button)

        self.setLayout(self.layout)
        self.show_card()

    def show_card(self):
        if self.cards:
            card = self.cards[0]
            front_html = self.patch_image_paths(card["front"], card.get("front_image"))
            self.card_screen.setHtml(front_html)
            self.show_answer_button.setText("Show Answer")
            self.choice_widget.setEnabled(False)
            self.side_label.setText("Front")
            self.showing_front = True

            if self.mode == "review":
                self.hard_button.setText("Hard [—]")
                self.good_button.setText("Good [—]")
                self.easy_button.setText("Easy [—]")
        else:
            self.card_screen.setHtml("""
                <div style="text-align:center; margin-top:40px; font-size:24px; color:#3d99f5;">
                    <b>All cards completed! Well Done!</b>
                </div>
            """)
            self.show_answer_button.hide()
            self.choice_widget.hide()
            self.close_button.show()

    def flip_card(self):
        if self.cards:
            card = self.cards[0]
            card_stats = self.database_manager.get_sm2_intervals(card["id"])
            if card_stats:
                for key in card_stats:
                    interval = int(card_stats[key])
                    if interval < 365:
                        card_stats[key] = f"{interval} day(s)"
                    else:
                        years = interval / 365
                        card_stats[key] = f"{years:.1f} year(s)"

                self.hard_button.setText(f"Hard [{card_stats['hard_interval']}]")
                self.good_button.setText(f"Good [{card_stats['good_interval']}]")
                self.easy_button.setText(f"Easy [{card_stats['easy_interval']}]")

            if self.showing_front:
                back_html = self.patch_image_paths(card["back"], card.get("back_image"))
                self.show_answer_button.setText("Show Question")
                self.card_screen.setHtml(back_html)
                self.choice_widget.setEnabled(True)
                self.side_label.setText("Back")
                self.set_card_background(False)
            else:
                front_html = self.patch_image_paths(card["front"], card.get("front_image"))
                self.show_answer_button.setText("Show Answer")
                self.card_screen.setHtml(front_html)
                self.choice_widget.setEnabled(False)
                self.side_label.setText("Front")
                self.set_card_background(True)

            self.showing_front = not self.showing_front

    def next_card(self, grade=None, repeat=False):
        if not self.cards:
            return

        card = self.cards.popleft()

        if self.mode == "learn":
            if repeat:
                self.cards.append(card)
            else:
                self.database_manager.update_card_sm2(card["id"], grade=3, deck_id=self.deck_id)
                self.completed_count += 1
                self.card_stats_changed.emit()

        elif self.mode == "review":
            if repeat:
                self.cards.append(card)
                self.database_manager.update_card_sm2(card["id"], grade=1, deck_id=self.deck_id)
                self.card_stats_changed.emit()
            else:
                self.database_manager.update_card_sm2(card["id"], grade=grade, deck_id=self.deck_id)
                self.completed_count += 1
                self.card_stats_changed.emit()

        self.set_card_background(True)
        self.update_progress_label()
        self.show_card()

    def update_progress_label(self):
        if self.mode == "learn":
            self.remaining_label.setText(
                f"{self.completed_count}/{self.total_cards} cards learned")
        else:
            self.remaining_label.setText(
                f"{self.completed_count}/{self.total_cards} cards reviewed")

    def close_clicked(self):
        self.card_stats_changed.emit()
        self.set_card_background(True)
        self.close()

    def set_card_background(self, is_front):
        if is_front:
            self.card_screen.setStyleSheet("background-color: #2d2d2d;")
        else:
            self.card_screen.setStyleSheet("background-color: #3B3B3B;")

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
