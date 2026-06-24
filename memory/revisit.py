import sqlite3
from datetime import date

from archive.config import get_db_path


def revisit_today():
    today = date.today()
    month_day = today.strftime("-%m-%d")

    conn = sqlite3.connect(get_db_path())
    cur = conn.cursor()

    cur.execute(
        """
        SELECT memory_pages.id, memory_pages.created_at, memory_pages.journal,
               memory_pages.location_name, memory_pages.weather
        FROM memory_pages
        WHERE substr(memory_pages.created_at, 5, 6) = ?
        ORDER BY memory_pages.created_at DESC
        """,
        (month_day,),
    )

    rows = cur.fetchall()
    conn.close()
    return rows


def revisit_random():
    conn = sqlite3.connect(get_db_path())
    cur = conn.cursor()

    cur.execute(
        """
        SELECT id, created_at, journal, location_name, weather
        FROM memory_pages
        ORDER BY RANDOM()
        LIMIT 1
        """
    )

    row = cur.fetchone()
    conn.close()
    return row