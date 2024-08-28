#!/usr/bin/env python

import base64
import os
import os.path as path
from getpass import getpass
from cryptography.fernet import Fernet
from cryptography.fernet import InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import pyperclip
from utils.colors import *
from utils.files import *
from utils.passwords import *

PASSWORDS = "passwords.txt"
SALT = "salt.txt"


def get_salt() -> bytes:

    if not path.exists(SALT):
        salt = os.urandom(32)

        with open(SALT, "wb") as file:
            file.write(salt)

        return salt

    with open(SALT, "rb") as file:
        salt = file.read().strip()

    return salt


def get_key(password: bytes) -> bytes:
    salt = get_salt()
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(), length=32, salt=salt, iterations=480000
    )
    key = base64.urlsafe_b64encode(kdf.derive(password))
    return key


def get_apps() -> list[str]:
    with open(PASSWORDS, "r") as file:
        apps = [line.strip().split(" ")[0] for line in file.readlines()]
    return apps


def show_password(f: Fernet, passwords: dict[str, str]):
    if not passwords:
        print(change_color("There is no password saved yet", WARNING))
        return

    search_term = input("Enter the app you want to see the password: ").strip()

    for app in passwords:
        if app == search_term:
            password = f.decrypt(passwords[app].encode("utf-8")).decode()
            pyperclip.copy(password)
            print(
                change_color(
                    f"{search_term} password copied to the clipboard", SUCCESS
                )
            )
            return

    print(
        change_color(f"{search_term} app doesn't exist in the list", WARNING)
    )


def add_password(f: Fernet, passwords: dict[str, str]):
    apps = [app for app in passwords]

    app = input("Enter the app name: ")
    if app in apps:
        print(change_color(f"{app} app is already registered", WARNING))
        return

    while True:
        password = getpass("Enter the app password: ")
        repeat_pass = getpass("Repeat the password: ")
        if password == repeat_pass:
            break
        print(change_color("The passwords don't match, try again", WARNING))

    password = f.encrypt(password.encode("utf-8")).decode()
    append_password(PASSWORDS, app, password)
    passwords[app] = password
    print(change_color(f"{app} password was added", SUCCESS))


def delete_password(f: Fernet, passwords: dict[str, str]):
    if not passwords:
        print(change_color("There is no password saved yet", WARNING))
        return
    app = input("Enter the app name you want to delete: ")

    try:
        del passwords[app]
    except KeyError:
        print(change_color(f"{app} app doesn't exist in the list", WARNING))
        return

    write_passwords(PASSWORDS, passwords)
    print(change_color(f"{app} password deleted", SUCCESS))


def update_password(f: Fernet, passwords: dict[str, str]):
    if not passwords:
        print(change_color("There is no password saved yet", WARNING))
        return
    app = input("Enter the app name you want to change the password: ")

    if app not in passwords:
        print(change_color(f"{app} app doesn't exist in the list", WARNING))
        return

    while True:
        password = getpass("Enter the new password: ")
        repeat_pass = getpass("Repeat the password: ")
        if password == repeat_pass:
            break
        print(change_color("The passwords don't match, try again", WARNING))

    password = f.encrypt(password.encode("utf-8")).decode()
    passwords[app] = password

    write_passwords(PASSWORDS, passwords)
    print(change_color(f"{app} password changed", SUCCESS))


def list_apps(passwords: dict[str, str]):
    if not passwords:
        print(change_color("There is no password saved yet", WARNING))
        return

    [print(change_color(app, SUCCESS)) for app in passwords]


def change_master_password(f: Fernet, passwords: dict[str, str]) -> Fernet:
    if not passwords:
        print(
            change_color(
                "You haven't saved any password yet, so no verification"
                + " is needed, make sure to not forget your new master"
                + " password after this change!",
                DANGER,
            )
        )
    else:
        while True:
            master_pass = getpass(
                "Enter your current master password: "
            ).encode("utf-8")

            temp_key = get_key(master_pass)
            temp_f = Fernet(temp_key)
            is_master_pass = verify_password(temp_f, passwords)
            if is_master_pass:
                break
            else:
                print(
                    change_color(
                        "Master password incorrect, try again.", WARNING
                    )
                )

    while True:
        new_master_pass = getpass("Enter the new master password: ")
        new_master_pass_repeat = getpass("Repeat the new master password: ")

        if new_master_pass == new_master_pass_repeat:
            break
        else:
            print(
                change_color("The passwords don't match try again.", WARNING)
            )

    new_master_pass = new_master_pass.encode("utf-8")
    os.remove(SALT)
    if not passwords:
        key = get_key(new_master_pass)
        f = Fernet(key)
    else:
        f, passwords = reencrypt_passwords(f, new_master_pass, passwords)
    print(change_color("Master password changed", SUCCESS))
    return f, passwords


def reencrypt_passwords(
    f: Fernet, master_pass: bytes, passwords: dict[str, str]
) -> Fernet:
    key = get_key(master_pass)
    new_f = Fernet(key)

    passwords = {
        app: new_f.encrypt(f.decrypt(password.encode("utf-8"))).decode()
        for app, password in passwords.items()
    }

    write_passwords(PASSWORDS, passwords)
    return new_f, passwords


def menu(f: Fernet, passwords: dict[str, str]):
    while True:
        print("\n1. read a password")
        print("2. add a new password")
        print("3. delete a password")
        print("4. update a password")
        print("5. list apps")
        print("6. change the master password")
        print("0. exit")

        option = input("choose an option: ")
        try:
            option = int(option)
        except ValueError:
            pass

        if option == 1:
            show_password(f, passwords)
        elif option == 2:
            add_password(f, passwords)
        elif option == 3:
            delete_password(f, passwords)
        elif option == 4:
            update_password(f, passwords)
        elif option == 5:
            list_apps(passwords)
        elif option == 6:
            f, passwords = change_master_password(f, passwords)
        elif option == 0:
            break
        else:
            print(change_color("Invalid option", WARNING))


def verify_password(f: Fernet, passwords: dict[str, str]) -> bool:
    first = list(passwords.keys())[0]
    password = passwords[first]

    try:
        f.decrypt(password)
        return True
    except InvalidToken:
        return False


def login(passwords: dict[str, str]) -> Fernet:
    while True:
        master_pass = getpass("Enter the master password: ").encode("utf-8")
        key = get_key(master_pass)
        f = Fernet(key)
        is_master_pass = verify_password(f, passwords)
        if is_master_pass:
            break
        else:
            print(
                change_color(
                    "Master password incorrect, try again.\n", WARNING
                )
            )

    return f


def first_login() -> Fernet:
    print(
        change_color(
            "This message will appear every time until you save your first "
            + "password, or will appear again if you delete all your "
            + "passwords.\nThis happens because the passwords are encrypted "
            + "using your master password and the master password isn't saved "
            + "anywhere inside of this program.",
            DANGER,
        )
    )

    while True:
        master_pass = getpass("Enter the master password: ").encode("utf-8")
        repeat_pass = getpass("Repeat the master password: ").encode("utf-8")
        if master_pass == repeat_pass:
            break
        print(change_color("The passwords don't match, try again", WARNING))

    key = get_key(master_pass)
    f = Fernet(key)
    return f


def main():
    if is_empty(PASSWORDS):
        passwords = {}
        f = first_login()
    else:
        passwords = read_passwords(PASSWORDS)
        f = login(passwords)
    menu(f, passwords)


if __name__ == "__main__":
    main()
