import sqlite3
from datetime import datetime

class ChatDatabase:
    def __init__(self):
        self.conn = sqlite3.connect('chat_history.db')
        # Drop and recreate the table to include the new session column
        self.reset_database()

    def reset_database(self):
        cursor = self.conn.cursor()
        # Drop the table if it exists
        cursor.execute('DROP TABLE IF EXISTS conversations')
        # Create the table with the session column
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                model TEXT,
                user_message TEXT,
                ai_response TEXT,
                session TEXT DEFAULT 'Default'
            )
        ''')
        self.conn.commit()

    def save_conversation(self, model, user_message, ai_response, session='Default'):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO conversations (timestamp, model, user_message, ai_response, session)
            VALUES (?, ?, ?, ?, ?)
        ''', (datetime.now().isoformat(), model, user_message, ai_response, session))
        self.conn.commit()

    def get_recent_conversations(self, session='Default', limit=50):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM conversations 
            WHERE session = ?
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (session, limit))
        return cursor.fetchall()

    def search_conversations(self, query, session='Default'):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM conversations 
            WHERE session = ? AND (
                user_message LIKE ? OR 
                ai_response LIKE ?
            )
            ORDER BY timestamp DESC
        ''', (session, f'%{query}%', f'%{query}%'))
        return cursor.fetchall()

    def clear_history(self):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM conversations')
        self.conn.commit()
