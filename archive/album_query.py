import sqlite3

from archive.config import get_db_path


def list_albums():
    conn = sqlite3.connect(get_db_path())
    cur = conn.cursor()

    cur.execute(
        """
        SELECT albums.id,
               albums.title,
               albums.artist,
               physical_discs.accession_code
        FROM albums
        JOIN physical_discs
            ON albums.disc_id = physical_discs.id
        ORDER BY albums.artist, albums.title
        """
    )

    rows = cur.fetchall()
    conn.close()

    return rows


def show_disc(accession):
    conn = sqlite3.connect(get_db_path())
    cur = conn.cursor()

    cur.execute(
        """
        SELECT id, title, artist, year
        FROM physical_discs
        WHERE accession_code = ?
        """,
        (accession,),
    )

    disc = cur.fetchone()

    if disc is None:
        conn.close()
        return None

    disc_id = disc[0]

    cur.execute(
        """
        SELECT title, artist, year
        FROM albums
        WHERE disc_id = ?
        """,
        (disc_id,),
    )

    album = cur.fetchone()

    cur.execute(
    """
    SELECT tracks.track_number, tracks.title, tracks.artist
    FROM tracks
    JOIN albums
        ON tracks.album_id = albums.id
    WHERE albums.disc_id = ?
    ORDER BY tracks.track_number
    """,
    (disc_id,),
)

    tracks = cur.fetchall()

    conn.close()

    return {
        "disc": disc,
        "album": album,
        "tracks": tracks,
    }