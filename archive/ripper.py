from pathlib import Path
import subprocess


def rip_track_to_wav(track_number, output_path):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    command = [
        "cdparanoia",
        str(track_number),
        str(output_path),
    ]

    result = subprocess.run(command)

    if result.returncode != 0:
        raise RuntimeError(f"Failed to rip track {track_number}")

    return output_path


def convert_wav_to_flac(wav_path, flac_path):
    wav_path = Path(wav_path)
    flac_path = Path(flac_path)
    flac_path.parent.mkdir(parents=True, exist_ok=True)

    command = [
        "flac",
        "-f",
        "-o",
        str(flac_path),
        str(wav_path),
    ]

    result = subprocess.run(command)

    if result.returncode != 0:
        raise RuntimeError(f"Failed to convert {wav_path} to FLAC")

    return flac_path


def rip_track_to_flac(track_number, output_path, keep_wav=False):
    output_path = Path(output_path)
    wav_path = output_path.with_suffix(".wav")

    rip_track_to_wav(track_number, wav_path)
    flac_path = convert_wav_to_flac(wav_path, output_path)

    if not keep_wav:
        wav_path.unlink(missing_ok=True)

    return flac_path