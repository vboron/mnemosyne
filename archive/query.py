import sqlite3
from archive.config import get_db_path


def list_discs():
    conn = sqlite3.connect(get_db_path())
    cur = conn.cursor()

    cur.execute(
        """
        SELECT accession_code, title, artist, year, archive_date
        FROM physical_discs
        ORDER BY id
        """
    )

    rows = cur.fetchall()
    conn.close()
    return rows


def search_discs(term):
    conn = sqlite3.connect(get_db_path())
    cur = conn.cursor()

    pattern = f"%{term}%"

    cur.execute(
        """
        SELECT accession_code, title, artist, year, archive_date
        FROM physical_discs
        WHERE title LIKE ?
           OR artist LIKE ?
           OR accession_code LIKE ?
        ORDER BY id
        """,
        (pattern, pattern, pattern),
    )

    rows = cur.fetchall()
    conn.close()
    return rows


if __name__ == "__main__":
    for row in list_discs():
        accession, title, artist, year, archive_date = row
        print(f"{accession} | {artist} — {title} | {year} | {archive_date}")
