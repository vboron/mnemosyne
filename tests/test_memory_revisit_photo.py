from memory.session import create_session
from memory.page import create_memory_page
from memory.photo import register_photo
from memory.revisit import revisit_today, revisit_random


def test_memory_revisit_and_photo_registration():
    session_id = create_session(mode="listen")

    memory_id = create_memory_page(
        session_id=session_id,
        journal="Test memory.",
        tags=["Rain", "Velvet"],
        location_name="London",
        weather="Cloudy",
    )

    photo_id = register_photo(
        memory_id=memory_id,
        photo_type="portrait",
        file_path="vault/photos/portrait/test.jpg",
    )

    today_rows = revisit_today()
    random_row = revisit_random()

    assert isinstance(memory_id, int)
    assert isinstance(photo_id, int)
    assert len(today_rows) >= 1
    assert random_row is not None