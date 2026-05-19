import sqlite3
from contextlib import contextmanager


@contextmanager
def get_connection():
    conn = sqlite3.connect("aibot.db")
    try:
        yield conn
        conn.commit()
    except sqlite3.Error as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def create_table_users():
    with get_connection() as conn:
        cursor = conn.execute('''
            CREATE TABLE IF NOT EXISTS users(
                id INTEGER PRIMARY KEY,
                fullname TEXT NOT NULL,
                username TEXT UNIQUE,
                user_id INTEGER NOT NULL UNIQUE,
                ai_count INTEGER DEFAULT 0
            )
        ''')
        return cursor


def add_user(fullname, username, user_id):
    try:
        with get_connection() as conn:
            cursor = conn.execute('''
                INSERT INTO users(fullname, username, user_id) VALUES(?,?,?)''',
                                  (fullname, username, user_id))
            return cursor.lastrowid
    except sqlite3.IntegrityError as e:
        return ValueError(f"Integer xatoligi: {e}")


def increment_ai_count(user_id: int) -> bool:
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE users
            SET ai_count = ai_count + 1
            WHERE user_id = ?
        """, (user_id,))

        conn.commit()

        cursor.execute(
            "SELECT ai_count FROM users WHERE user_id = ?",
            (user_id,)
        )
        count = cursor.fetchone()[0]

        return count >= 10


def check_user(telegram_id: int) -> bool:
    with get_connection() as conn:
        cursor = conn.execute(
            "SELECT 1 FROM users WHERE user_id = ? LIMIT 1",
            (telegram_id,)
        )
        return cursor.fetchone() is not None
