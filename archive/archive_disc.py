from pathlib import Path

from archive.album import register_album
from archive.cd_detect import get_cd_toc
from archive.register_disc import register_disc
from archive.ripper import rip_track_to_flac
from archive.track import register_track
from archive.config import get_vault_discs


def archive_current_disc(title, artist, year=None):
    tracks = get_cd_toc()

    accession = register_disc(
        title=title,
        artist=artist,
        year=year,
    )

    album_id = register_album(
        disc_accession=accession,
        title=title,
        artist=artist,
        year=year,
    )

    disc_folder = get_vault_discs() / accession
    tracks_folder = disc_folder / "tracks"

    for track in tracks:
        number = track["track_number"]
        filename = f"{number:02d}.flac"
        flac_path = tracks_folder / filename

        print(f"Ripping track {number:02d} → {flac_path}")

        rip_track_to_flac(
            track_number=number,
            output_path=flac_path,
        )

        register_track(
            album_id=album_id,
            title=track.get("title", f"Track {number:02d}"),
            artist=track.get("artist"),
            track_number=number,
            duration_seconds=track["duration_seconds"],
            flac_path=str(flac_path),
        )

    return accession