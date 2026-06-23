from archive.register_disc import register_disc


def test_register_disc_creates_accession():
    accession = register_disc(
        title="Test Disc",
        artist="Test Artist",
    )

    assert accession.startswith("VB-CD-")
    assert len(accession) == 12
