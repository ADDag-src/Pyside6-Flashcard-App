from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QTextEdit, QComboBox, QSizePolicy,
                               QPushButton, QMessageBox, QHBoxLayout, QFontComboBox)
from PySide6.QtGui import QFont
from PySide6.QtCore import QTimer
from PySide6.QtCore import Signal
from PySide6.QtCore import Qt


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

        # -------------------------|text control toolbar|------------------------- #
        self.toolbar_container = QWidget()
        self.text_control_layout = QHBoxLayout(self.toolbar_container)
        self.text_control_layout.addSpacing(5)
        self.text_control_layout.setContentsMargins(0, 0, 0, 0)

        self.font_text = QLabel("Font:")
        self.font_text.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        self.font_combobox = QFontComboBox()

        # -------------------------|combining font text and font selector|------------------------- #
        self.font_group = QWidget()
        self.font_group.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)

        self.inner_layout1 = QHBoxLayout(self.font_group)
        self.inner_layout1.setSpacing(5)
        self.inner_layout1.setContentsMargins(0, 0, 0, 0)
        self.inner_layout1.addWidget(self.font_text)
        self.inner_layout1.addWidget(self.font_combobox)

        self.text_control_layout.addWidget(self.font_group)

        self.font_size_text = QLabel("Font size:")
        self.font_size_text.setAlignment(Qt.AlignCenter)

        self.font_size_combobox = QComboBox()
        self.font_size_combobox.addItems([str(size) for size in range(8, 30, 2)])

        # -------------------------|combining font size text and font size selector|------------------------- #
        self.size_group = QWidget()
        self.size_group.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        self.inner_layout2 = QHBoxLayout(self.size_group)
        self.inner_layout2.setSpacing(5)
        self.inner_layout2.setContentsMargins(0, 0, 0, 0)
        self.inner_layout2.addWidget(self.font_size_text)
        self.inner_layout2.addWidget(self.font_size_combobox)

        self.text_control_layout.addWidget(self.size_group)

        # -------------------------|style buttons|------------------------- #
        self.button_bold = QPushButton("Bold")
        self.button_bold.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        self.button_bold.setCheckable(True)
        self.text_control_layout.addWidget(self.button_bold)

        self.button_italic = QPushButton("Italic")
        self.button_italic.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        self.button_italic.setCheckable(True)
        self.text_control_layout.addWidget(self.button_italic)

        self.button_underline = QPushButton("Underline")
        self.button_underline.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        self.button_underline.setCheckable(True)
        self.text_control_layout.addWidget(self.button_underline)
        self.text_control_layout.addStretch()

        # -------------------------|new window UI|------------------------- #
        self.layout = QVBoxLayout()

        self.status_label = QLabel(f"Adding cards to deck: {self.deck_name}")
        self.status_label.setContentsMargins(0, 0, 0, 20)
        self.status_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.status_label.setStyleSheet("font-size: 25px")
        self.layout.addWidget(self.status_label)

        self.layout.addWidget(self.toolbar_container)

        self.front_input = QTextEdit()
        self.front_input.setPlaceholderText("Front of the card")
        self.front_label = QLabel("Front")
        self.front_label.setContentsMargins(5, 0, 0, 0)
        self.layout.addWidget(self.front_label)
        self.layout.addWidget(self.front_input)

        self.back_input = QTextEdit()
        self.back_input.setPlaceholderText("Back of the card")
        self.back_label = QLabel("Back")
        self.back_label.setContentsMargins(5, 0, 0, 0)
        self.layout.addWidget(self.back_label)
        self.layout.addWidget(self.back_input)

        self.add_button = QPushButton("Add Card")
        self.add_button.clicked.connect(self.add_card)
        self.layout.addWidget(self.add_button)

        self.done_button = QPushButton("Done")
        self.done_button.clicked.connect(self.done_clicked)
        self.layout.addWidget(self.done_button)

        self.setLayout(self.layout)

        # -------------------------|connecting the font controls|------------------------- #
        self.font_combobox.currentFontChanged.connect(self.font_changed)
        self.font_size_combobox.currentTextChanged.connect(self.font_size_changed)
        self.button_bold.toggled.connect(self.bold_checked)
        self.button_italic.toggled.connect(self.italics_checked)
        self.button_underline.toggled.connect(self.underline_checked)

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

    def font_changed(self, font):
        self.front_input.setCurrentFont(font)
        self.back_input.setCurrentFont(font)

    def font_size_changed(self, size):
        self.front_input.setFontPointSize(float(size))
        self.back_input.setFontPointSize(float(size))

    def bold_checked(self, checked):
        if checked:
            weight = QFont.Bold
        else:
            weight = QFont.Normal

        for editor in [self.front_input, self.back_input]:
            cursor = editor.textCursor()
            bold_format = cursor.charFormat()
            bold_format.setFontWeight(weight)
            cursor.mergeCharFormat(bold_format)
            editor.setCurrentCharFormat(bold_format)

            if not cursor.hasSelection():
                editor.setFontWeight(weight)

    def italics_checked(self, checked):
        for editor in [self.front_input, self.back_input]:
            cursor = editor.textCursor()
            italic_format = cursor.charFormat()
            italic_format.setFontItalic(checked)
            cursor.mergeCharFormat(italic_format)
            editor.setCurrentCharFormat(italic_format)

            if not cursor.hasSelection():
                editor.setFocus()
                editor.setFontItalic(checked)

    def underline_checked(self, checked):
        for editor in [self.front_input, self.back_input]:
            cursor = editor.textCursor()
            text_format = cursor.charFormat()
            text_format.setFontUnderline(checked)
            cursor.mergeCharFormat(text_format)
            editor.setCurrentCharFormat(text_format)

            if not cursor.hasSelection():
                editor.setFocus()
                editor.setFontUnderline(checked)
