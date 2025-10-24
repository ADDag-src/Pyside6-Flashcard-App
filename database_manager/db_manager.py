import os
import sqlite3


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
        self.cursor = self.connection.cursor()
        self.database_init()

    def database_init(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS decks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                created TEXT DEFAULT CURRENT_TIMESTAMP,
                total_cards INTEGER NOT NULL DEFAULT 0,
                learn_cards INTEGER NOT NULL DEFAULT 0,
                due_cards INTEGER NOT NULL DEFAULT 0
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS cards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                deck_id INTEGER NOT NULL,
                front TEXT NOT NULL,
                back TEXT NOT NULL,
                image_path TEXT,
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
