CREATE TABLE IF NOT EXISTS physical_discs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    accession_code TEXT UNIQUE NOT NULL,
    title TEXT,
    artist TEXT,
    year INTEGER,
    archive_date TEXT
);

CREATE TABLE IF NOT EXISTS counters (
    name TEXT PRIMARY KEY,
    value INTEGER NOT NULL
);

INSERT OR IGNORE INTO counters (name, value)
VALUES ('cd_accession', 0);
