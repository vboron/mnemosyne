CREATE TABLE tracks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    album_id INTEGER,
    title TEXT,
    track_number INTEGER,
    duration INTEGER,
    flac_path TEXT,

    FOREIGN KEY(album_id)
        REFERENCES albums(id)
);
