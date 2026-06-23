from pathlib import Path
import sqlite3
from archive.config import DB_PATH

def register_track(
    album_id,
    title,
    track_number=None,
    duration_seconds=None,
    flac_path=None,
):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute(
        """
        SELECT id
        FROM albums
        WHERE id = ?
        """,
        (album_id,),
    )

    if cur.fetchone() is None:
        conn.close()
        raise ValueError(f"No album found with id: {album_id}")

    cur.execute(
        """
        INSERT INTO tracks
        (album_id, title, track_number, duration_seconds, flac_path)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            album_id,
            title,
            track_number,
            duration_seconds,
            flac_path,
        ),
    )

    track_id = cur.lastrowid

    conn.commit()
    conn.close()

    return track_id

