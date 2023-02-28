"""Unit tests for utils module."""

import os
import pytest

from pathlib import Path

from dicomsorter.utils import (
    clean_directory_name,
    filename_generator,
    find_unique_filename,
    mkdir_p,
    recursive_string_interpolation,
)


class TestRecursiveMakeDirectory:
    """Test recursive folder creation"""

    def test_when_the_folder_exists(self, tmp_path):
        """There should be no errors if the folder exists."""
        assert tmp_path.exists()
        mkdir_p(str(tmp_path))

    def test_when_no_permission(self, tmp_path):
        """An error should be raised when the directory is not writable."""
        tmp_path.chmod(0)
        desired = tmp_path.joinpath("folder")

        with pytest.raises(Exception):
            mkdir_p(str(desired))

    def test_when_subfolder_does_not_exist(self, tmp_path):
        """A subfolder is created successfully."""
        new_directory = tmp_path.joinpath("new_folder")
        assert not new_directory.exists()

        mkdir_p(str(new_directory))

        assert new_directory.exists()

    def test_when_nested_folder_does_not_exist(self, tmp_path):
        """Nested subfolders are created successfully."""
        nested = tmp_path.joinpath("folder1", "folder2", "folder3")
        assert not nested.exists()

        mkdir_p(str(nested))

        assert nested.exists()


class TestFindUniqueFilename:
    """Test unique filename generator"""

    def test_when_file_does_not_exist(self, tmp_path):
        """The original filename is returned if it is unique."""
        filename = os.path.join(str(tmp_path), "does_not_exist.output")
        output = find_unique_filename(filename)

        assert output == filename
        assert os.path.exists(filename)

    def test_when_commit_is_false(self, tmp_path):
        """No file is created when commit is False."""
        filename = os.path.join(str(tmp_path), "does_not_exist.output")
        output = find_unique_filename(filename, commit=False)

        assert output == filename
        assert not os.path.exists(filename)

    def test_when_file_exists(self, tmp_path):
        """A file with a suffix is created when the file exists."""
        filename = os.path.join(str(tmp_path), "exists.output")
        Path(filename).touch()

        expected = os.path.join(str(tmp_path), "exists (2).output")

        output = find_unique_filename(filename)

        assert output == expected
        assert os.path.exists(expected)

    def test_when_multiple_files_exist(self, tmp_path):
        """A file with a suffix is created when multiple versions of the file exist."""
        filename = os.path.join(str(tmp_path), "exists.output")
        Path(filename).touch()

        filename2 = os.path.join(str(tmp_path), "exists (2).output")
        Path(filename2).touch()

        expected = os.path.join(str(tmp_path), "exists (3).output")

        output = find_unique_filename(filename)

        assert output == expected
        assert os.path.exists(expected)


class TestFilenameGenerator:
    """Test generator for creating unique filenames."""

    def test_when_there_is_no_extension(self):
        """There are no issues when there is no extension."""
        input_filename = os.path.join("this", "is", "a", "path")
        generator = filename_generator(input_filename)

        outputs = [next(generator) for _ in range(2)]
        expected = [input_filename, input_filename + " (2)"]

        assert outputs == expected

    def test_with_a_single_iteration(self):
        """The original filename should be returned on the first iteration."""
        input_filename = os.path.join("this", "is", "a", "file.name")
        generator = filename_generator(input_filename)
        assert next(generator) == input_filename

    def test_with_multiple_iterations(self):
        """The filenames have incrementing suffixes."""
        input_filename = os.path.join("this", "is", "a", "file.name")
        generator = filename_generator(input_filename)

        expected = [input_filename]

        for k in range(9):
            expected.append(os.path.join("this", "is", "a", "file (%d).name" % (k + 2)))

        outputs = [next(generator) for _ in range(10)]
        assert outputs == expected


class TestCleanDirectoryName:
    """Test function for sanitizing directory/file names."""

    def test_with_valid_chars(self):
        """Check that a valid filename remains unchanged."""
        filepath = "filename"
        assert clean_directory_name(filepath) == filepath

    def test_with_invalid_chars(self):
        """Ensure that invalid characters are replaced by an underscore."""

        invalid_chars = ':|<>"?*'

        for char in invalid_chars:
            filepath = "file%sname" % char
            assert clean_directory_name(filepath) == "file_name"

    def test_replacement_char(self):
        """If we provide a replacement character, it should be used."""

        invalid_chars = ':|<>"?*'

        for char in invalid_chars:
            filepath = "file%sname" % char
            assert clean_directory_name(filepath, "-") == "file-name"


class TestRecursiveStringInterpolation:
    """Test functionality of performing string interpolation recursively."""

    def test_with_no_interpolation(self):
        """No interpolation causes no substution."""

        string = "123abcABC890"
        assert recursive_string_interpolation(string, {}) == string

    def test_single_interpolation(self):
        """Test normal string interpolation."""

        string = "123%(Key)s456"
        params = {"Key": "Value"}

        assert recursive_string_interpolation(string, params) == string % params

    def test_recursive_interpolation(self):
        """Ensure that string interpolation is performed twice."""

        string = "123%(Key)s456"
        params = {"Key": "Key2", "Key2": "Value"}

        expected = (string % params) % params

        assert recursive_string_interpolation(string, params) == expected

    def test_recursive_depth_limit(self):
        """Ensure that interpolation stops at a certain depth."""

        string = "123%(Key)s456"

        # Set the params so it loops infinitely
        params = {"Key": "%(Key)s"}

        assert recursive_string_interpolation(string, params) == string
