import re
import subprocess


TRACK_RE = re.compile(
    r"^\s*(\d+)\.\s+(\d+)\s+\[(\d+):(\d+)\.(\d+)\]"
)


def get_cd_toc_raw():
    result = subprocess.run(
        ["cdparanoia", "-Q"],
        capture_output=True,
        text=True,
    )

    output = result.stdout + result.stderr

    if "Table of contents" not in output:
        raise RuntimeError("No readable audio CD found.")

    return output


def parse_cd_toc(output):
    tracks = []

    for line in output.splitlines():
        match = TRACK_RE.match(line)

        if not match:
            continue

        track_number = int(match.group(1))
        frames = int(match.group(2))
        minutes = int(match.group(3))
        seconds = int(match.group(4))

        duration_seconds = minutes * 60 + seconds

        tracks.append(
            {
                "track_number": track_number,
                "frames": frames,
                "duration_seconds": duration_seconds,
                "duration_text": f"{minutes:02d}:{seconds:02d}",
            }
        )

    return tracks


def get_cd_toc():
    raw_output = get_cd_toc_raw()
    return parse_cd_toc(raw_output)


def print_cd_toc():
    tracks = get_cd_toc()

    print("Audio CD detected")
    print()

    for track in tracks:
        print(
            f"Track {track['track_number']:02d} "
            f"| {track['duration_text']}"
        )

    print()
    print(f"Total tracks: {len(tracks)}")