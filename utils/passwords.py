def read_passwords(file) -> dict[str, str]:
    with open(file, "r") as f:
        lines = f.readlines()

    lines = [line.strip().split(" ") for line in lines]
    passwords = {app: password for app, password in lines}
    return passwords


def write_passwords(file: str, passwords: dict[str, str]):
    lines = [f"{app} {password}\n" for app, password in passwords.items()]
    with open(file, "w") as f:
        f.writelines(lines)


def append_password(file: str, app: str, password: str):
    with open(file, "a") as f:
        f.write(f"{app} {password}\n")
