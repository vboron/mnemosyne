from archive.register_disc import register_disc
from archive.album import register_album
from archive.track import register_track


disc_accession = register_disc(
    title="Rumours",
    artist="Fleetwood Mac",
    year=1977,
)

album_id = register_album(
    disc_accession=disc_accession,
    title="Rumours",
    artist="Fleetwood Mac",
    year=1977,
)

tracks = [
    "Second Hand News",
    "Dreams",
    "Never Going Back Again",
    "Don't Stop",
    "Go Your Own Way",
]

for index, title in enumerate(tracks, start=1):
    register_track(
        album_id=album_id,
        title=title,
        track_number=index,
    )

print()
print("Registered demo archive:")
print(f"Disc: {disc_accession}")
print("Album: Rumours")
print("Tracks:")

for index, title in enumerate(tracks, start=1):
    print(f"{index:02d}. {title}")

