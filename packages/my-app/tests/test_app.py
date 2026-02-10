"""Tests for my_app module."""

from cosi.cosi_app import process_numbers


class TestApp:
    """Test application functionality."""

    def test_process_numbers_basic(self):
        """Test processing a basic list of numbers."""
        result = process_numbers([1, 2, 3])
        assert result["sum"] == 6
        assert result["product"] == 6

    def test_process_numbers_with_zero(self):
        """Test processing numbers including zero."""
        result = process_numbers([2, 0, 5])
        assert result["sum"] == 7
        assert result["product"] == 0

    def test_process_numbers_single(self):
        """Test processing a single number."""
        result = process_numbers([5])
        assert result["sum"] == 5
        assert result["product"] == 5

    def test_process_numbers_empty(self):
        """Test processing an empty list."""
        result = process_numbers([])
        assert result["sum"] == 0
        assert result["product"] == 0

    def test_process_numbers_negative(self):
        """Test processing negative numbers."""
        result = process_numbers([-2, 3, -1])
        assert result["sum"] == 0
        assert result["product"] == 6
