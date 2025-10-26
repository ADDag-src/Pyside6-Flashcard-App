from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit, QPushButton, QMessageBox
from PySide6.QtCore import QTimer
from PySide6.QtCore import Signal


class NewCardWindow(QWidget):
    # ---------------| Custom signal to update list in main window |--------------- #
    card_added = Signal()

    def __init__(self, deck_name, deck_id, database_manager):
        super().__init__()
        self.deck_id = deck_id
        self.deck_name = deck_name
        self.database_manager = database_manager
        self.setWindowTitle("Add New Card")
        self.setMinimumSize(750, 550)

        # -------------------------|new window UI|------------------------- #
        layout = QVBoxLayout()
        self.status_label = QLabel(f"Adding cards to deck: {self.deck_name}")
        self.status_label.setStyleSheet("font-size: 20px")
        layout.addWidget(self.status_label)

        self.front_input = QTextEdit()
        self.front_input.setPlaceholderText("Front of the card")
        layout.addWidget(QLabel("Front"))
        layout.addWidget(self.front_input)

        self.back_input = QTextEdit()
        self.back_input.setPlaceholderText("Back of the card")
        layout.addWidget(QLabel("Back"))
        layout.addWidget(self.back_input)

        self.add_button = QPushButton("Add Card")
        self.add_button.clicked.connect(self.add_card)
        layout.addWidget(self.add_button)

        self.done_button = QPushButton("Done")
        self.done_button.clicked.connect(self.done_clicked)
        layout.addWidget(self.done_button)

        self.setLayout(layout)

    def add_card(self):
        front = self.front_input.toPlainText().strip()
        back = self.back_input.toPlainText().strip()

        if not front or not back:
            QMessageBox.warning(self, "Missing Fields", "Both front and back must be filled.")
            return
        image_path = None
        self.database_manager.add_card(self.deck_id, front, back, image_path)
        self.status_label.setText("Card Added!")
        self.card_added.emit()
        QTimer.singleShot(1500, lambda: self.status_label.setText(f"Adding cards to deck: {self.deck_name}"))
        self.front_input.clear()
        self.back_input.clear()

    def done_clicked(self):
        self.card_added.emit()
        self.close()
