from archive.register_disc import register_disc
from archive.album import register_album
from archive.track import register_track


def ingest_disc_stub(title, artist, year=None, tracks=None):
    tracks = tracks or []

    accession = register_disc(title=title, artist=artist, year=year)

    album_id = register_album(
        disc_accession=accession,
        title=title,
        artist=artist,
        year=year,
    )

    for index, track_title in enumerate(tracks, start=1):
        register_track(
            album_id=album_id,
            title=track_title,
            track_number=index,
        )

    return accession, album_id