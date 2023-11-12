from pathlib import Path

FILES_FOLDER = Path("static")


class UnsupportedFolderForLaunchTest(Exception):
    # Raised when test is launched from wrong folder
    pass


def generate_right_path_to_test_file(filename: str) -> Path:

    """Correct file path for test

    Parameters
    ----------
    filename : str
        Filename

    Returns
    -------
    path : Path
        Return right path
    """

    relative_path = FILES_FOLDER.joinpath(filename)
    cwd = Path.cwd()
    if cwd.match("*/tests"):
        return cwd.joinpath(relative_path)
    elif cwd.match("*/formal-lang-course"):
        return cwd.joinpath("tests").joinpath(relative_path)
    elif cwd.match("*/project"):
        return cwd.parent.joinpath("tests").joinpath(relative_path)

    raise UnsupportedFolderForLaunchTest
