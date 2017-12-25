"""Unit tests for utils module."""

import os

from dicomsorter.utils import groups_of


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
