# issue-manager/issue_manager/cli.py
"""GitHub issue management CLI tool."""
import os
import sys
import re
from typing import Optional, List
import requests
import typer
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = typer.Typer(help="GitHub issue management")
console = Console()

# GitHub API
GITHUB_API = "https://api.github.com"


def get_github_token() -> str:
    """Get GitHub token from environment."""
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        console.print("[red]Error: GITHUB_TOKEN environment variable not set[/red]")
        console.print("Please set your GitHub token in .env file or environment")
        sys.exit(1)
    return token


def get_repo_info() -> str:
    """Extract repository owner/name from git remote."""
    import subprocess

    try:
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            capture_output=True,
            text=True,
            check=True,
        )
        repo_url = result.stdout.strip()
    except subprocess.CalledProcessError:
        console.print(
            "[red]Error: Not a git repository or no remote origin found[/red]"
        )
        sys.exit(1)

    # Parse different GitHub URL formats
    patterns = [
        r"^git@github\.com:(.+)/(.+)\.git$",
        r"^git@github\.com:(.+)/(.+)$",
        r"^https://github\.com/(.+)/(.+)\.git$",
        r"^https://github\.com/(.+)/(.+)$",
    ]

    for pattern in patterns:
        match = re.match(pattern, repo_url)
        if match:
            return f"{match.group(1)}/{match.group(2)}"

    console.print(f"[red]Error: Unsupported git remote URL format: {repo_url}[/red]")
    sys.exit(1)


def github_request(
    method: str, endpoint: str, token: str, **kwargs
) -> requests.Response:
    """Make a GitHub API request."""
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }

    response = requests.request(
        method, f"{GITHUB_API}{endpoint}", headers=headers, **kwargs
    )

    if response.status_code >= 400:
        try:
            error_msg = response.json().get("message", "Unknown error")
        except:
            error_msg = "Unknown error"
        console.print(
            f"[red]GitHub API error ({response.status_code}): {error_msg}[/red]"
        )
        sys.exit(1)

    return response


def hex_to_rgb(hex_color: str) -> tuple:
    """Convert hex color to RGB tuple."""
    if len(hex_color) != 6:
        return None
    try:
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return (r, g, b)
    except ValueError:
        return None


@app.command()
def list():
    """List all open issues."""
    token = get_github_token()
    repo = get_repo_info()

    console.print(f"[bright_blue]Fetching open issues for {repo}...[/bright_blue]")

    # Get issues
    issues_response = github_request(
        "GET", f"/repos/{repo}/issues", token, params={"state": "open"}
    )
    issues = issues_response.json()

    # Get labels for color mapping
    labels_response = github_request("GET", f"/repos/{repo}/labels", token)
    labels = labels_response.json()
    label_colors = {label["name"]: label["color"] for label in labels}

    if not issues:
        console.print("[gray]No open issues found[/gray]")
        return

    # Create table
    table = Table(show_header=True, header_style="bold")
    table.add_column("ID", style="green", width=6)
    table.add_column("TITLE", width=50)
    table.add_column("LABEL", width=10)
    table.add_column("AUTHOR", width=12)
    table.add_column("CREATED", width=10)

    for issue in issues:
        number = str(issue["number"])
        title = issue["title"][:50]
        author = issue["user"]["login"]
        created = issue["created_at"][:10]

        label_name = ""
        label_style = ""
        if issue.get("labels"):
            label_name = issue["labels"][0]["name"]
            hex_color = label_colors.get(label_name)
            if hex_color:
                rgb = hex_to_rgb(hex_color)
                if rgb:
                    label_style = f"rgb({rgb[0]},{rgb[1]},{rgb[2]})"

        table.add_row(
            number,
            title,
            (
                f"[{label_style}]{label_name}[/{label_style}]"
                if label_style
                else label_name
            ),
            author,
            created,
        )

    console.print(table)


