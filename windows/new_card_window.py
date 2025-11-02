from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QTextEdit, QComboBox, QSizePolicy,
                               QPushButton, QMessageBox, QHBoxLayout, QFontComboBox)
from PySide6.QtGui import QFont, QTextCharFormat, QTextCursor, QImage
from PySide6.QtCore import QTimer
from PySide6.QtCore import Signal
from PySide6.QtCore import Qt
from datetime import datetime
from urllib.parse import quote
from pathlib import Path
import re


# ----| QTextEdit subclass to ensure that selected text is cleared if clicking in another QTextEdit |---- #
# ----| and custom behaviour to accept drag and drop images |---- #
class FlashcardTextEdit(QTextEdit):
    def __init__(self, name, on_focus_callback, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name
        self.on_focus_callback = on_focus_callback
        self.setAcceptDrops(True)
        self.pending_images = {}
        self.image_filename = None

    # ----| method that is called when an editor is focused, and trigger callback |---- #
    def focusInEvent(self, event):
        super().focusInEvent(event)
        if self.on_focus_callback:
            self.on_focus_callback(self)

    # ----| check if the file that is drag and dropped is a supported image |---- #
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            image_formats = ["png", "jpg", "jpeg", "bmp"]
            for url in event.mimeData().urls():
                image_url_ending = url.toLocalFile().split(".")[-1].lower()
                if image_url_ending in image_formats:
                    event.acceptProposedAction()
                    return
        event.ignore()

    # ----| handle the image, save a temp QImage for later saving and display the image |---- #
    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                local_path = url.toLocalFile()
                image = QImage(local_path)
                image_url = self.path_to_file_url(local_path)
                if not image.isNull():
                    if self.pending_images and self.has_image():
                        reply = QMessageBox.question(
                            self,
                            "Replace Image?",
                            "This card already has an image. Do you want to replace it?",
                            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                        )
                        if reply == QMessageBox.StandardButton.Yes:
                            self.replace_image(image_url, image)
                    else:
                        cursor = self.textCursor()
                        current_format = cursor.charFormat()

                        placeholder = f"__img_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}__"
                        self.pending_images[placeholder] = image
                        self.insertHtml(f'<img src="{image_url}" /><br>&nbsp;')

                        cursor = self.textCursor()
                        cursor.setCharFormat(current_format)
                        self.setTextCursor(cursor)
                        self.setFocus()
            event.acceptProposedAction()
        else:
            event.ignore()

    # ----| fix an image's path to display correctly in the QTextEdit|---- #
    @staticmethod
    def path_to_file_url(path):
        resolved = str(Path(path).resolve())
        normalized = resolved.replace("\\", "/")
        return f"file:///{quote(normalized)}"

    # ----| method to handle replacing images if a new one is added to same card|---- #
    def replace_image(self, new_image_url, new_image_obj):
        cursor = self.textCursor()
        current_format = cursor.charFormat()

        cursor.select(QTextCursor.SelectionType.Document)
        all_html = cursor.selection().toHtml()

        new_img_tag = f'<img src="{new_image_url}" /><br>&nbsp;'
        altered_html = re.sub(r"<img[^>]*>", new_img_tag, all_html, flags=re.IGNORECASE)
        self.setHtml(altered_html)

        cursor = self.textCursor()
        cursor.setCharFormat(current_format)
        self.setTextCursor(cursor)
        self.setFocus()

        self.pending_images.clear()
        placeholder = f"__img_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}__"
        self.pending_images[placeholder] = new_image_obj

    # ----| method to check if there's an image in the current html|---- #
    def has_image(self):
        return bool(re.search(r"<img[^>]*>", self.toHtml(), flags=re.IGNORECASE))

    # ----| method to finalise card html and save images to save folder and reference those images in the html|---- #
    def finalize_images(self, image_folder_path):
        image_folder_path = Path(image_folder_path)
        self.image_filename = None
        if not self.pending_images:
            return self.toHtml()

        html = self.toHtml()
        matches = re.findall(r'src="file:///([^"]+)"', html)

        for placeholder, q_image in self.pending_images.items():
            if not matches:
                continue

            matched_url = matches[0]

            ext_match = re.search(r'\.([a-zA-Z0-9]+)$', matched_url)
            ext = ext_match.group(1).lower() if ext_match else "png"

            filename = f"{placeholder}.{ext}"
            save_path = image_folder_path.joinpath(filename)
            if not save_path.exists():
                try:
                    q_image.save(str(save_path), ext.upper())
                    self.image_filename = filename
                except Exception as e:
                    print(f"Failed to save image {filename}: {e}")

            full_src = f'src="file:///{matched_url}"'
            new_src = f'src="images/{filename}"'
            html = html.replace(full_src, new_src)

        self.pending_images.clear()
        return html


class NewCardWindow(QWidget):
    # ---------------| Custom signal to update list in main window |--------------- #
    card_added = Signal()

    def __init__(self, deck_name, deck_id, database_manager):
        super().__init__()
        self.deck_id = deck_id
        self.deck_name = deck_name
        self.database_manager = database_manager
        self.setWindowTitle("Add New Card")
        self.setMinimumSize(805, 550)

        # -------------------------|text control toolbar|------------------------- #
        self.toolbar_container = QWidget()
        self.text_control_layout = QHBoxLayout(self.toolbar_container)
        self.text_control_layout.addSpacing(5)
        self.text_control_layout.setContentsMargins(0, 0, 0, 0)

        self.font_text = QLabel("Font:")
        self.font_text.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        self.font_combobox = QFontComboBox()
        self.font_combobox.setEditable(False)
        self.font_combobox.setMaxVisibleItems(15)

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
        self.font_size_combobox.addItems([str(size) for size in range(8, 42, 2)])
        self.font_size_combobox.setCurrentText("20")

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
        self.text_control_layout.addWidget(self.button_bold)

        self.button_italic = QPushButton("Italic")
        self.button_italic.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        self.text_control_layout.addWidget(self.button_italic)

        self.button_underline = QPushButton("Underline")
        self.button_underline.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        self.text_control_layout.addWidget(self.button_underline)

        # -------------------------|text alignment options|------------------------- #
        self.align_group = QWidget()
        self.inner_layout3 = QHBoxLayout(self.align_group)

        self.align_label = QLabel("Align text:")
        self.inner_layout3.addWidget(self.align_label)

        self.button_align_left = QPushButton("Left")
        self.button_align_center = QPushButton("Center")
        self.button_align_right = QPushButton("Right")
        self.inner_layout3.addWidget(self.button_align_left)
        self.inner_layout3.addWidget(self.button_align_center)
        self.inner_layout3.addWidget(self.button_align_right)
        self.inner_layout3.setSpacing(5)
        self.inner_layout3.setContentsMargins(0, 0, 0, 0)

        self.text_control_layout.addWidget(self.align_group)
        self.text_control_layout.addStretch()

        # -------------------------|new window UI|------------------------- #
        self.layout = QVBoxLayout()
        self.default_format = QTextCharFormat()
        self.default_format.setFontPointSize(20)

        self.status_label = QLabel(f"Adding cards to deck: {self.deck_name}")
        self.status_label.setContentsMargins(0, 0, 0, 20)
        self.status_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.status_label.setStyleSheet("font-size: 25px")
        self.layout.addWidget(self.status_label)

        self.layout.addWidget(self.toolbar_container)

        self.front_input = FlashcardTextEdit("front", self.handle_focus_change)
        # self.front_input.setAlignment(Qt.AlignCenter)
        self.front_input.setCurrentCharFormat(self.default_format)
        self.front_input.setPlaceholderText("Front of the card."
                                            " Supports drag and dropping images."
                                            " One image per card side."
                                            " Supported formats: .png, .jpg, .jpeg, .bmp")

        self.front_label = QLabel("Front")
        self.front_label.setContentsMargins(5, 0, 0, 0)
        self.layout.addWidget(self.front_label)
        self.layout.addWidget(self.front_input)

        self.back_input = FlashcardTextEdit("back", self.handle_focus_change)
        # self.back_input.setAlignment(Qt.AlignCenter)
        self.back_input.setCurrentCharFormat(self.default_format)
        self.back_input.setPlaceholderText("Back of the card."
                                           " Supports drag and dropping images."
                                           " One image per card side."
                                           " Supported formats: .png, .jpg, .jpeg, .bmp")

        self.back_label = QLabel("Back")
        self.back_label.setContentsMargins(5, 0, 0, 0)
        self.layout.addWidget(self.back_label)
        self.layout.addWidget(self.back_input)

        self.add_button = QPushButton("Add Card")
        self.add_button.clicked.connect(self.add_card)
        self.layout.addWidget(self.add_button)

        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.close_clicked)
        self.layout.addWidget(self.close_button)

        self.setLayout(self.layout)

        # -------------------------|connecting the font controls|------------------------- #
        self.font_combobox.activated.connect(self.font_selected)
        self.font_size_combobox.activated.connect(self.font_size_changed)
        self.button_bold.pressed.connect(self.bold_clicked)
        self.button_italic.pressed.connect(self.italics_clicked)
        self.button_underline.pressed.connect(self.underline_clicked)
        self.front_input.textChanged.connect(self.handle_text_changed)
        self.back_input.textChanged.connect(self.handle_text_changed)
        self.button_align_right.pressed.connect(self.alignment_clicked)
        self.button_align_center.pressed.connect(self.alignment_clicked)
        self.button_align_left.pressed.connect(self.alignment_clicked)

        # -------------------------|connecting the method to apply the correct style|------------------------- #
        self.front_input.cursorPositionChanged.connect(lambda: self.reset_typing_format(self.front_input))
        self.back_input.cursorPositionChanged.connect(lambda: self.reset_typing_format(self.back_input))

    def add_card(self):
        front = self.front_input.toPlainText().strip()
        back = self.back_input.toPlainText().strip()

        if not front or not back:
            QMessageBox.warning(self, "Missing Fields", "Both front and back must be filled.")
            return

        image_path = self.database_manager.image_folder_path

        front_html = self.front_input.finalize_images(image_path)
        back_html = self.back_input.finalize_images(image_path)

        front_image_path = self.front_input.image_filename if self.front_input.image_filename else None
        back_image_path = self.back_input.image_filename if self.back_input.image_filename else None

        self.database_manager.add_card(self.deck_id, front_html, back_html, front_image_path, back_image_path)
        self.status_label.setText("Card Added!")
        self.card_added.emit()
        QTimer.singleShot(1500, lambda: self.status_label.setText(f"Adding cards to deck: {self.deck_name}"))
        self.front_input.clear()
        self.back_input.clear()

        self.front_input.setCurrentCharFormat(self.default_format)
        self.back_input.setCurrentCharFormat(self.default_format)

    def close_clicked(self):
        self.card_added.emit()
        self.close()

    # ---------------|method to change font to selected text, otherwise set new cursor font|---------------- #
    def font_selected(self):
        font_family = self.font_combobox.currentText()
        font_format = QTextCharFormat()
        font_format.setFontFamily(font_family)
        font_format.setFontPointSize(float(self.font_size_combobox.currentText()))  # ensure size is preserved

        for editor in [self.front_input, self.back_input]:
            cursor = editor.textCursor()
            if cursor.hasSelection():
                cursor.mergeCharFormat(font_format)
                editor.setTextCursor(cursor)
            else:
                editor.setCurrentCharFormat(font_format)

    # ---------------|method to change font size to selected text, otherwise set new cursor size|---------------- #
    def font_size_changed(self, index):
        size = float(self.font_size_combobox.itemText(index))
        font_size_format = QTextCharFormat()
        font_size_format.setFontPointSize(size)

        any_selection = False

        for editor in [self.front_input, self.back_input]:
            cursor = editor.textCursor()
            if cursor.hasSelection():
                cursor.mergeCharFormat(font_size_format)
                editor.setTextCursor(cursor)
                any_selection = True

        if not any_selection:
            for editor in [self.front_input, self.back_input]:
                editor.setCurrentCharFormat(font_size_format)

    def bold_clicked(self):
        for editor in [self.front_input, self.back_input]:
            cursor = editor.textCursor()
            if cursor.hasSelection():
                start = cursor.selectionStart()
                end = cursor.selectionEnd()
                midpoint = start + (end - start) // 2

                temp_cursor = QTextCursor(editor.document())
                temp_cursor.setPosition(midpoint)
                mid_weight = temp_cursor.charFormat().fontWeight()

                new_weight = QFont.Normal if mid_weight == QFont.Bold else QFont.Bold
                bold_format = QTextCharFormat()
                bold_format.setFontWeight(new_weight)

                cursor.mergeCharFormat(bold_format)
                editor.setTextCursor(cursor)

                cursor.setPosition(end)
                editor.setTextCursor(cursor)

                # ---------------|reset cursor to not be bold anymore|---------------- #
                reset_format = QTextCharFormat()
                reset_format.setFontPointSize(editor.fontPointSize())
                reset_format.setFontFamily(self.font_combobox.currentText())
                reset_format.setFontWeight(QFont.Normal)

                editor.setCurrentCharFormat(reset_format)

    def italics_clicked(self):
        for editor in [self.front_input, self.back_input]:
            cursor = editor.textCursor()
            if cursor.hasSelection():
                start = cursor.selectionStart()
                end = cursor.selectionEnd()
                midpoint = start + (end - start) // 2

                temp_cursor = QTextCursor(editor.document())
                temp_cursor.setPosition(midpoint)
                mid_italic = temp_cursor.charFormat().fontItalic()

                new_italic = not mid_italic

                italic_format = QTextCharFormat()
                italic_format.setFontItalic(new_italic)

                cursor.mergeCharFormat(italic_format)
                editor.setTextCursor(cursor)

                cursor.setPosition(end)
                editor.setTextCursor(cursor)

                # ---------------|reset cursor to not be italic anymore|---------------- #
                reset_format = QTextCharFormat()
                reset_format.setFontPointSize(editor.fontPointSize())
                reset_format.setFontFamily(self.font_combobox.currentText())
                reset_format.setFontItalic(False)

                editor.setCurrentCharFormat(reset_format)

    def underline_clicked(self):
        for editor in [self.front_input, self.back_input]:
            cursor = editor.textCursor()
            if cursor.hasSelection():
                start = cursor.selectionStart()
                end = cursor.selectionEnd()
                midpoint = start + (end - start) // 2

                temp_cursor = QTextCursor(editor.document())
                temp_cursor.setPosition(midpoint)
                mid_underline = temp_cursor.charFormat().fontUnderline()

                new_underline = not mid_underline

                underline_format = QTextCharFormat()
                underline_format.setFontUnderline(new_underline)

                cursor.mergeCharFormat(underline_format)
                editor.setTextCursor(cursor)

                cursor.setPosition(end)
                editor.setTextCursor(cursor)

                # ---------------|reset cursor to not be underline anymore|---------------- #
                reset_format = QTextCharFormat()
                reset_format.setFontPointSize(editor.fontPointSize())
                reset_format.setFontFamily(self.font_combobox.currentText())
                reset_format.setFontUnderline(False)

                editor.setCurrentCharFormat(reset_format)

    # -----------------|method to make sure font size setting stays even if all text is deleted|--------------------- #
    def handle_text_changed(self):
        size = float(self.font_size_combobox.currentText())
        text_format = QTextCharFormat()
        text_format.setFontPointSize(size)
        text_format.setFontFamily(self.font_combobox.currentText())

        for editor in [self.front_input, self.back_input]:
            if editor.toPlainText() == "":
                cursor = editor.textCursor()
                cursor.setCharFormat(text_format)
                editor.setTextCursor(cursor)

    # ---------------| method that handles alignment buttons |--------------- #
    def alignment_clicked(self):
        clicked_button = self.sender()
        alignment = clicked_button.text()

        if alignment == "Left":
            align_flag = Qt.AlignLeft
        elif alignment == "Center":
            align_flag = Qt.AlignCenter
        elif alignment == "Right":
            align_flag = Qt.AlignRight
        else:
            return

        for editor in [self.front_input, self.back_input]:
            editor.selectAll()
            editor.setAlignment(align_flag)
            editor.moveCursor(QTextCursor.End)

    # ---------------| method that handles clearing of selected text |--------------- #
    def handle_focus_change(self, focused_editor):
        if focused_editor == self.front_input:
            other_editor = self.back_input
        else:
            other_editor = self.front_input

        other_cursor = other_editor.textCursor()
        if other_cursor.hasSelection():
            other_cursor.clearSelection()
            other_editor.setTextCursor(other_cursor)

    # --------| method that resets the cursor if the user types after text that has a style applied|------------- #
    def reset_typing_format(self, editor):
        cursor = editor.textCursor()
        if not cursor.hasSelection():
            char_format = cursor.charFormat()

            clean_format = QTextCharFormat()
            clean_format.setFontPointSize(float(self.font_size_combobox.currentText()))
            clean_format.setFontFamily(self.font_combobox.currentText())

            if char_format.fontWeight() == QFont.Bold or char_format.fontItalic() or char_format.fontUnderline():
                clean_format.setFontWeight(QFont.Normal)
                clean_format.setFontItalic(False)
                clean_format.setFontUnderline(False)

            editor.setCurrentCharFormat(clean_format)
