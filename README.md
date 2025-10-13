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

```bash
poetry add --group dev git+https://github.com/basileaw/issue-manager.git
```

## Usage

### Direct CLI (Works immediately after installation)

```bash
issue list              # List all open issues
issue bug               # Create a new bug issue
issue task              # Create a new task issue
issue idea              # Create a new idea issue
issue resolve 1 2 3     # Resolve issues by number
issue delete 1 2 3      # Delete issues permanently
```

### Optional: Poe the Poet Integration

If you use Poe the Poet and want custom task aliases, add to your `tasks.yaml`:

```yaml
tasks:
  "issue:list":
    cmd: issue list
    help: List all open issues
  
  "issue:bug":
    cmd: issue bug
    help: Create a bug issue
  
  "issue:task":
    cmd: issue task
    help: Create a task issue
  
  "issue:idea":
    cmd: issue idea
    help: Create an idea issue
  
  "issue:resolve":
    cmd: issue resolve
    help: Resolve issues by number
  
  "issue:delete":
    cmd: issue delete
    help: Delete issues permanently
```

Then use:

```bash
poe issue:list
poe issue:bug
poe issue:resolve 1 2 3
```

## Setup

### GitHub Token

Create a `.env` file in your project root:

```
GITHUB_TOKEN=your_github_personal_access_token
```

Or export it in your shell:

```bash
export GITHUB_TOKEN=your_github_personal_access_token
```

### GitHub Token Permissions

Your personal access token needs these scopes:
- `repo` (for private repos) or `public_repo` (for public repos only)

## Requirements

- Python 3.12+
- Git repository with GitHub remote origin
- GitHub personal access token with repo access
- Tools: git (for repository detection)

## Development

```bash
# Install dependencies
poetry install

# Run tests
poetry run pytest
```