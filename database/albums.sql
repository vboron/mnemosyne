CREATE TABLE albums (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    disc_id INTEGER,
    title TEXT,
    artist TEXT,
    year INTEGER,

    FOREIGN KEY(disc_id)
        REFERENCES physical_discs(id)
);
