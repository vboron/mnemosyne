import argparse

from archive.query import list_discs, search_discs
from archive.register_disc import register_disc
from archive.album import register_album
from archive.track import register_track
from memory.session import create_session, end_session
from memory.page import create_memory_page
from memory.query import list_memories, show_memory, search_memories_by_tag
from mixtape.mixtape import create_mixtape, add_track_to_mixtape
from memory.revisit import revisit_today, revisit_random
from memory.photo import register_photo
from archive.provenance import show_track_provenance
from archive.ingest import ingest_disc_stub
from memory.wizard import preserve_memory
from memory.review import year_in_review
from memory.export import export_memory

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

    subparsers.add_parser("list-memories")

    show_memory_parser = subparsers.add_parser("show-memory")
    show_memory_parser.add_argument("memory_id", type=int)

    tag_search_parser = subparsers.add_parser("search-memories-tag")
    tag_search_parser.add_argument("tag")

    create_mix_parser = subparsers.add_parser("create-mixtape")
    create_mix_parser.add_argument("--title", required=True)
    create_mix_parser.add_argument("--reason")
    create_mix_parser.add_argument("--liner-notes")

    add_mix_track_parser = subparsers.add_parser("add-track-to-mixtape")
    add_mix_track_parser.add_argument("--mix-code", required=True)
    add_mix_track_parser.add_argument("--track-id", type=int, required=True)

    subparsers.add_parser("revisit-today")
    subparsers.add_parser("revisit-random")

    photo_parser = subparsers.add_parser("register-photo")
    photo_parser.add_argument("--memory-id", type=int, required=True)
    photo_parser.add_argument("--type", required=True, choices=["portrait", "environment"])
    photo_parser.add_argument("--file-path", required=True)

    track_prov_parser = subparsers.add_parser("show-track")
    track_prov_parser.add_argument("term")

    ingest_parser = subparsers.add_parser("ingest-disc-stub")
    ingest_parser.add_argument("--title", required=True)
    ingest_parser.add_argument("--artist", required=True)
    ingest_parser.add_argument("--year", type=int)
    ingest_parser.add_argument("--tracks", help="Comma-separated track titles")

    subparsers.add_parser("preserve")

    review_parser = subparsers.add_parser("year-in-review")
    review_parser.add_argument("year", type=int)

    export_parser = subparsers.add_parser("export-memory")
    export_parser.add_argument("memory_id", type=int)

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
    elif args.command == "list-memories":
        for memory_id, created_at, journal, location, weather, album_id, track_id in list_memories():
            print(f"{memory_id} | {created_at} | {location or 'unknown location'} | {journal or ''}")

    elif args.command == "show-memory":
        result = show_memory(args.memory_id)

        if result is None:
            print("No memory found.")
        else:
            memory = result["memory"]
            tags = result["tags"]

            memory_id, session_id, created_at, journal, location, weather = memory

            print(f"Memory {memory_id}")
            print(f"Created: {created_at}")
            print(f"Session: {session_id}")
            print(f"Location: {location or 'unknown'}")
            print(f"Weather: {weather or 'unknown'}")
            print(f"Tags: {', '.join(tags) if tags else 'none'}")
            print()
            print(journal or "")

    elif args.command == "search-memories-tag":
        rows = search_memories_by_tag(args.tag)

        if not rows:
            print("No memories found.")
        else:
            for memory_id, created_at, journal in rows:
                print(f"{memory_id} | {created_at} | {journal or ''}")

    elif args.command == "create-mixtape":
        mix_code = create_mixtape(
            title=args.title,
            reason=args.reason,
            liner_notes=args.liner_notes,
        )
        print(f"Created mixtape: {mix_code}")

    elif args.command == "add-track-to-mixtape":
        order = add_track_to_mixtape(
            mix_code=args.mix_code,
            track_id=args.track_id,
        )
        print(f"Added track at position {order}")

    elif args.command == "revisit-today":
        rows = revisit_today()
        if not rows:
            print("No memories found for today.")
        else:
            for memory_id, created_at, journal, location, weather in rows:
                print(f"Memory {memory_id} | {created_at}")
                print(f"Location: {location or 'unknown'}")
                print(f"Weather: {weather or 'unknown'}")
                print(journal or "")
                print()

    elif args.command == "revisit-random":
        row = revisit_random()
        if row is None:
            print("No memories found.")
        else:
            memory_id, created_at, journal, location, weather = row
            print(f"Memory {memory_id} | {created_at}")
            print(f"Location: {location or 'unknown'}")
            print(f"Weather: {weather or 'unknown'}")
            print(journal or "")

    elif args.command == "register-photo":
        photo_id = register_photo(
            memory_id=args.memory_id,
            photo_type=args.type,
            file_path=args.file_path,
        )
        print(f"Registered photo: {photo_id}")

    elif args.command == "show-track":
        results = show_track_provenance(args.term)

        if not results:
            print("No tracks found.")
        else:
            for result in results:
                track_id, track_title, track_number, album_title, album_artist, accession = result["track"]

                print(f"Track {track_id}: {track_title}")
                print(f"Origin: {accession}")
                print(f"Album: {album_artist} — {album_title}")

                print("Mixtapes:")
                if result["mixtapes"]:
                    for mix_code, mix_title in result["mixtapes"]:
                        print(f"  {mix_code} — {mix_title}")
                else:
                    print("  none")

                print("Listening sessions:")
                if result["sessions"]:
                    for session_id, started_at, mode in result["sessions"]:
                        print(f"  {session_id} | {started_at} | {mode}")
                else:
                    print("  none")

                print()

    elif args.command == "ingest-disc-stub":
        tracks = args.tracks.split(",") if args.tracks else []

        accession, album_id = ingest_disc_stub(
            title=args.title,
            artist=args.artist,
            year=args.year,
            tracks=[track.strip() for track in tracks],
        )

        print(f"Archived disc: {accession}")
        print(f"Album ID: {album_id}")

    elif args.command == "preserve":
        memory_id = preserve_memory()
        print(f"Preserved memory: {memory_id}")

    elif args.command == "year-in-review":
        review = year_in_review(args.year)

        print(f"Mnemosyne Year in Review: {review['year']}")
        print(f"Memories: {review['memory_count']}")
        print(f"Listening sessions: {review['session_count']}")
        print("Top tags:")

        for tag, count in review["top_tags"]:
            print(f"  {tag}: {count}")

    elif args.command == "export-memory":
        output_path = export_memory(args.memory_id)
        print(f"Exported memory to: {output_path}")

if __name__ == "__main__":
    main()
