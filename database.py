import sqlite3
from datetime import datetime

class ChatDatabase:
    def __init__(self):
        self.conn = sqlite3.connect('chat_history.db')
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                model TEXT,
                user_message TEXT,
                ai_response TEXT
            )
        ''')
        self.conn.commit()

    def save_conversation(self, model, user_message, ai_response):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO conversations (timestamp, model, user_message, ai_response)
            VALUES (?, ?, ?, ?)
        ''', (datetime.now().isoformat(), model, user_message, ai_response))
        self.conn.commit()

    def get_recent_conversations(self, limit=50):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM conversations 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (limit,))
        return cursor.fetchall()

    def clear_history(self):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM conversations')
        self.conn.commit()
