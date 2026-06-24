from pathlib import Path
from datetime import datetime
import subprocess


CAMERA_DEVICE = "/dev/video0"


def capture_photo(output_folder):
    output_folder = Path(output_folder)
    output_folder.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = output_folder / f"{timestamp}.jpg"

    subprocess.run(
        [
            "fswebcam",
            "-d",
            CAMERA_DEVICE,
            "-r",
            "1920x1080",
            "--no-banner",
            str(output_path),
        ],
        check=True,
    )

    return output_path