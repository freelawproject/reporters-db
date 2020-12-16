import json
from pathlib import Path
import sys


json_path = Path(__file__).parent / "data" / "reporters.json"


def get_json():
    current_json = Path(json_path).read_text()
    formatted_json = json.dumps(
        json.loads(current_json),
        indent=4,
        ensure_ascii=False,
        sort_keys=True,
    )
    formatted_json += "\n"
    return current_json, formatted_json


def check_json():
    current_json, formatted_json = get_json()
    return current_json == formatted_json


def update_json():
    current_json, formatted_json = get_json()
    if current_json != formatted_json:
        json_path.write_text(formatted_json)
        return True
    return False


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--check":
        if not check_json():
            sys.exit("JSON file doesn't match. Run without --check to update.")
    else:
        updated = update_json()
        print("JSON file updated." if updated else "No changes needed.")
