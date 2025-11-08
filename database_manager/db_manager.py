import os
import sqlite3
from datetime import datetime


class DBManager:
    def __init__(self):
        base_dir = os.path.dirname(os.path.dirname(__file__))
        data_dir = os.path.join(base_dir, "data")
        os.makedirs(data_dir, exist_ok=True)
        image_folder_dir = os.path.join(data_dir, "images")
        os.makedirs(image_folder_dir, exist_ok=True)

        self.db_path = os.path.join(data_dir, "flashcard_app.db")
        self.image_folder_path = image_folder_dir
        self.connection = sqlite3.connect(self.db_path)
        self.connection.execute("PRAGMA foreign_keys = ON")
        self.cursor = self.connection.cursor()
        self.database_init()

    def database_init(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS decks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                created TEXT DEFAULT CURRENT_TIMESTAMP,
                total_cards INTEGER NOT NULL DEFAULT 0,
                new_cards INTEGER NOT NULL DEFAULT 0,
                due_cards INTEGER NOT NULL DEFAULT 0
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS cards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                deck_id INTEGER NOT NULL,
                front TEXT NOT NULL,
                back TEXT NOT NULL,
                front_image_filename TEXT,
                back_image_filename  TEXT,
                status TEXT NOT NULL DEFAULT 'new',
                next_review TEXT,
                review_stage INTEGER DEFAULT 0,
                created TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(deck_id) REFERENCES decks(id) ON DELETE CASCADE
            )
        """)

    def add_deck(self, name):
        self.cursor.execute("INSERT INTO decks (name) VALUES (?)", (name,))
        self.connection.commit()

    def del_deck(self, deck_id):
        self.cursor.execute("DELETE FROM decks WHERE id = ?", (deck_id,))
        self.connection.commit()

    def check_existing(self, name):
        self.cursor.execute("SELECT 1 FROM decks WHERE name = ? LIMIT 1", (name,))
        return bool(self.cursor.fetchone())

    def get_all_decks(self):
        self.cursor.execute("SELECT * FROM decks ORDER BY name ASC")
        return self.cursor.fetchall()

    def get_deck_id_by_name(self, name):
        self.cursor.execute("SELECT id FROM decks WHERE name = ?", (name,))
        result = self.cursor.fetchone()
        if result:
            return result[0]

    def update_deck_stats(self, deck_id):
        self.cursor.execute("SELECT status, next_review FROM cards WHERE deck_id = ?", (deck_id,))
        results = self.cursor.fetchall()
        total_cards = len(results)
        new_cards = 0
        due_cards = 0
        now = datetime.now()

        for status, next_review in results:
            if status == "new":
                new_cards += 1
            if next_review:
                try:
                    review_time = datetime.fromisoformat(next_review)
                    if review_time <= now:
                        due_cards += 1
                except ValueError:
                    pass

        self.cursor.execute(
            """
            UPDATE decks
            SET total_cards = ?, new_cards = ?, due_cards = ?
            WHERE id = ?
            """,
            (total_cards, new_cards, due_cards, deck_id)
        )
        self.connection.commit()

    def add_card(self, deck_id, front, back, front_image_filename=None, back_image_filename=None):
        now = datetime.now().isoformat()
        self.cursor.execute(
            """
            INSERT INTO cards (deck_id, front, back, front_image_filename, back_image_filename, status, review_stage, next_review, created)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (deck_id, front, back, front_image_filename, back_image_filename, 'new', 0, None, now)
        )
        self.connection.commit()
        self.update_deck_stats(deck_id)

    def rename_deck(self, new_name, deck_id):
        self.cursor.execute("UPDATE decks SET name = ? WHERE id = ?", (new_name, deck_id))
        self.connection.commit()

    def get_deck_cards(self, deck_id):
        self.cursor.execute("SELECT id, front, back, front_image_filename, back_image_filename, created FROM cards WHERE deck_id = ?", (deck_id,))
        return self.cursor.fetchall()

    def delete_cards(self, deck_id, card_ids):
        if not card_ids:
            return
        self.cursor.executemany("DELETE FROM cards where id=?", [(card_id,) for card_id in card_ids])
        self.connection.commit()
        self.update_deck_stats(deck_id)
