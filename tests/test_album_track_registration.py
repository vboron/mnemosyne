from archive.register_disc import register_disc
from archive.album import register_album
from archive.track import register_track


def test_album_and_track_registration():
    disc_accession = register_disc(
        title="Test Album Disc",
        artist="Test Artist",
    )

    album_id = register_album(
        disc_accession=disc_accession,
        title="Test Album",
        artist="Test Artist",
    )

    track_id = register_track(
        album_id=album_id,
        title="Test Track",
        track_number=1,
    )

    assert isinstance(album_id, int)
    assert isinstance(track_id, int)

