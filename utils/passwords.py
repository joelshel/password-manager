import json
from json.decoder import JSONDecodeError
import sys
from .colors import change_color, DANGER


def read_passwords(file: str) -> dict[str, str]:
    """
    Reads a file in json format with the app names and passwords.
    Returns a dict with that info

    Parameters
    ----------
    file
        Filename with the passwords

    Returns
    -------
    dict[str, str]
        Dictionary with the app name as key and the app password as
        value
    """
    try:
        with open(file, "r", encoding="utf-8") as f:
            return json.load(f)
    except JSONDecodeError:
        print(change_color(f"{file} is not in JSON format", DANGER))
        sys.exit()


def write_passwords(file: str, passwords: dict[str, str]):
    """
    Writes a dictionary with the app name and passwords to a file in
    json format

    Parameters
    ----------
    file
        Filename to save the passwords
    passwords
        Dictionary with the app name as key and the app password as
        value
    """
    with open(file, "w", encoding="utf-8") as f:
        json.dump(passwords, f)
