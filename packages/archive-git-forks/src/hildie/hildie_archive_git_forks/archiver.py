"""Archive GitHub forked repositories."""

import json
import shutil
import subprocess
from pathlib import Path

import requests


def get_github_username() -> str:
    """Get GitHub username from git config."""
    result = subprocess.run(
        ["git", "config", "user.name"],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0 and result.stdout.strip():
        return result.stdout.strip()

    raise RuntimeError(
        "Could not get GitHub username from git config. Run: git config user.name 'your-username'"
    )


class ArchiveForks:
    """Archive forked repositories on GitHub."""

    def __init__(
        self,
        username: str,
        token: str,
        work_dir: str = "./forked_repos",
        archive_dir: str = "./archived_repos",
    ):
        self.username = username
        self.token = token
        self.work_dir = Path(work_dir)
        self.archive_dir = Path(archive_dir)
        self.session = requests.Session()
        self.session.auth = (username, token)

    def setup_directories(self):
        """Create work and archive directories."""
        self.work_dir.mkdir(parents=True, exist_ok=True)
        self.archive_dir.mkdir(parents=True, exist_ok=True)

    def fetch_forked_repos(self) -> list[dict]:
        """Fetch all forked repositories (excluding own repos)."""
        repos = []
        page = 1

        while True:
            url = f"https://api.github.com/users/{self.username}/repos?per_page=100&page={page}"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            data = response.json()
            if not data:
                break

            # Only include forked repos
            for repo in data:
                if repo.get("fork"):
                    repos.append(repo)

            page += 1

        return repos

    def export_repos(self, repos: list[dict], filename: str):
        """Export repos to JSON file, sorted by last updated."""
        # Sort by updated_at, newest first
        sorted_repos = sorted(repos, key=lambda r: r.get("updated_at", ""), reverse=True)

        data = [
            {
                "name": r["name"],
                "clone_url": r["clone_url"],
                "updated_at": r.get("updated_at", ""),
            }
            for r in sorted_repos
        ]
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)

    def load_repos(self, filename: str) -> list[dict]:
        """Load repos from JSON file."""
        with open(filename) as f:
            return json.load(f)

    def load_selected_repos(self, filename: str) -> list[dict]:
        """Load selected repos from JSON file."""
        return self.load_repos(filename)

    def _ssh_url(self, https_url: str) -> str:
        """Convert HTTPS URL to SSH format."""
        return https_url.replace("https://github.com/", "git@github.com:")

    def clone_repo(self, clone_url: str, repo_name: str) -> Path:
        """Clone a repository."""
        local_path = self.work_dir / repo_name

        # Remove existing directory if present
        if local_path.exists():
            shutil.rmtree(local_path)

        ssh_url = self._ssh_url(clone_url)
        result = subprocess.run(
            ["git", "clone", ssh_url, str(local_path)],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            raise RuntimeError(f"Failed to clone {repo_name}: {result.stderr}")

        return local_path

    def archive_repo(self, local_path: Path, repo_name: str) -> Path:
        """Create zip archive of repository."""
        archive_base = self.archive_dir / repo_name
        archive_path = shutil.make_archive(str(archive_base), "zip", local_path)
        return Path(archive_path)

    def make_private(self, repo_name: str):
        """Make repository private on GitHub."""
        url = f"https://api.github.com/repos/{self.username}/{repo_name}"
        response = self.session.patch(url, json={"private": True}, timeout=10)

        if response.status_code == 422:
            raise RuntimeError(
                f"Cannot make {repo_name} private: repo is a fork "
                "(free plans don't support private forks)"
            )

        response.raise_for_status()

    def delete_repo(self, repo_name: str) -> bool:
        """Delete repository from GitHub. Returns True if deleted."""
        url = f"https://api.github.com/repos/{self.username}/{repo_name}"
        response = self.session.delete(url, timeout=10)
        return response.status_code in (204, 404)  # 204=deleted, 404=already gone

    def process_repos(self, repos: list[dict]) -> dict:
        """Clone, archive, and make repos private."""
        results = {"successful": [], "failed": [], "warnings": []}

        for repo in repos:
            repo_name = repo["name"]
            try:
                self.clone_repo(repo["clone_url"], repo_name)
                self.archive_repo(self.work_dir / repo_name, repo_name)

                try:
                    self.make_private(repo_name)
                except RuntimeError as e:
                    if "422" in str(e):
                        results["warnings"].append({"name": repo_name, "reason": str(e)})
                    else:
                        raise

                results["successful"].append(repo_name)
            except RuntimeError as e:
                results["failed"].append({"name": repo_name, "error": str(e)})

        return results

    def delete_repos(self, repos: list[dict]) -> dict:
        """Delete repositories from GitHub."""
        results = {"deleted": [], "failed": []}

        for repo in repos:
            repo_name = repo["name"]
            try:
                if self.delete_repo(repo_name):
                    results["deleted"].append(repo_name)
            except Exception as e:
                results["failed"].append({"name": repo_name, "error": str(e)})

        return results

    def cleanup(self):
        """Remove work directory."""
        if self.work_dir.exists():
            shutil.rmtree(self.work_dir)
