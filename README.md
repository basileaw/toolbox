# issue-manager

GitHub issue management CLI tool for Python projects.

## Features

- List all open issues with colored labels
- Create bug, task, and idea issues interactively
- Resolve (close) one or multiple issues
- Delete issues permanently (uses GraphQL API)
- Auto-detects repository from git remote
- Rich terminal output with colors

## Installation

### In your project

```toml
# pyproject.toml
[tool.poetry.group.dev.dependencies]
issue-manager = { path = "../issue-manager", develop = true }
```

Or from GitHub:

```toml
[tool.poetry.group.dev.dependencies]
issue-manager = { git = "https://github.com/youruser/issue-manager.git", branch = "main" }
```

### Setup GitHub Token

Create a `.env` file in your project root:

```
GITHUB_TOKEN=your_github_personal_access_token
```

Or export it in your shell:

```bash
export GITHUB_TOKEN=your_github_personal_access_token
```

## Usage

### With Poe the Poet (Recommended)

Add to your `tasks.yaml`:

```yaml
include:
  - .venv/lib/python3.12/site-packages/issue_manager/tasks.yaml
```

Then use:

```bash
poe list              # List all open issues
poe bug               # Create a new bug issue
poe task              # Create a new task issue
poe idea              # Create a new idea issue
poe resolve 1 2 3     # Resolve issues by number
poe delete 1 2 3      # Delete issues permanently by number
```

### Direct CLI Usage

```bash
python -m issue_manager.cli list
python -m issue_manager.cli bug
python -m issue_manager.cli resolve 1 2 3
```

## Requirements

- Python 3.12+
- Git repository with GitHub remote origin
- GitHub personal access token with repo access
- Tools: git (for repository detection)

## GitHub Token Permissions

Your personal access token needs these scopes:
- `repo` (for private repos) or `public_repo` (for public repos only)

## Development

```bash
# Install dependencies
poetry install

# Run tests
poetry run pytest
```