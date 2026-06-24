from pathlib import Path

from memory.query import show_memory

EXPORT_DIR = Path("exports")


def export_memory(memory_id):
    result = show_memory(memory_id)

    if result is None:
        raise ValueError(f"No memory found: {memory_id}")

    EXPORT_DIR.mkdir(exist_ok=True)

    memory = result["memory"]
    tags = result["tags"]

    memory_id, session_id, created_at, journal, location, weather = memory

    output_path = EXPORT_DIR / f"memory_{memory_id}.txt"

    content = f"""Mnemosyne Memory {memory_id}

Created: {created_at}
Session: {session_id}
Location: {location or "unknown"}
Weather: {weather or "unknown"}
Tags: {", ".join(tags) if tags else "none"}

Journal:
{journal or ""}
"""

    output_path.write_text(content)

    return output_path