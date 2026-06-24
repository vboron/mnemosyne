import sqlite3
from datetime import datetime

from archive.config import get_db_path, get_vault_discs


def next_accession(conn):
    cur = conn.cursor()

    cur.execute(
        """
        UPDATE counters
        SET value = value + 1
        WHERE name = 'cd_accession'
        """
    )

    cur.execute(
        """
        SELECT value
        FROM counters
        WHERE name = 'cd_accession'
        """
    )

    number = cur.fetchone()[0]
    return f"VB-CD-{number:06d}"


def register_disc(title, artist, year=None):
    vault_discs = get_vault_discs()
    vault_discs.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(get_db_path())

    try:
        accession = next_accession(conn)
        disc_folder = vault_discs / accession
        disc_folder.mkdir(exist_ok=False)

        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO physical_discs
            (accession_code, title, artist, year, archive_date)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                accession,
                title,
                artist,
                year,
                datetime.now().isoformat(),
            ),
        )

        conn.commit()
        print(f"Registered {accession}")
        print(f"Created vault folder: {disc_folder}")

        return accession

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


if __name__ == "__main__":
    register_disc(
        title="Mnemosyne Prototype Disc",
        artist="System",
    )