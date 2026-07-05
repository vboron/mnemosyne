import sqlite3
from archive.config import get_db_path


def rich_memory(memory_id):
    conn = sqlite3.connect(get_db_path())
    cur = conn.cursor()

    cur.execute(
        """
        SELECT memory_pages.id, memory_pages.created_at, memory_pages.journal,
               memory_pages.location_name, memory_pages.weather,
               listening_sessions.album_id, listening_sessions.track_id
        FROM memory_pages
        JOIN listening_sessions ON memory_pages.session_id = listening_sessions.id
        WHERE memory_pages.id = ?
        """,
        (memory_id,),
    )

    memory = cur.fetchone()

    if memory is None:
        conn.close()
        return None

    cur.execute(
        """
        SELECT tags.name
        FROM tags
        JOIN memory_tags ON tags.id = memory_tags.tag_id
        WHERE memory_tags.memory_id = ?
        ORDER BY tags.name
        """,
        (memory_id,),
    )
    tags = [row[0] for row in cur.fetchall()]

    cur.execute(
        """
        SELECT type, file_path, captured_at
        FROM photos
        WHERE memory_id = ?
        ORDER BY captured_at
        """,
        (memory_id,),
    )
    photos = cur.fetchall()

    conn.close()

    return {
        "memory": memory,
        "tags": tags,
        "photos": photos,
    }