"""Unit tests for utils module."""

import os
from pathlib import Path

import pytest

from dicomsorter.utils import (
    clean_directory_name,
    filename_generator,
    find_unique_filename,
    mkdir_p,
    recursive_string_interpolation,
)


class TestRecursiveMakeDirectory:
    """Test recursive folder creation"""

    def test_when_the_folder_exists(self, tmp_path: Path) -> None:
        """There should be no errors if the folder exists."""
        assert tmp_path.exists()
        mkdir_p(tmp_path)

    def test_when_no_permission(self, tmp_path: Path) -> None:
        """An error should be raised when the directory is not writable."""
        tmp_path.chmod(0)
        desired = tmp_path.joinpath("folder")

        with pytest.raises(Exception):
            mkdir_p(desired)

    def test_when_subfolder_does_not_exist(self, tmp_path: Path) -> None:
        """A subfolder is created successfully."""
        new_directory = tmp_path.joinpath("new_folder")
        assert not new_directory.exists()

        mkdir_p(new_directory)

        assert new_directory.exists()

    def test_when_nested_folder_does_not_exist(self, tmp_path: Path) -> None:
        """Nested subfolders are created successfully."""
        nested = tmp_path.joinpath("folder1", "folder2", "folder3")
        assert not nested.exists()

        mkdir_p(nested)

        assert nested.exists()


class TestFindUniqueFilename:
    """Test unique filename generator"""

    def test_when_file_does_not_exist(self, tmp_path: Path) -> None:
        """The original filename is returned if it is unique."""
        filename = tmp_path.joinpath("does_not_exist.output")
        output = find_unique_filename(filename)

        assert output == filename
        assert filename.exists()

    def test_when_commit_is_false(self, tmp_path: Path) -> None:
        """No file is created when commit is False."""
        filename = tmp_path.joinpath("does_not_exist.output")
        output = find_unique_filename(filename, commit=False)

        assert output == filename
        assert not filename.exists()

    def test_when_file_exists(self, tmp_path: Path) -> None:
        """A file with a suffix is created when the file exists."""
        filename = tmp_path.joinpath("exists.output")
        filename.touch()

        expected = tmp_path.joinpath("exists (2).output")

        output = find_unique_filename(filename)

        assert output == expected
        assert expected.exists()

    def test_when_multiple_files_exist(self, tmp_path: Path) -> None:
        """A file with a suffix is created when multiple versions of the file exist."""
        filename = tmp_path.joinpath("exists.output")
        filename.touch()

        filename2 = tmp_path.joinpath("exists (2).output")
        filename2.touch()

        expected = tmp_path.joinpath("exists (3).output")

        output = find_unique_filename(filename)

        assert output == expected
        assert expected.exists()


class TestFilenameGenerator:
    """Test generator for creating unique filenames."""

    def test_when_there_is_no_extension(self) -> None:
        """There are no issues when there is no extension."""
        input_filename = Path(os.path.join("this", "is", "a", "path"))
        generator = filename_generator(input_filename)

        second_filename = input_filename.parent.joinpath("path (2)")

        outputs = [next(generator) for _ in range(2)]
        expected = [input_filename, second_filename]

        assert outputs == expected

    def test_with_a_single_iteration(self) -> None:
        """The original filename should be returned on the first iteration."""
        input_filename = Path(os.path.join("this", "is", "a", "file.name"))
        generator = filename_generator(input_filename)
        assert next(generator) == input_filename

    def test_with_multiple_iterations(self) -> None:
        """The filenames have incrementing suffixes."""
        input_filename = Path(os.path.join("this", "is", "a", "file.name"))
        generator = filename_generator(input_filename)

        expected = [input_filename]

        for k in range(9):
            expected.append(
                Path(os.path.join("this", "is", "a", "file (%d).name" % (k + 2)))
            )

        outputs = [next(generator) for _ in range(10)]
        assert outputs == expected


class TestCleanDirectoryName:
    """Test function for sanitizing directory/file names."""

    def test_with_valid_chars(self) -> None:
        """Check that a valid filename remains unchanged."""
        filepath = "filename"
        assert clean_directory_name(filepath) == filepath

    def test_with_invalid_chars(self) -> None:
        """Ensure that invalid characters are replaced by an underscore."""

        invalid_chars = ':|<>"?*'

        for char in invalid_chars:
            filepath = f"file{char}name"
            assert clean_directory_name(filepath) == "file_name"

    def test_replacement_char(self) -> None:
        """If we provide a replacement character, it should be used."""

        invalid_chars = ':|<>"?*'

        for char in invalid_chars:
            filepath = f"file{char}name"
            assert clean_directory_name(filepath, "-") == "file-name"


class TestRecursiveStringInterpolation:
    """Test functionality of performing string interpolation recursively."""

    def test_with_no_interpolation(self) -> None:
        """No interpolation causes no substution."""

        string = "123abcABC890"
        assert recursive_string_interpolation(string, {}) == string

    def test_single_interpolation(self) -> None:
        """Test normal string interpolation."""

        string = "123%(Key)s456"
        params = {"Key": "Value"}

        assert recursive_string_interpolation(string, params) == string % params

    def test_recursive_interpolation(self) -> None:
        """Ensure that string interpolation is performed twice."""

        string = "123%(Key)s456"
        params = {"Key": "Key2", "Key2": "Value"}

        expected = (string % params) % params

        assert recursive_string_interpolation(string, params) == expected

    def test_recursive_depth_limit(self) -> None:
        """Ensure that interpolation stops at a certain depth."""

        string = "123%(Key)s456"

        # Set the params so it loops infinitely
        params = {"Key": "%(Key)s"}

        assert recursive_string_interpolation(string, params) == string
