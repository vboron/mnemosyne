from pathlib import Path
import os

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def get_db_path():
    return Path(
        os.environ.get(
            "MNEMOSYNE_DB_PATH",
            PROJECT_ROOT / "database" / "mnemosyne.db",
        )
    )


def get_vault_discs():
    return Path(
        os.environ.get(
            "MNEMOSYNE_VAULT_DISCS",
            PROJECT_ROOT / "vault" / "discs",
        )
    )