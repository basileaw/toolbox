# cli.py

"""Developer toolbox CLI - main orchestrator."""
import typer
from typing import List
from toolbox import taskman

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


if __name__ == "__main__":
    app()
