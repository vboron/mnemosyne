import sqlite3
import subprocess

from archive.config import get_db_path
from memory.session import create_session


def play_track(term):
    conn = sqlite3.connect(get_db_path())
    cur = conn.cursor()

    cur.execute(
        """
        SELECT id, title, artist, flac_path
        FROM tracks
        WHERE title LIKE ?
          AND flac_path IS NOT NULL
        ORDER BY id
        LIMIT 1
        """,
        (f"%{term}%",),
    )

    row = cur.fetchone()
    conn.close()

    if row is None:
        raise ValueError(f"No playable track found for: {term}")

    track_id, title, artist, flac_path = row

    session_id = create_session(
        track_id=track_id,
        mode="listen",
    )

    print(f"Playing: {artist or 'Unknown'} — {title}")
    print(f"Session: {session_id}")

    subprocess.run(
        ["cvlc", "--play-and-exit", flac_path],
        check=False,
    )

    return session_id