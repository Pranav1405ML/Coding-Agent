import sqlite3
import json
from datetime import datetime

def init_db():
    connection = sqlite3.connect("chat_history.db")
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            role TEXT,
            content TEXT,
            timestamp TEXT
        )
    """)
    connection.commit()
    connection.close()

def save_message(user_id, role, content):
    connection = sqlite3.connect("chat_history.db")
    cursor = connection.cursor()

    try:
        content_json = json.dumps(content)
        timestamp = datetime.now().isoformat()

        cursor.execute(
            "INSERT INTO history (user_id, role, content, timestamp) VALUES (?, ?, ?, ?)",
            (user_id, role, content_json, timestamp)
        )

        connection.commit()
        return True, None

    except (sqlite3.Error, TypeError, ValueError) as e:
        return False, f"Failed to save the message for {user_id}: {e}"

    finally:
        connection.close()

def load_history(user_id):
    connection = sqlite3.connect("chat_history.db")
    cursor = connection.cursor()

    try:
        cursor.execute(
            "SELECT * FROM history WHERE user_id = ? ORDER BY timestamp",
            (user_id,)
        )
        rows = cursor.fetchall()
        reconstructed = []

        for row in rows:
            temp_dict = {}
            temp_dict['role'] = row[2]
            content = json.loads(row[3])
            temp_dict['parts'] = content
            reconstructed.append(temp_dict)

        return reconstructed

    except sqlite3.Error as e:
        print(f"Database error occurred: {e}")
        return []

    finally:
        # No need to commit anything as no change has been made
        connection.close()

