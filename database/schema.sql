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

    FOREIGN KEY(disc_id)
        REFERENCES physical_discs(id)
);

CREATE TABLE IF NOT EXISTS tracks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    album_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    track_number INTEGER,
    duration_seconds INTEGER,
    flac_path TEXT,

    FOREIGN KEY(album_id)
        REFERENCES albums(id)
);

CREATE TABLE IF NOT EXISTS counters (
    name TEXT PRIMARY KEY,
    value INTEGER NOT NULL
);

INSERT OR IGNORE INTO counters (name, value)
VALUES ('cd_accession', 0);

