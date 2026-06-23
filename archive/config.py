from pathlib import Path
import os

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DB_PATH = Path(
    os.environ.get(
        "MNEMOSYNE_DB_PATH",
        PROJECT_ROOT / "database" / "mnemosyne.db",
    )
)

VAULT_DISCS = Path(
    os.environ.get(
        "MNEMOSYNE_VAULT_DISCS",
        PROJECT_ROOT / "vault" / "discs",
    )
)
