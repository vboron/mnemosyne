import sqlite3
from datetime import datetime

from archive.config import DB_PATH


def create_session(album_id=None, track_id=None, mode="listen"):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO listening_sessions
        (album_id, track_id, started_at, mode)
        VALUES (?, ?, ?, ?)
        """,
        (album_id, track_id, datetime.now().isoformat(), mode),
    )

    session_id = cur.lastrowid
    conn.commit()
    conn.close()

    return session_id


def end_session(session_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute(
        """
        UPDATE listening_sessions
        SET ended_at = ?
        WHERE id = ?
        """,
        (datetime.now().isoformat(), session_id),
    )

    conn.commit()
    conn.close()
