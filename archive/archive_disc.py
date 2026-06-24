import json
import re
from datetime import datetime
from pathlib import Path

import requests

from archive.album import register_album
from archive.cd_detect import get_cd_toc
from archive.config import get_vault_discs
from archive.metadata import lookup_disc_metadata
from archive.register_disc import register_disc
from archive.ripper import rip_track_to_flac
from archive.track import register_track


def safe_filename(value):
    value = value.strip()
    value = re.sub(r"[^\w\s\-.]", "", value)
    value = re.sub(r"\s+", " ", value)
    return value[:120]


def year_from_date(date_text):
    if not date_text:
        return None
    return int(date_text[:4]) if date_text[:4].isdigit() else None


def download_artwork(release, artwork_folder):
    release_id = release.get("id")
    if not release_id:
        return None

    url = f"https://coverartarchive.org/release/{release_id}/front"
    output = artwork_folder / "front.jpg"

    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            output.write_bytes(response.content)
            return str(output)
    except requests.RequestException:
        return None

    return None


def archive_current_disc_from_metadata(release_index=0):
    toc_tracks = get_cd_toc()
    metadata = lookup_disc_metadata()

    if not metadata["found"]:
        raise RuntimeError("No MusicBrainz metadata found for this disc.")

    release = metadata["releases"][release_index]

    title = release["title"]
    artist = release["artist"]
    year = year_from_date(release.get("date"))

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
    artwork_folder = disc_folder / "artwork"

    mb_tracks = release.get("tracks", [])
    artwork_path = download_artwork(release, artwork_folder)

    archived_tracks = []

    for toc_track in toc_tracks:
        number = toc_track["track_number"]
        mb_track = mb_tracks[number - 1] if number - 1 < len(mb_tracks) else {}

        track_title = mb_track.get("title") or f"Track {number:02d}"
        track_artist = mb_track.get("artist") or artist

        filename = safe_filename(
            f"{number:02d} - {track_artist} - {track_title}.flac"
        )

        flac_path = tracks_folder / filename

        print(f"Ripping {number:02d}: {track_artist} — {track_title}")

        rip_track_to_flac(
            track_number=number,
            output_path=flac_path,
        )

        register_track(
            album_id=album_id,
            title=track_title,
            artist=track_artist,
            track_number=number,
            duration_seconds=toc_track["duration_seconds"],
            flac_path=str(flac_path),
        )

        archived_tracks.append(
            {
                "number": number,
                "title": track_title,
                "artist": track_artist,
                "duration_seconds": toc_track["duration_seconds"],
                "flac_path": str(flac_path),
            }
        )

    metadata_json = {
        "accession": accession,
        "musicbrainz_disc_id": metadata["disc_id"],
        "title": title,
        "artist": artist,
        "year": year,
        "archived_at": datetime.now().isoformat(),
        "artwork_path": artwork_path,
        "tracks": archived_tracks,
    }

    metadata_path = disc_folder / "metadata.json"
    metadata_path.write_text(
        json.dumps(metadata_json, indent=2, ensure_ascii=False)
    )

    return accession