"""Tests for archive_git_forks CLI."""

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from archive_git_forks.main import cli


class TestFetchCommand:
    """Test the fetch command."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    @patch("archive_git_forks.main.get_github_username")
    @patch("archive_git_forks.main.get_env_or_fail")
    @patch("archive_git_forks.main.ArchiveForks")
    def test_fetch_command_success(self, mock_archiver_class, mock_env, mock_username):
        """Test successful fetch command."""
        # Setup mocks
        mock_username.return_value = "testuser"
        mock_env.side_effect = lambda x: "testuser" if x == "GITHUB_USERNAME" else "token123"
        mock_archiver = MagicMock()
        mock_archiver_class.return_value = mock_archiver
        mock_archiver.fetch_forked_repos.return_value = [
            {"name": "repo1", "clone_url": "https://github.com/testuser/repo1.git"},
            {"name": "repo2", "clone_url": "https://github.com/testuser/repo2.git"},
        ]

        # Run command
        with tempfile.TemporaryDirectory() as tmpdir:
            flat_file = Path(tmpdir) / "repos.json"
            result = self.runner.invoke(
                cli,
                ["fetch", "--flat-file", str(flat_file)],
                env={"GITHUB_USERNAME": "testuser", "GITHUB_TOKEN": "token123"},
            )

            # Assertions
            assert result.exit_code == 0
            assert "Found 2 forked repositories" in result.output
            assert "Exported 2 repos to" in result.output

    @patch("archive_git_forks.main.get_env_or_fail")
    def test_fetch_command_missing_credentials(self, mock_env):
        """Test fetch command with missing credentials."""
        mock_env.side_effect = Exception("GITHUB_USERNAME is not set")

        result = self.runner.invoke(cli, ["fetch"])
        assert result.exit_code != 0


class TestProcessCommand:
    """Test the process command."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    @patch("archive_git_forks.main.get_github_username")
    @patch("archive_git_forks.main.get_env_or_fail")
    @patch("archive_git_forks.main.ArchiveForks")
    def test_process_command_success(self, mock_archiver_class, mock_env, mock_username):
        """Test successful process command."""
        # Setup mocks
        mock_username.return_value = "testuser"
        mock_env.side_effect = lambda x: "testuser" if x == "GITHUB_USERNAME" else "token123"

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test repos file
            repos_file = Path(tmpdir) / "repos.json"
            repos_data = [
                {"name": "repo1", "clone_url": "https://github.com/testuser/repo1.git"},
                {"name": "repo2", "clone_url": "https://github.com/testuser/repo2.git"},
            ]
            with open(repos_file, "w") as f:
                json.dump(repos_data, f)

            # Setup mocks
            mock_archiver = MagicMock()
            mock_archiver_class.return_value = mock_archiver
            mock_archiver.load_selected_repos.return_value = repos_data
            mock_archiver.process_repos.return_value = {
                "successful": ["repo1", "repo2"],
                "failed": [],
            }

            # Run command
            result = self.runner.invoke(
                cli,
                ["process", "--flat-file", str(repos_file)],
                env={"GITHUB_USERNAME": "testuser", "GITHUB_TOKEN": "token123"},
            )

            # Assertions
            assert result.exit_code == 0
            assert "Processing 2 selected repositories" in result.output
            assert "✓ repo1" in result.output
            assert "✓ repo2" in result.output

    def test_process_command_missing_file(self):
        """Test process command with missing repos file."""
        result = self.runner.invoke(
            cli,
            ["process", "--flat-file", "/nonexistent/file.json"],
            env={"GITHUB_USERNAME": "testuser", "GITHUB_TOKEN": "token123"},
        )

        assert result.exit_code != 0


class TestCleanupCommand:
    """Test the cleanup command."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_cleanup_command_nonexistent_dir(self):
        """Test cleanup command with nonexistent directory."""
        result = self.runner.invoke(
            cli,
            ["cleanup", "--work-dir", "/nonexistent/dir"],
        )

        assert result.exit_code == 0
        assert "Directory does not exist" in result.output

    def test_cleanup_command_with_confirmation(self):
        """Test cleanup command with user confirmation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_dir = Path(tmpdir) / "to_delete"
            test_dir.mkdir()
            (test_dir / "test_file.txt").write_text("test")

            result = self.runner.invoke(
                cli,
                ["cleanup", "--work-dir", str(test_dir)],
                input="y\n",
            )

            assert result.exit_code == 0
            assert "Deleted" in result.output
            assert not test_dir.exists()
