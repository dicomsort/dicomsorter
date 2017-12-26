"""Unit tests for utils module."""

import os

from dicomsorter.utils import (
    groups_of,
    clean_filepath,
    recursive_string_interpolation
)


class TestGroupsOf:
    """Test groups_of functionality."""

    def test_empty_array(self):
        """Check that an empty input yields an empty output."""
        assert groups_of([], 10) == []

    def test_scalar(self):
        """Check that groups of one yield an array of scalars."""
        assert groups_of([1,2], 1) == [1, 2]

    def test_divisible(self):
        """Check that an array can be broken into equal sized groups."""
        array = [1, 2, 3, 4, 5, 6]
        assert groups_of(array, 2) == [(1, 2), (3, 4), (5, 6)]

    def test_remainders(self):
        """Check that padding slots are filled with None."""
        array = [1, 2, 3, 4, 5, 6]
        assert groups_of(array, 4) == [(1, 2, 3, 4), (5, 6, None, None)]


class TestCleanFilepath:
    """Test function for sanitizing file paths."""

    def test_with_valid_chars(self):
        """Check that a valid path remains unchanged."""
        filepath = os.path.join('Users', 'testuser', 'folder', 'file')
        assert clean_filepath(filepath) == filepath

    def test_with_invalid_chars(self):
        """Ensure that invalid characters are replaced by an underscore."""

        invalid_chars = ':|<>"?*'

        for char in invalid_chars:
            filepath = os.path.join('Users%s' % char,
                                    'test%suser' % char,
                                    'file%sname' % char)

            expected = os.path.join('Users_', 'test_user', 'file_name')

            assert clean_filepath(filepath) == expected

    def test_replacement_char(self):
        """If we provide a replacement character, it should be used."""

        invalid_chars = ':|<>"?*'

        for char in invalid_chars:
            filepath = os.path.sep.join(['Users%s' % char,
                                         'test%suser' % char,
                                         'file%sname' % char])

            expected = os.path.join('Users-', 'test-user', 'file-name')

            assert clean_filepath(filepath, '-') == expected


class TestRecursiveStringInterpolation:
    """Test functionality of performing string interpolation recursively."""

    def test_with_no_interpolation(self):
        """No interpolation causes no substution."""

        string = '123abcABC890'
        assert recursive_string_interpolation(string, {}) == string


    def test_single_interpolation(self):
        """Test normal string interpolation."""

        string = '123%(Key)s456'
        params = { 'Key': 'Value' }

        assert recursive_string_interpolation(string, params) == string % params

    def test_recursive_interpolation(self):
        """Ensure that string interpolation is performed twice."""

        string = '123%(Key)s456'
        params = { 'Key': 'Key2', 'Key2': 'Value' }

        expected = (string % params) % params

        assert recursive_string_interpolation(string, params) == expected

    def test_recursive_depth_limit(self):
        """Ensure that interpolation stops at a certain depth."""

        string = '123%(Key)s456'

        # Set the params so it loops infinitely
        params = { 'Key': '%(Key)s' }

        assert recursive_string_interpolation(string, params) == string
