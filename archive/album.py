from pathlib import Path
import sqlite3
from archive.config import DB_PATH

def register_album(disc_accession, title, artist=None, year=None):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute(
        """
        SELECT id
        FROM physical_discs
        WHERE accession_code = ?
        """,
        (disc_accession,),
    )

    row = cur.fetchone()

    if row is None:
        conn.close()
        raise ValueError(f"No disc found with accession code: {disc_accession}")

    disc_id = row[0]

    cur.execute(
        """
        INSERT INTO albums
        (disc_id, title, artist, year)
        VALUES (?, ?, ?, ?)
        """,
        (disc_id, title, artist, year),
    )

    album_id = cur.lastrowid

    conn.commit()
    conn.close()

    return album_id

