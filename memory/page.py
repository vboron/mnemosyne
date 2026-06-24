import sqlite3
from datetime import datetime

from archive.config import get_db_path


def create_memory_page(
    session_id,
    journal=None,
    tags=None,
    location_name=None,
    weather=None,
):
    tags = tags or []

    conn = sqlite3.connect(get_db_path())
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO memory_pages
        (session_id, created_at, journal, location_name, weather)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            session_id,
            datetime.now().isoformat(),
            journal,
            location_name,
            weather,
        ),
    )

    memory_id = cur.lastrowid

    for tag in tags:
        clean_tag = tag.strip()

        if not clean_tag:
            continue

        cur.execute(
            """
            INSERT OR IGNORE INTO tags (name)
            VALUES (?)
            """,
            (clean_tag,),
        )

        cur.execute(
            """
            SELECT id FROM tags WHERE name = ?
            """,
            (clean_tag,),
        )

        tag_id = cur.fetchone()[0]

        cur.execute(
            """
            INSERT OR IGNORE INTO memory_tags
            (memory_id, tag_id)
            VALUES (?, ?)
            """,
            (memory_id, tag_id),
        )

    conn.commit()
    conn.close()

    return memory_id
