CREATE TABLE physical_discs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    accession_code TEXT UNIQUE NOT NULL,
    title TEXT,
    artist TEXT,
    year INTEGER,
    archive_date TEXT
);
