"""CLI for archiving GitHub forked repositories."""

import os

import click

from .archiver import ArchiveForks, get_github_username


def get_env_or_fail(var_name: str) -> str:
    """Get environment variable or raise exception if not set."""
    value = os.getenv(var_name)
    if not value:
        raise Exception(f"{var_name} is not set")
    return value


def get_token() -> str:
    """Get GitHub token from environment."""
    return get_env_or_fail("GITHUB_TOKEN")


@click.group()
def cli():
    """Archive and manage GitHub forked repositories."""


@cli.command()
@click.option("--work-dir", default="./forked_repos")
@click.option("--archive-dir", default="./archived_repos")
@click.option("--flat-file", default="forked_repos.json")
def fetch(work_dir, archive_dir, flat_file):
    """Fetch all your forked repos."""
    try:
        token = get_token()
        username = get_github_username()
    except Exception as e:
        raise click.ClickException(str(e)) from e

    click.echo(f"GitHub user: {username}")

    manager = ArchiveForks(username, token, work_dir, archive_dir)
    manager.setup_directories()

    click.echo("Fetching forked repos...")
    repos = manager.fetch_forked_repos()
    click.echo(f"Found {len(repos)} forked repositories\n")

    # Sort by updated date and display
    sorted_repos = sorted(repos, key=lambda r: r.get("updated_at", ""), reverse=True)
    click.echo("Recent repos:")
    for repo in sorted_repos[:10]:  # Show top 10
        updated = repo.get("updated_at", "unknown")[:10]  # Just the date part
        click.echo(f"  {repo['name']:40} ({updated})")
    if len(repos) > 10:
        click.echo(f"  ... and {len(repos) - 10} more")

    manager.export_repos(repos, flat_file)
    click.echo(f"\nExported {len(repos)} repos to {flat_file}")
    click.echo("Edit the file to select which repos to archive")
    click.echo("Then run: archive-git-forks process")


@cli.command()
@click.option("--work-dir", default="./forked_repos")
@click.option("--archive-dir", default="./archived_repos")
@click.option("--flat-file", default="forked_repos.json")
def process(work_dir, archive_dir, flat_file):
    """Clone, archive, and make repos private."""
    try:
        token = get_token()
        username = get_github_username()
    except Exception as e:
        raise click.ClickException(str(e)) from e

    manager = ArchiveForks(username, token, work_dir, archive_dir)
    manager.setup_directories()

    try:
        repos = manager.load_selected_repos(flat_file)
    except FileNotFoundError:
        raise click.ClickException(f"{flat_file} not found. Run 'fetch' first.") from None

    if not repos:
        raise click.ClickException("No repos to process")

    click.echo(f"Processing {len(repos)} selected repositories\n")

    results = manager.process_repos(repos)

    # Show results
    for name in results["successful"]:
        click.echo(f"✓ {name}")

    for warning in results.get("warnings", []):
        click.echo(f"⚠ {warning['name']}: {warning['reason']}")

    for failed in results["failed"]:
        click.echo(f"✗ {failed['name']}: {failed['error']}")

    click.echo(
        f"\nDone: {len(results['successful'])} successful, "
        f"{len(results.get('warnings', []))} skipped, "
        f"{len(results['failed'])} failed"
    )


@cli.command()
@click.option("--flat-file", default="forked_repos.json")
@click.option("--force", is_flag=True, help="Skip confirmation")
def delete(flat_file, force):
    """Delete forked repos from GitHub (irreversible!)."""
    try:
        token = get_token()
        username = get_github_username()
    except Exception as e:
        raise click.ClickException(str(e)) from e

    manager = ArchiveForks(username, token)

    try:
        repos = manager.load_repos(flat_file)
    except FileNotFoundError:
        raise click.ClickException(f"{flat_file} not found") from None

    if not repos:
        raise click.ClickException("No repos to delete")

    click.echo("Repos to delete:")
    for repo in repos:
        click.echo(f"  - {repo['name']}")

    if not force and not click.confirm(f"\nDelete {len(repos)} repos? This cannot be undone!"):
        click.echo("Cancelled")
        return

    results = manager.delete_repos(repos)

    for name in results["deleted"]:
        click.echo(f"✓ {name} deleted")

    for failed in results["failed"]:
        click.echo(f"✗ {failed['name']}: {failed['error']}")

    click.echo(f"\nDeleted: {len(results['deleted'])}, Failed: {len(results['failed'])}")


@cli.command()
@click.option("--work-dir", default="./forked_repos")
def cleanup(work_dir):
    """Delete local cloned repos."""
    import shutil
    from pathlib import Path

    path = Path(work_dir)
    if not path.exists():
        click.echo("Directory does not exist")
        return

    if click.confirm(f"Delete {work_dir}?"):
        shutil.rmtree(path)
        click.echo(f"Deleted {work_dir}")


if __name__ == "__main__":
    cli()
