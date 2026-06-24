CREATE TABLE IF NOT EXISTS physical_discs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    accession_code TEXT UNIQUE NOT NULL,
    title TEXT,
    artist TEXT,
    year INTEGER,
    archive_date TEXT
);

CREATE TABLE IF NOT EXISTS albums (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    disc_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    artist TEXT,
    year INTEGER,
    FOREIGN KEY(disc_id) REFERENCES physical_discs(id)
);

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

CREATE TABLE IF NOT EXISTS photos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    memory_id INTEGER NOT NULL,
    type TEXT NOT NULL,
    file_path TEXT NOT NULL,
    captured_at TEXT NOT NULL,
    FOREIGN KEY(memory_id) REFERENCES memory_pages(id)
);

CREATE TABLE IF NOT EXISTS mixtapes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mix_code TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    created_at TEXT NOT NULL,
    reason TEXT,
    liner_notes TEXT
);

CREATE TABLE IF NOT EXISTS mixtape_tracks (
    mixtape_id INTEGER NOT NULL,
    track_id INTEGER NOT NULL,
    track_order INTEGER NOT NULL,
    PRIMARY KEY(mixtape_id, track_order),
    FOREIGN KEY(mixtape_id) REFERENCES mixtapes(id),
    FOREIGN KEY(track_id) REFERENCES tracks(id)
);

CREATE TABLE IF NOT EXISTS tracks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    album_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    artist TEXT,
    track_number INTEGER,
    duration_seconds INTEGER,
    flac_path TEXT,
    FOREIGN KEY(album_id) REFERENCES albums(id)
);

CREATE TABLE IF NOT EXISTS counters (
    name TEXT PRIMARY KEY,
    value INTEGER NOT NULL
);

INSERT OR IGNORE INTO counters (name, value)
VALUES ('cd_accession', 0);

INSERT OR IGNORE INTO counters (name, value)
VALUES ('mixtape', 0);