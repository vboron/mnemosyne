import sqlite3
from datetime import datetime
from archive.config import get_db_path


def next_mix_code(conn):
    cur = conn.cursor()

    cur.execute("""
        UPDATE counters
        SET value = value + 1
        WHERE name = 'mixtape'
    """)

    cur.execute("""
        SELECT value
        FROM counters
        WHERE name = 'mixtape'
    """)

    number = cur.fetchone()[0]
    return f"VB-MIX-{number:06d}"


def create_mixtape(title, reason=None, liner_notes=None):
    conn = sqlite3.connect(get_db_path())

    try:
        mix_code = next_mix_code(conn)
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO mixtapes
            (mix_code, title, created_at, reason, liner_notes)
            VALUES (?, ?, ?, ?, ?)
        """, (
            mix_code,
            title,
            datetime.now().isoformat(),
            reason,
            liner_notes,
        ))

        conn.commit()
        return mix_code

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


def add_track_to_mixtape(mix_code, track_id):
    conn = sqlite3.connect(get_db_path())
    cur = conn.cursor()

    cur.execute("SELECT id FROM mixtapes WHERE mix_code = ?", (mix_code,))
    row = cur.fetchone()

    if row is None:
        conn.close()
        raise ValueError(f"No mixtape found: {mix_code}")

    mixtape_id = row[0]

    cur.execute("""
        SELECT COALESCE(MAX(track_order), 0) + 1
        FROM mixtape_tracks
        WHERE mixtape_id = ?
    """, (mixtape_id,))

    track_order = cur.fetchone()[0]

    cur.execute("""
        INSERT INTO mixtape_tracks
        (mixtape_id, track_id, track_order)
        VALUES (?, ?, ?)
    """, (mixtape_id, track_id, track_order))

    conn.commit()
    conn.close()

    return track_order