def create_issue(label: str):
    """Create an issue with the specified label."""
    token = get_github_token()
    repo = get_repo_info()

    title = Prompt.ask("[bright_blue]?[/bright_blue] Title")

    if not title:
        console.print("[red]Error:[/red] Title cannot be empty")
        sys.exit(1)

    # Create issue
    response = github_request(
        "POST", f"/repos/{repo}/issues", token, json={"title": title, "labels": [label]}
    )

    issue = response.json()
    number = issue["number"]
    url = issue["html_url"]

    # Get label color
    labels_response = github_request("GET", f"/repos/{repo}/labels", token)
    labels = labels_response.json()
    label_color = next((l["color"] for l in labels if l["name"] == label), None)

    label_style = ""
    if label_color:
        rgb = hex_to_rgb(label_color)
        if rgb:
            label_style = f"rgb({rgb[0]},{rgb[1]},{rgb[2]})"

    console.print(
        f"[green]✓[/green] Created [{label_style}]{label}[/{label_style}] "
        f"[green]{number}[/green] → [gray]{url}[/gray]"
    )


@app.command()
def bug():
    """Create a new bug issue."""
    create_issue("bug")


@app.command()
def task():
    """Create a new task issue."""
    create_issue("task")


@app.command()
def idea():
    """Create a new idea issue."""
    create_issue("idea")


@app.command()
def resolve(
    issue_numbers: List[int] = typer.Argument(..., help="Issue numbers to resolve")
):
    """Resolve (close) issues by number."""
    token = get_github_token()
    repo = get_repo_info()

    # Get labels for color mapping
    labels_response = github_request("GET", f"/repos/{repo}/labels", token)
    labels = labels_response.json()
    label_colors = {label["name"]: label["color"] for label in labels}

    for number in issue_numbers:
        # Get issue details
        issue_response = github_request("GET", f"/repos/{repo}/issues/{number}", token)
        issue = issue_response.json()

        # Close issue
        github_request(
            "PATCH", f"/repos/{repo}/issues/{number}", token, json={"state": "closed"}
        )

        url = issue["html_url"]
        label_name = issue["labels"][0]["name"] if issue.get("labels") else "issue"

        label_style = ""
        if label_name != "issue":
            hex_color = label_colors.get(label_name)
            if hex_color:
                rgb = hex_to_rgb(hex_color)
                if rgb:
                    label_style = f"rgb({rgb[0]},{rgb[1]},{rgb[2]})"

        console.print(
            f"[green]✓[/green] Resolved [{label_style}]{label_name}[/{label_style}] "
            f"[green]{number}[/green] → [gray]{url}[/gray]"
        )


@app.command()
def delete(
    issue_numbers: List[int] = typer.Argument(..., help="Issue numbers to delete")
):
    """Delete issues permanently by number (uses GraphQL API)."""
    token = get_github_token()
    repo = get_repo_info()
    owner, name = repo.split("/")

    # Get labels for color mapping
    labels_response = github_request("GET", f"/repos/{repo}/labels", token)
    labels = labels_response.json()
    label_colors = {label["name"]: label["color"] for label in labels}

    graphql_url = "https://api.github.com/graphql"

    for number in issue_numbers:
        # Get issue details
        issue_response = github_request("GET", f"/repos/{repo}/issues/{number}", token)
        issue = issue_response.json()
        title = issue["title"]
        label_name = issue["labels"][0]["name"] if issue.get("labels") else "issue"

        # Get issue ID via GraphQL
        query = {
            "query": f"""
                query {{
                    repository(owner: "{owner}", name: "{name}") {{
                        issue(number: {number}) {{
                            id
                        }}
                    }}
                }}
            """
        }

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        response = requests.post(graphql_url, json=query, headers=headers)
        result = response.json()

        if "errors" in result:
            console.print(f"[red]GraphQL error: {result['errors']}[/red]")
            continue

        issue_id = result["data"]["repository"]["issue"]["id"]

        # Delete issue via GraphQL mutation
        mutation = {
            "query": f"""
                mutation {{
                    deleteIssue(input: {{issueId: "{issue_id}"}}) {{
                        repository {{
                            id
                        }}
                    }}
                }}
            """
        }

        response = requests.post(graphql_url, json=mutation, headers=headers)
        result = response.json()

        if "errors" in result:
            console.print(f"[red]GraphQL error: {result['errors']}[/red]")
            continue

        label_style = ""
        if label_name != "issue":
            hex_color = label_colors.get(label_name)
            if hex_color:
                rgb = hex_to_rgb(hex_color)
                if rgb:
                    label_style = f"rgb({rgb[0]},{rgb[1]},{rgb[2]})"

        console.print(
            f"[green]✓[/green] Deleted [{label_style}]{label_name}[/{label_style}] "
            f"[green]{number}[/green]: [bold]{title}[/bold]"
        )


if __name__ == "__main__":
    app()
