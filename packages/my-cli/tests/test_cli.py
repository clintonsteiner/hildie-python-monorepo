"""Tests for my_cli module."""

from click.testing import CliRunner
from hildie.hildie_cli.main import cli


class TestCLI:
    """Test CLI commands."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_add_command(self):
        """Test the add command."""
        result = self.runner.invoke(cli, ["add-numbers", "5", "3"])
        assert result.exit_code == 0
        assert "5 + 3 = 8" in result.output

    def test_multiply_command(self):
        """Test the multiply command."""
        result = self.runner.invoke(cli, ["multiply-numbers", "4", "7"])
        assert result.exit_code == 0
        assert "4 x 7 = 28" in result.output

    def test_sum_all_command(self):
        """Test the sum-all command."""
        result = self.runner.invoke(cli, ["sum-all", "1", "2", "3", "4"])
        assert result.exit_code == 0
        assert "Sum: 10" in result.output

    def test_multiply_all_command(self):
        """Test the multiply-all command."""
        result = self.runner.invoke(cli, ["multiply-all", "2", "3", "4"])
        assert result.exit_code == 0
        assert "Product: 24" in result.output
