from PySide6.QtGui import QStandardItemModel, QStandardItem, QTextDocument
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QSizePolicy, QPushButton, QMessageBox,
                               QHBoxLayout, QTableView, QAbstractItemView, QInputDialog, QHeaderView, QDialog,
                               QTextBrowser)
from PySide6.QtCore import Qt, Signal, QTimer, QModelIndex, QUrl
from datetime import datetime
import re
import os
from windows.card_editor_window import CardEditorWindow


class EditDeckWindow(QWidget):
    # ---------------| Custom signal to update list in main window |--------------- #
    deck_edited = Signal()

    def __init__(self, deck_name, deck_id, database_manager):
        super().__init__()
        self.setWindowModality(Qt.ApplicationModal)
        self.deck_id = deck_id
        self.deck_name = deck_name
        self.editor = None
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
        self.card_list.setSelectionBehavior(QAbstractItemView.SelectItems)
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

        # -------------------------|edit button|------------------------- #
        self.edit_button = QPushButton("Edit selected card")
        self.edit_button.setMaximumWidth(200)
        self.edit_button.setStyleSheet("""
                               QPushButton {
                                   color: white;
                                   background-color: #1e5bbf;
                                   font-size: 15px;
                               }
                               QPushButton:hover {
                                   background-color: #5ab0ff;
                               }
                           """)
        self.button_layout.addWidget(self.edit_button)
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
        self.edit_button.clicked.connect(self.edit_clicked)

    # -------------------------|cell click connection|------------------------- #
        self.card_list.clicked.connect(self.cell_click_handler)

    @staticmethod
    def html_to_plaintext(html_string):
        html_string = re.sub(r"<img[^>]*>", "Image detected — click cell for preview", html_string, flags=re.IGNORECASE)
        doc = QTextDocument()
        doc.setHtml(html_string)
        plain = doc.toPlainText()
        return plain.replace("\u00A0", " ").replace("\n", " ").strip()

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

    # -------------------------|method to refresh or populate card list|------------------------- #
    def refresh_card_list(self):
        cards = self.database_manager.get_deck_cards(self.deck_id)
        header = self.card_list.horizontalHeader()
        header.setSectionsClickable(False)
        header.setHighlightSections(False)

        if cards:
            model = QStandardItemModel(len(cards), 4)
            model.setHorizontalHeaderLabels(["Select", "Front", "Back", "Created"])
            for row, (card_id, front, back, front_img, back_img, created) in enumerate(cards):

                checkbox_item = QStandardItem(" ")
                checkbox_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
                checkbox_item.setCheckState(Qt.Unchecked)
                checkbox_item.setData(card_id, Qt.UserRole)

                front_text = self.html_to_plaintext(front)
                back_text = self.html_to_plaintext(back)

                front_item = QStandardItem(front_text)
                front_item.setToolTip("Click to preview front side")
                front_item.setData(front, Qt.UserRole + 1)
                front_item.setData(front_img, Qt.UserRole + 2)

                back_item = QStandardItem(back_text)
                back_item.setToolTip("Click to preview back side")
                back_item.setData(back, Qt.UserRole + 1)
                back_item.setData(back_img, Qt.UserRole + 2)

                creation_dt = datetime.strptime(created, "%Y-%m-%dT%H:%M:%S.%f")
                formatted_time = creation_dt.strftime("%b %d, %Y %H:%M")
                items = [
                    checkbox_item,
                    front_item,
                    back_item,
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
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)

    # -------------------------|method to delete cards|------------------------- #
    def delete_cards(self):
        model = self.card_list.model()
        card_ids_to_delete = []

        for row in range(model.rowCount()):
            current_checkbox = model.item(row, 0)  # type: ignore
            if current_checkbox.checkState() == Qt.Checked:
                card_id = current_checkbox.data(Qt.UserRole)
                if card_id:
                    card_ids_to_delete.append(card_id)

        if not card_ids_to_delete:
            QMessageBox.information(self, "Delete Cards", "No cards selected for deletion.")
            return

        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Delete {len(card_ids_to_delete)} selected card(s)?\n !This can not be undone!",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            self.database_manager.delete_cards(self.deck_id, card_ids_to_delete)
            self.refresh_card_list()
            self.deck_name_label.setText("Cards deleted!")
            self.deck_edited.emit()
            QTimer.singleShot(1500, lambda: self.deck_name_label.setText(f"Editing deck: {self.deck_name}"))

    # -------------------------|method to handle cell preview, when clicked|------------------------- #
    def cell_click_handler(self, index: QModelIndex):
        item = self.card_list.model().itemFromIndex(index)  # type: ignore
        html = item.data(Qt.UserRole + 1)
        image_filename = item.data(Qt.UserRole + 2)

        if not html:
            return

        if image_filename:
            image_path = os.path.join(self.database_manager.image_folder_path, image_filename)
            if os.path.exists(image_path):
                image_url = QUrl.fromLocalFile(image_path).toString()
                html = html.replace(image_filename, image_url)
            else:
                html += f"<p><i>Image file '{image_filename}' not found</i></p>"

        dialog = QDialog(self)
        dialog.setWindowTitle("Card Preview")
        dialog.setWindowFlags(Qt.Window | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)
        layout = QVBoxLayout(dialog)

        viewer = QTextBrowser()
        viewer.setHtml(html)
        viewer.setOpenExternalLinks(True)
        layout.addWidget(viewer)

        dialog.setLayout(layout)
        dialog.resize(500, 400)
        dialog.exec()

    def edit_clicked(self):
        model = self.card_list.model()
        selected_card_ids = []

        for row in range(model.rowCount()):
            checkbox_item = model.item(row, 0)  # type: ignore
            if checkbox_item.checkState() == Qt.Checked:
                card_id = checkbox_item.data(Qt.UserRole)
                if card_id:
                    selected_card_ids.append(row)

        if not selected_card_ids:
            QMessageBox.warning(self, "No Selection", "Please check a card to edit.")
            return

        if len(selected_card_ids) > 1:
            QMessageBox.information(self, "Multiple Selection", "Please select only one card to edit at a time.")
            return

        row = selected_card_ids[0]

        card_id_item = model.item(row, 0)  # type: ignore
        card_id = card_id_item.data(Qt.UserRole)

        front_item = model.item(row, 1)  # type: ignore
        back_item = model.item(row, 2)   # type: ignore

        front_html = front_item.data(Qt.UserRole + 1)
        front_image = front_item.data(Qt.UserRole + 2)

        back_html = back_item.data(Qt.UserRole + 1)
        back_image = back_item.data(Qt.UserRole + 2)

        editor = CardEditorWindow(
            self.deck_name,
            self.deck_id,
            self.database_manager,
            card_id=card_id,
            front_html=front_html,
            back_html=back_html,
            front_image=front_image,
            back_image=back_image
        )
        editor.card_edited.connect(self.refresh_card_list)
        editor.show()
