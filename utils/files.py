import os
import os.path as path


def is_empty(file: str) -> bool:
    """
    Function to check if a file is empty or not

    Returns True if the file is empty, the file has an empty line,
    or if the file doesn't exist

    Parameters
    ----------
    file
        Name of the file

    Returns
    -------
    bool
        True if file is empty, false otherwise
    """
    return not path.exists(file) or os.stat(file).st_size <= 1
