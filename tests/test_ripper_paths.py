from pathlib import Path

from archive.ripper import rip_track_to_flac


def test_ripper_imports():
    assert callable(rip_track_to_flac)