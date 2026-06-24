from archive.register_disc import register_disc
from archive.album import register_album
from archive.track import register_track
from archive.provenance import show_track_provenance


def test_track_provenance_finds_origin_disc():
    accession = register_disc(
        title="Test Disc",
        artist="Test Artist",
    )

    album_id = register_album(
        disc_accession=accession,
        title="Test Album",
        artist="Test Artist",
    )

    register_track(
        album_id=album_id,
        title="Test Track",
        track_number=1,
    )

    results = show_track_provenance("Test Track")

    assert len(results) == 1
    assert results[0]["track"][5] == accession