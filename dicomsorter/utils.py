import errno
import os
import re
from pathlib import Path
from typing import Any, Generator

RE_INVALID_CHARS = re.compile('[\\\\/:*?"<>|]+')


def clean_directory_name(directory: str, replacement: str = "_") -> str:
    """Scrub invalid characters from a filename."""
    return re.sub(RE_INVALID_CHARS, replacement, directory)


def filename_generator(filename: Path) -> Generator[Path, None, None]:
    """Creates filenames with increasing (version) number suffixes."""
    yield filename

    name, extension = os.path.splitext(filename)
    extension = extension or ""

    counter = 2

    while True:
        yield Path("".join([name, " (", str(counter), ")", extension]))
        counter += 1


def find_unique_filename(filename: Path, commit: bool = True) -> Path:
    """Find an un-used filename and create it (if specified)."""
    generator = filename_generator(filename)

    for filename in generator:
        if filename.exists():
            continue

        if commit:
            Path(filename).touch()

        return filename

    raise Exception("Should never be reached")


def mkdir_p(path: Path) -> None:
    """Recursively make directories and ignore if they exist."""
    try:
        path.mkdir(parents=True)
    except OSError as exception:
        if exception.errno == errno.EEXIST and path.is_dir():
            pass
        else:
            raise


def recursive_string_interpolation(
    string: str,
    obj: Any,
    max_depth: int = 5,
) -> str:
    """Recursively perform string interpolation."""

    for iteration in range(max_depth):
        previous_string = string
        string = string % obj

        if string == previous_string:
            break

    return string
