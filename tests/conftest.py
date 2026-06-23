import os
import sqlite3
from pathlib import Path
import pytest


@pytest.fixture(autouse=True)
def temp_archive_env(tmp_path, monkeypatch):
    test_db = tmp_path / "test_mnemosyne.db"
    test_vault = tmp_path / "vault" / "discs"

    monkeypatch.setenv("MNEMOSYNE_DB_PATH", str(test_db))
    monkeypatch.setenv("MNEMOSYNE_VAULT_DISCS", str(test_vault))

    schema_path = Path(__file__).resolve().parents[1] / "database" / "schema.sql"

    conn = sqlite3.connect(test_db)
    with open(schema_path) as f:
        conn.executescript(f.read())
    conn.close()
