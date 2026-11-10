"""Store the most recent expense calculations locally and safely."""
import json
from pathlib import Path

HISTORY_FILE = Path.home() / ".python_small_projects" / "expense_history.json"


def load_history(path=HISTORY_FILE):
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    if not isinstance(value, list):
        return []
    return [row for row in value if isinstance(row, dict) and "shares" in row][-100:]


def save_history(entries, path=HISTORY_FILE):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(entries[-100:], indent=2), encoding="utf-8")
    temporary.replace(path)
