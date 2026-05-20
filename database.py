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

def generate_referral_code(user_id: int) -> str:
    return f"ref_{user_id}"

def get_referral_link(user_id: int, bot_username: str):
    code = generate_referral_code(user_id)
    return f"https://t.me/{bot_username}?start={code}"


def create_table_users():
    with get_connection() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users(
                id INTEGER PRIMARY KEY,
                fullname TEXT NOT NULL,
                username TEXT UNIQUE,
                user_id INTEGER NOT NULL UNIQUE,
                ai_count INTEGER DEFAULT 0,
                referral_code TEXT UNIQUE,
                referred_by INTEGER DEFAULT NULL
            )
        ''')


def add_user(fullname, username, user_id, referred_by=None):
    try:
        referral_code = generate_referral_code(user_id)

        with get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO users(
                    fullname,
                    username,
                    user_id,
                    referral_code,
                    referred_by
                )
                VALUES (?, ?, ?, ?, ?)
            """, (
                fullname,
                username,
                user_id,
                referral_code,
                referred_by
            ))

            # referral bonus
            if referred_by:
                conn.execute("""
                    UPDATE users
                    SET ai_count = 0
                    WHERE user_id = ?
                """, (referred_by,))

            return cursor.lastrowid

    except sqlite3.IntegrityError:
        return None


def increment_ai_count(user_id: int) -> bool:
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE users
            SET ai_count = ai_count + 1
            WHERE user_id = ?
        """, (user_id,))

        cursor.execute("""
            SELECT ai_count
            FROM users
            WHERE user_id = ?
        """, (user_id,))

        result = cursor.fetchone()

        # user topilmasa
        if result is None:
            return False

        count = result[0]

        return count >= 10


def check_user(telegram_id: int) -> bool:
    with get_connection() as conn:
        cursor = conn.execute(
            "SELECT 1 FROM users WHERE user_id = ? LIMIT 1",
            (telegram_id,)
        )
        return cursor.fetchone() is not None
