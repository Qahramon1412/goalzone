import psycopg

from config import DB_HOST, DB_NAME, DB_PASSWORD, DB_USER


def _connect():
    return psycopg.connect(
        host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD
    )


def save_user(telegram_id, username):
    with _connect() as conn:
        conn.execute(
            "INSERT INTO users (telegram_id, username) VALUES (%s, %s) "
            "ON CONFLICT (telegram_id) DO UPDATE SET username = EXCLUDED.username",
            (telegram_id, username),
        )


def get_user(telegram_id):
    with _connect() as conn:
        row = conn.execute(
            "SELECT telegram_id, username, favorite_team FROM users "
            "WHERE telegram_id = %s",
            (telegram_id,),
        ).fetchone()
    return row
