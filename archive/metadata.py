import musicbrainzngs
import discid

musicbrainzngs.set_useragent(
    "Mnemosyne",
    "0.1",
    "https://github.com/vboron/mnemosyne",
)


def get_disc_id():

    disc = discid.read("/dev/sr0")

    return disc.id



def lookup_disc_metadata():
    disc_id = get_disc_id()

    result = musicbrainzngs.get_releases_by_discid(
        disc_id,
        includes=["artists", "recordings"],
    )

    releases = result.get("disc", {}).get("release-list", [])

    if not releases:
        return {
            "disc_id": disc_id,
            "found": False,
            "releases": [],
        }

    parsed = []

    for release in releases:
        artist_credit = release.get("artist-credit", [])
        artist = ""

        if artist_credit:
            artist = artist_credit[0].get("artist", {}).get("name", "")

        media = release.get("medium-list", [])
        tracks = []

        if media:
            track_list = media[0].get("track-list", [])

            for track in track_list:
                recording = track.get("recording", {})

                track_artist = ""

                artist_credit = recording.get("artist-credit", [])

                if artist_credit:
                    track_artist = (
                        artist_credit[0]
                        .get("artist", {})
                        .get("name", "")
                    )

                tracks.append(
                    {
                        "number": int(track.get("number", 0)),
                        "title": recording.get("title", track.get("title", "")),
                        "artist": track_artist,
                    }
                )

        parsed.append(
            {
                "id": release.get("id"),
                "title": release.get("title"),
                "artist": artist,
                "date": release.get("date"),
                "tracks": tracks,
            }
        )

    return {
        "disc_id": disc_id,
        "found": True,
        "releases": parsed,
    }