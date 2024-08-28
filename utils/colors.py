# colors from https://yeun.github.io/open-color/ingredients.html
SUCCESS = (55, 178, 77)
WARNING = (245, 159, 0)
DANGER = (240, 62, 62)


def change_color(text: str, color: tuple[int, int, int]) -> str:
    """
    Function to change the color of a string when printing it to the
    stdout

    Returns a string with ANSI code to change a color when printing it
    to the stdout

    Parameters
    ----------
    text
        The text to change the color
    color
        The color that changes the text color in RGB format

    Returns
    -------
    str
        A string with the text changed to show a different color when
        printed to the stdout
    """
    return f"\033[38;2;{color[0]};{color[1]};{color[2]}m{text}\033[0m"


if __name__ == "__main__":
    print(change_color("aaa", SUCCESS))
    print(change_color("aaa", WARNING))
    print(change_color("aaa", DANGER))
    print("aaa")
