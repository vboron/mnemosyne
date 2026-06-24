import sqlite3
from archive.config import get_db_path


def year_in_review(year):
    conn = sqlite3.connect(get_db_path())
    cur = conn.cursor()

    year_prefix = f"{year}-"

    cur.execute(
        """
        SELECT COUNT(*)
        FROM memory_pages
        WHERE created_at LIKE ?
        """,
        (f"{year_prefix}%",),
    )
    memory_count = cur.fetchone()[0]

    cur.execute(
        """
        SELECT tags.name, COUNT(*) as count
        FROM tags
        JOIN memory_tags ON tags.id = memory_tags.tag_id
        JOIN memory_pages ON memory_pages.id = memory_tags.memory_id
        WHERE memory_pages.created_at LIKE ?
        GROUP BY tags.name
        ORDER BY count DESC
        LIMIT 10
        """,
        (f"{year_prefix}%",),
    )
    top_tags = cur.fetchall()

    cur.execute(
        """
        SELECT COUNT(*)
        FROM listening_sessions
        WHERE started_at LIKE ?
        """,
        (f"{year_prefix}%",),
    )
    session_count = cur.fetchone()[0]

    conn.close()

    return {
        "year": year,
        "memory_count": memory_count,
        "session_count": session_count,
        "top_tags": top_tags,
    }