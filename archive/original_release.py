import sqlite3
import musicbrainzngs

from archive.config import get_db_path


def _year_sort_key(release):
    date = release.get("date")
    if not date:
        return "9999-99-99"
    return date


def find_original_release(term):
    conn = sqlite3.connect(get_db_path())
    cur = conn.cursor()

    cur.execute(
        """
        SELECT title, artist, musicbrainz_recording_id,
               release_title, release_date
        FROM tracks
        WHERE title LIKE ?
          AND musicbrainz_recording_id IS NOT NULL
        ORDER BY id
        LIMIT 1
        """,
        (f"%{term}%",),
    )

    row = cur.fetchone()
    conn.close()

    if row is None:
        return None

    title, artist, recording_id, current_release, current_date = row

    result = musicbrainzngs.get_recording_by_id(
        recording_id,
        includes=["releases", "artists"],
    )

    releases = result.get("recording", {}).get("release-list", [])
    dated_releases = [release for release in releases if release.get("date")]
    dated_releases.sort(key=_year_sort_key)

    earliest = dated_releases[0] if dated_releases else None

    return {
        "title": title,
        "artist": artist,
        "recording_id": recording_id,
        "current_release": current_release,
        "current_date": current_date,
        "earliest_release": earliest,
    }