import sqlite3
from datetime import datetime

from archive.config import get_db_path


def register_photo(memory_id, photo_type, file_path):
    conn = sqlite3.connect(get_db_path())
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO photos
        (memory_id, type, file_path, captured_at)
        VALUES (?, ?, ?, ?)
        """,
        (memory_id, photo_type, file_path, datetime.now().isoformat()),
    )

    photo_id = cur.lastrowid
    conn.commit()
    conn.close()

    return photo_id