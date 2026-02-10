"""Tests for my_library module."""

from cosi.cosi_library import add, multiply


class TestMath:
    """Test mathematical operations."""

    def test_add(self):
        """Test addition function."""
        assert add(2, 3) == 5
        assert add(0, 0) == 0
        assert add(-1, 1) == 0

    def test_add_negative(self):
        """Test addition with negative numbers."""
        assert add(-5, -3) == -8
        assert add(10, -5) == 5

    def test_multiply(self):
        """Test multiplication function."""
        assert multiply(2, 3) == 6
        assert multiply(0, 100) == 0
        assert multiply(-2, 3) == -6

    def test_multiply_negative(self):
        """Test multiplication with negative numbers."""
        assert multiply(-2, -3) == 6
        assert multiply(5, -2) == -10
