import os
import re

RE_INVALID_CHARS = re.compile('[\\\\/\:\*\?\"\<\>\|]+')


def clean_directory_name(directory, replacement='_'):
    """Scrub invalid characters from a filename."""

    return re.sub(RE_INVALID_CHARS, replacement, directory)


def clean_filepath(filepath, replacement='_'):
    """Scrub invalid characters from a full file path."""

    filepath_parts = filepath.split(os.path.sep)
    clean_parts = [clean_directory_name(part, replacement) for part in filepath_parts]
    return os.path.join(*clean_parts)


def groups_of(iterable, n):
    """Group an iterable into groups of N items."""
    return map(None, *[iter(iterable), ] * n)


def recursive_string_interpolation(string, obj, max_depth=5):
    """Recursively perform string interpolation."""

    for iteration in range(max_depth):
        previous_string = string
        string = string % obj

        if string == previous_string:
            break

    return string
