import sqlite3

from archive.config import get_db_path


def register_track(
    album_id,
    title,
    artist=None,
    track_number=None,
    duration_seconds=None,
    flac_path=None,
    musicbrainz_track_id=None,
    musicbrainz_recording_id=None,
    musicbrainz_release_id=None,
    release_title=None,
    release_date=None,
):
    conn = sqlite3.connect(get_db_path())
    cur = conn.cursor()

    cur.execute(
        """
        SELECT id
        FROM albums
        WHERE id = ?
        """,
        (album_id,),
    )

    if cur.fetchone() is None:
        conn.close()
        raise ValueError(f"No album found with id: {album_id}")

    cur.execute(
        """
        INSERT INTO tracks
        (
            album_id,
            title,
            artist,
            track_number,
            duration_seconds,
            flac_path,
            musicbrainz_track_id,
            musicbrainz_recording_id,
            musicbrainz_release_id,
            release_title,
            release_date
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            album_id,
            title,
            artist,
            track_number,
            duration_seconds,
            flac_path,
            musicbrainz_track_id,
            musicbrainz_recording_id,
            musicbrainz_release_id,
            release_title,
            release_date,
        ),
    )

    track_id = cur.lastrowid

    conn.commit()
    conn.close()

    return track_id