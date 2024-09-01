import json
from json.decoder import JSONDecodeError
import sys
from .colors import change_color, DANGER


def read_passwords(file) -> dict[str, str]:
    try:
        with open(file, "r", encoding="utf-8") as f:
            return json.load(f)
    except JSONDecodeError:
        print(change_color(f"{file} is not in JSON format", DANGER))
        sys.exit()


def write_passwords(file: str, passwords: dict[str, str]):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(passwords, f)
