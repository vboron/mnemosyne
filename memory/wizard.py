from memory.session import create_session, end_session
from memory.page import create_memory_page
from memory.photo import register_photo
from services.location import get_current_location
from services.weather import get_current_weather
from hardware.camera import capture_portrait, capture_environment


def preserve_memory():
    album_id_raw = input("Album ID, optional: ").strip()
    track_id_raw = input("Track ID, optional: ").strip()

    album_id = int(album_id_raw) if album_id_raw else None
    track_id = int(track_id_raw) if track_id_raw else None

    session_id = create_session(
        album_id=album_id,
        track_id=track_id,
        mode="memory",
    )

    journal = input("Journal note: ").strip()
    tags_raw = input("Atmosphere tags, comma-separated: ").strip()
    tags = [tag.strip() for tag in tags_raw.split(",") if tag.strip()]

    location = get_current_location()
    weather = get_current_weather()

    memory_id = create_memory_page(
        session_id=session_id,
        journal=journal,
        tags=tags,
        location_name=location,
        weather=weather,
    )

    capture_portrait_answer = input("Capture portrait photo? [Y/n]: ").strip().lower()

    if capture_portrait_answer != "n":
        photo_path = capture_portrait()
        register_photo(memory_id, "portrait", str(photo_path))
        print(f"Captured portrait: {photo_path}")

    capture_environment_answer = input("Capture environment photo? [Y/n]: ").strip().lower()

    if capture_environment_answer != "n":
        photo_path = capture_environment()
        register_photo(memory_id, "environment", str(photo_path))
        print(f"Captured environment: {photo_path}")

    end_session(session_id)

    return memory_id