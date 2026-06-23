import sqlite3
from datetime import datetime

DB_PATH = "../database/mnemosyne.db"


def next_accession():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM physical_discs")
    count = cur.fetchone()[0] + 1

    conn.close()

    return f"VB-CD-{count:06d}"


accession = next_accession()

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.execute(
    """
    INSERT INTO physical_discs
    (accession_code, title, artist, archive_date)
    VALUES (?, ?, ?, ?)
    """,
    (
        accession,
        "Mnemosyne Prototype Disc",
        "System",
        datetime.now().isoformat()
    )
)

conn.commit()
conn.close()

print(f"Registered {accession}")
