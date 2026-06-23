import sqlite3

DB_PATH = "../database/mnemosyne.db"


def next_accession():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM physical_discs")
    count = cur.fetchone()[0] + 1

    conn.close()

    return f"VB-CD-{count:06d}"


if __name__ == "__main__":
    print(next_accession())
