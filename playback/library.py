"""Read-only queries the player needs: tracks to play, plus path/artwork resolution.

The DB stores ``flac_path`` as whatever absolute path existed on the machine that
ripped the disc (e.g. ``/home/<user>/mnemosyne/vault/...``). That path will not
exist on another machine, so :func:`resolve_media_path` remaps it onto the local
vault instead of trusting the stored string.
"""

import sqlite3
from pathlib import Path

from archive.config import get_db_path, get_vault_discs


_SELECT = """
    SELECT t.id,
           t.track_number,
           t.title,
           t.artist,
           t.duration_seconds,
           t.flac_path,
           a.id,
           a.title,
           a.artist,
           a.year,
           pd.accession_code
    FROM tracks t
    JOIN albums a ON t.album_id = a.id
    JOIN physical_discs pd ON a.disc_id = pd.id
"""


def _row_to_track(row):
    (track_id, number, title, artist, duration, flac_path,
     album_id, album_title, album_artist, year, accession) = row

    return {
        "id": track_id,
        "track_number": number,
        "title": title,
        "artist": artist or album_artist,
        "album": album_title,
        "album_id": album_id,
        "year": year,
        "accession": accession,
        "duration_seconds": duration,
        "flac_path": flac_path,
        "has_artwork": artwork_path(accession) is not None,
    }


def _query(where, params):
    conn = sqlite3.connect(get_db_path())
    try:
        cur = conn.cursor()
        cur.execute(_SELECT + where, params)
        return [_row_to_track(row) for row in cur.fetchall()]
    finally:
        conn.close()


def get_track(track_id):
    rows = _query("WHERE t.id = ?", (track_id,))
    return rows[0] if rows else None


def find_track(term):
    """First playable track whose title matches ``term``."""
    rows = _query(
        "WHERE t.title LIKE ? AND t.flac_path IS NOT NULL ORDER BY t.id LIMIT 1",
        (f"%{term}%",),
    )
    return rows[0] if rows else None


def get_album_tracks(album_id):
    return _query(
        "WHERE t.album_id = ? AND t.flac_path IS NOT NULL ORDER BY t.track_number",
        (album_id,),
    )


def first_playable():
    """A sensible default track so the Now Playing screen has something to show.

    Prefer a track that actually carries a track-level artist (real, tagged
    rips) over bare test discs archived without metadata, so the screen isn't
    stuck on an "Unknown Artist" placeholder.
    """
    rows = _query(
        "WHERE t.flac_path IS NOT NULL ORDER BY (t.artist IS NULL), t.id LIMIT 1",
        (),
    )
    return rows[0] if rows else None


def resolve_media_path(stored_path):
    """Map a stored ``flac_path`` onto the local vault.

    Returns a :class:`Path`. If the original absolute path exists we use it; else
    we rebuild the ``vault/...`` tail under this machine's vault root. The returned
    path may still not exist (caller should check) — we never guess blindly.
    """
    if not stored_path:
        return None

    path = Path(stored_path)
    if path.exists():
        return path

    parts = path.parts
    if "vault" in parts:
        # Take the tail after the *last* "vault" segment and rebuild locally.
        last_vault = len(parts) - 1 - parts[::-1].index("vault")
        tail = Path(*parts[last_vault + 1:])
        candidate = get_vault_discs().parent / tail
        if candidate.exists():
            return candidate

    return path


def artwork_path(accession):
    """Local cover-art file for a disc, or ``None`` if it wasn't downloaded."""
    if not accession:
        return None
    candidate = get_vault_discs() / accession / "artwork" / "front.jpg"
    return candidate if candidate.exists() else None
