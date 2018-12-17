import errno
import os
import re

from pathlib import Path

RE_INVALID_CHARS = re.compile('[\\\\/\:\*\?\"\<\>\|]+')


def clean_directory_name(directory, replacement='_'):
    """Scrub invalid characters from a filename."""

    return re.sub(RE_INVALID_CHARS, replacement, directory)


def clean_filepath(filepath, replacement='_'):
    """Scrub invalid characters from a full file path."""

    filepath_parts = filepath.split(os.path.sep)
    clean_parts = [clean_directory_name(part, replacement) for part in filepath_parts]
    return os.path.join(*clean_parts)


def filename_generator(filename):
    """Creates filenames with increasing (version) number suffixes."""
    yield filename

    name, extension = os.path.splitext(filename)

    counter = 2

    while True:
        yield ''.join([name, ' (', str(counter), ')', extension])
        counter += 1


def find_unique_filename(filename, commit=True):
    """Find an un-used filename and create it (if specified)."""
    generator = filename_generator(filename)

    for filename in generator:
        if os.path.exists(filename):
            continue

        if commit:
            Path(filename).touch()

        return filename


def groups_of(iterable, n):
    """Group an iterable into groups of N items."""
    return map(None, *[iter(iterable), ] * n)


def mkdir_p(path):
    """Recursively make directories and ignore if they exist."""
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def recursive_string_interpolation(string, obj, max_depth=5):
    """Recursively perform string interpolation."""

    for iteration in range(max_depth):
        previous_string = string
        string = string % obj

        if string == previous_string:
            break

    return string
