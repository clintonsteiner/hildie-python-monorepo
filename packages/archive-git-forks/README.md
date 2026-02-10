# archive-git-forks

Archive GitHub forked repositories locally and make them private.

## Overview

This tool helps you manage forked repositories by:

1. Fetching all your forks from GitHub
2. Exporting them to a JSON file for manual review
3. Cloning selected repositories locally
4. Creating zip archives of each fork
5. Making the repositories private on GitHub

## Installation

```bash
uv pip install -e .
```

## Setup

1. **Configure SSH for GitHub:**
   - Add your SSH public key to GitHub: https://github.com/settings/keys
   - Test SSH connection: `ssh -T git@github.com`
   - You should see: "Hi username! You've successfully authenticated..."

2. **Configure git user (for username detection):**

   ```bash
   git config --global user.name "your-github-username"
   ```

   The tool will auto-detect your GitHub username from this setting.

3. **Generate a GitHub Personal Access Token:**
   - Go to https://github.com/settings/tokens
   - Create a new token with `repo` and `delete_repo` scopes
   - Copy the token

4. **Set environment variable:**

   ```bash
   export GITHUB_TOKEN="your_personal_access_token"
   ```

   Example:

   ```bash
   export GITHUB_TOKEN="ghp_xxxxxxxxxxxxxxxxxxxx"
   archive-git-forks fetch
   ```

## Usage

### Step 1: Fetch all forks

```bash
archive-git-forks fetch
```

This creates `forked_repos.json` with all your forks. Edit this file to remove any repos you don't want to archive.

### Step 2: Process selected repos

After editing `forked_repos.json`:

```bash
archive-git-forks process
```

The tool will:

- Clone each repository
- Create zip archives in `./archived_repos/`
- Make each repository private on GitHub

### Step 3: Clean up (optional)

```bash
archive-git-forks cleanup
```

Remove the cloned repositories after archiving.

## Commands

### fetch

Fetch all forked repositories and export to JSON file.

```bash
archive-git-forks fetch [OPTIONS]

Options:
  --work-dir TEXT     Directory to clone repos into (default: ./forked_repos)
  --archive-dir TEXT  Directory to store zip archives (default: ./archived_repos)
  --flat-file TEXT    JSON file for repo selection (default: forked_repos.json)
```

### process

Process selected repositories: clone, archive, and make private.

```bash
archive-git-forks process [OPTIONS]

Options:
  --work-dir TEXT     Directory to clone repos into (default: ./forked_repos)
  --archive-dir TEXT  Directory to store zip archives (default: ./archived_repos)
  --flat-file TEXT    JSON file with selected repos (default: forked_repos.json)
```

### cleanup

Remove the work directory after archiving.

```bash
archive-git-forks cleanup [OPTIONS]

Options:
  --work-dir TEXT     Directory to clean up (default: ./forked_repos)
```

### delete

Delete forked repositories from your GitHub account.

⚠️ **WARNING**: This is irreversible! Deleted repos cannot be recovered.

```bash
archive-git-forks delete [OPTIONS]

Options:
  --flat-file TEXT    JSON file with repos to delete (default: forked_repos.json)
  --force            Skip confirmation prompt
```

Example:

```bash
# Review and confirm before deleting
archive-git-forks delete

# Force delete without confirmation
archive-git-forks delete --force
```

## Example Workflow

```bash
# One-time setup
git config --global user.name "octocat"
export GITHUB_TOKEN="ghp_xxxxxxxxxxxxxxxxxxxx"

# Fetch all your forks (creates forked_repos.json)
archive-git-forks fetch

# Edit forked_repos.json to remove unwanted repos
vim forked_repos.json

# Process selected repos (clone, archive, make private)
archive-git-forks process

# Clean up work directory
archive-git-forks cleanup
```

## Notes

- **SSH Required**: Uses SSH for cloning (more secure than HTTPS + token)
- **Username Auto-Detection**: Extracts GitHub username from `git config user.name`
- **Token Scope**: Only needs `repo` scope for API calls
- **Full History**: Repos are cloned with full git history
- **Archive Format**: Archives are created as zip files
- **Privacy Limitations**: Some repos can't be made private (e.g., forks on free plans). The tool will archive them anyway and report a warning.
- **Re-runs Safe**: If a repo was already cloned, the tool will remove the old directory and re-clone
- **Cleanup**: You can safely delete the `./forked_repos/` directory after archiving if you no longer need it

## Troubleshooting

**"Failed to clone ... permission denied (publickey)"**

- SSH keys aren't configured for GitHub
- Run: `ssh -T git@github.com` to test
- Add your public key to https://github.com/settings/keys

**"Cannot make repo private (422 Unprocessable Entity)"**

- You can't make forks private on free plans
- The repo is still archived successfully
- You may need a paid GitHub plan to make forks private

**"Could not determine GitHub username"**

- Set your git user: `git config --global user.name "your-username"`
- Or add to SSH config: `~/.ssh/config`

## Development

```bash
uv sync
pytest
```
