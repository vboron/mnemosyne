import argparse

from archive.query import list_discs, search_discs
from archive.register_disc import register_disc
from archive.album import register_album
from archive.track import register_track
from memory.session import create_session, end_session
from memory.page import create_memory_page

def print_rows(rows):
    if not rows:
        print("No records found.")
        return

    for accession, title, artist, year, archive_date in rows:
        year_text = year if year is not None else "unknown year"
        print(f"{accession} | {artist} — {title} | {year_text}")


def main():
    parser = argparse.ArgumentParser(description="Mnemosyne Archive CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("list-discs")

    search_parser = subparsers.add_parser("search-discs")
    search_parser.add_argument("term")

    register_disc_parser = subparsers.add_parser("register-disc")
    register_disc_parser.add_argument("--title", required=True)
    register_disc_parser.add_argument("--artist", required=True)
    register_disc_parser.add_argument("--year", type=int)

    register_album_parser = subparsers.add_parser("register-album")
    register_album_parser.add_argument("--disc", required=True)
    register_album_parser.add_argument("--title", required=True)
    register_album_parser.add_argument("--artist")
    register_album_parser.add_argument("--year", type=int)

    register_track_parser = subparsers.add_parser("register-track")
    register_track_parser.add_argument("--album-id", type=int, required=True)
    register_track_parser.add_argument("--title", required=True)
    register_track_parser.add_argument("--number", type=int)
    register_track_parser.add_argument("--duration", type=int)
    register_track_parser.add_argument("--flac-path")

    session_parser = subparsers.add_parser("create-session")
    session_parser.add_argument("--album-id", type=int)
    session_parser.add_argument("--track-id", type=int)
    session_parser.add_argument("--mode", default="listen")

    end_session_parser = subparsers.add_parser("end-session")
    end_session_parser.add_argument("session_id", type=int)

    memory_parser = subparsers.add_parser("create-memory")
    memory_parser.add_argument("--session-id", type=int, required=True)
    memory_parser.add_argument("--journal")
    memory_parser.add_argument("--tags")
    memory_parser.add_argument("--location")
    memory_parser.add_argument("--weather")
    args = parser.parse_args()

    if args.command == "list-discs":
        print_rows(list_discs())

    elif args.command == "search-discs":
        print_rows(search_discs(args.term))

    elif args.command == "register-disc":
        accession = register_disc(
            title=args.title,
            artist=args.artist,
            year=args.year,
        )
        print(f"Registered disc: {accession}")

    elif args.command == "register-album":
        album_id = register_album(
            disc_accession=args.disc,
            title=args.title,
            artist=args.artist,
            year=args.year,
        )
        print(f"Registered album ID: {album_id}")

    elif args.command == "register-track":
        track_id = register_track(
            album_id=args.album_id,
            title=args.title,
            track_number=args.number,
            duration_seconds=args.duration,
            flac_path=args.flac_path,
        )
        print(f"Registered track ID: {track_id}")
    elif args.command == "create-session":
        session_id = create_session(
            album_id=args.album_id,
            track_id=args.track_id,
            mode=args.mode,
        )
        print(f"Created listening session: {session_id}")

    elif args.command == "end-session":
        end_session(args.session_id)
        print(f"Ended listening session: {args.session_id}")

    elif args.command == "create-memory":
        tags = args.tags.split(",") if args.tags else []

        memory_id = create_memory_page(
            session_id=args.session_id,
            journal=args.journal,
            tags=tags,
            location_name=args.location,
            weather=args.weather,
        )

        print(f"Created memory page: {memory_id}")

if __name__ == "__main__":
    main()
