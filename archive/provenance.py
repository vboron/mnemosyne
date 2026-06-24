import sqlite3

from archive.config import get_db_path


def show_track_provenance(term):
    conn = sqlite3.connect(get_db_path())
    cur = conn.cursor()

    cur.execute(
        """
        SELECT tracks.id, tracks.title, tracks.track_number,
               albums.title, albums.artist,
               physical_discs.accession_code
        FROM tracks
        JOIN albums ON tracks.album_id = albums.id
        JOIN physical_discs ON albums.disc_id = physical_discs.id
        WHERE tracks.title LIKE ?
        ORDER BY tracks.id
        """,
        (f"%{term}%",),
    )

    tracks = cur.fetchall()
    results = []

    for track in tracks:
        track_id = track[0]

        cur.execute(
            """
            SELECT mixtapes.mix_code, mixtapes.title
            FROM mixtapes
            JOIN mixtape_tracks ON mixtapes.id = mixtape_tracks.mixtape_id
            WHERE mixtape_tracks.track_id = ?
            ORDER BY mixtapes.id
            """,
            (track_id,),
        )
        mixtapes = cur.fetchall()

        cur.execute(
            """
            SELECT listening_sessions.id, listening_sessions.started_at, listening_sessions.mode
            FROM listening_sessions
            WHERE listening_sessions.track_id = ?
            ORDER BY listening_sessions.started_at DESC
            """,
            (track_id,),
        )
        sessions = cur.fetchall()

        results.append(
            {
                "track": track,
                "mixtapes": mixtapes,
                "sessions": sessions,
            }
        )

    conn.close()
    return results