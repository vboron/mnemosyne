from pathlib import Path
from datetime import datetime
import subprocess


CAMERA_DEVICES = {
    "portrait": "/dev/video0",
    "environment": "/dev/video0",
}


def capture_photo(output_folder, camera_type="portrait"):
    output_folder = Path(output_folder)
    output_folder.mkdir(parents=True, exist_ok=True)

    device = CAMERA_DEVICES[camera_type]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = output_folder / f"{camera_type}_{timestamp}.jpg"

    subprocess.run(
        [
            "fswebcam",
            "-d",
            device,
            "-r",
            "1920x1080",
            "--no-banner",
            str(output_path),
        ],
        check=True,
    )

    return output_path


def capture_portrait():
    return capture_photo("vault/photos/portrait", "portrait")


def capture_environment():
    return capture_photo("vault/photos/environment", "environment")