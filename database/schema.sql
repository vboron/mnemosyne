CREATE TABLE IF NOT EXISTS listening_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    album_id INTEGER,
    track_id INTEGER,
    started_at TEXT NOT NULL,
    ended_at TEXT,
    mode TEXT,

    FOREIGN KEY(album_id) REFERENCES albums(id),
    FOREIGN KEY(track_id) REFERENCES tracks(id)
);

CREATE TABLE IF NOT EXISTS memory_pages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    created_at TEXT NOT NULL,
    journal TEXT,
    location_name TEXT,
    weather TEXT,

    FOREIGN KEY(session_id) REFERENCES listening_sessions(id)
);

CREATE TABLE IF NOT EXISTS tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS memory_tags (
    memory_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,

    PRIMARY KEY(memory_id, tag_id),
    FOREIGN KEY(memory_id) REFERENCES memory_pages(id),
    FOREIGN KEY(tag_id) REFERENCES tags(id)
);
