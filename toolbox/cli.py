# cli.py

"""Developer toolbox CLI - main orchestrator."""
import typer
from typing import List
from toolbox import taskman, publisher

app = typer.Typer(help="Developer toolbox - task management and utilities")


@app.command()
def list():
    """List all open tasks."""
    taskman.list_tasks()


@app.command()
def bug():
    """Create a new bug task."""
    taskman.create_bug()


@app.command()
def task():
    """Create a new task."""
    taskman.create_task_issue()


@app.command()
def idea():
    """Create a new idea task."""
    taskman.create_idea()


@app.command()
def resolve(
    issue_numbers: List[int] = typer.Argument(..., help="Task numbers to resolve")
):
    """Resolve (close) tasks by number."""
    taskman.resolve_tasks(issue_numbers)


@app.command()
def delete(
    issue_numbers: List[int] = typer.Argument(..., help="Task numbers to delete")
):
    """Delete tasks permanently by number (uses GraphQL API)."""
    taskman.delete_tasks(issue_numbers)


@app.command()
def release(
    bump_type: str = typer.Argument(help="Version bump type: patch, minor, or major"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Simulate release without making changes"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt")
):
    """Bump version and publish to PyPI."""
    pub = publisher.Publisher(dry_run=dry_run)
    pub.release(bump_type, skip_confirm=yes)


if __name__ == "__main__":
    app()
