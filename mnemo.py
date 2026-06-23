import argparse

from archive.query import list_discs, search_discs
from archive.register_disc import register_disc


def print_rows(rows):
    if not rows:
        print("No records found.")
        return

    for accession, title, artist, year, archive_date in rows:
        year_text = year if year is not None else "unknown year"
        print(f"{accession} | {artist} — {title} | {year_text}")


def main():
    parser = argparse.ArgumentParser(
        description="Mnemosyne Archive CLI"
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True
    )

    subparsers.add_parser("list-discs")

    search_parser = subparsers.add_parser("search-discs")
    search_parser.add_argument("term")

    register_parser = subparsers.add_parser("register-disc")
    register_parser.add_argument("--title", required=True)
    register_parser.add_argument("--artist", required=True)
    register_parser.add_argument("--year", type=int)

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


if __name__ == "__main__":
    main()
