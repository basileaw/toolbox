# toolbox

Developer toolbox CLI - task management and utilities for Python projects.

## Features

### Task Management
- List all open GitHub issues/tasks with colored labels
- Create bug, task, and idea issues interactively
- Resolve (close) one or multiple tasks
- Delete tasks permanently (uses GraphQL API)
- Auto-detects repository from git remote
- Rich terminal output with colors

## Installation

```bash
poetry add --group dev git+https://github.com/basileaw/toolbox.git
```

## Usage

### Direct CLI (Works immediately after installation)

```bash
box list              # List all open tasks
box bug               # Create a new bug task
box task              # Create a new task
box idea              # Create a new idea task
box resolve 1 2 3     # Resolve tasks by number
box delete 1 2 3      # Delete tasks permanently
```

### Optional: Poe the Poet Integration

If you use Poe the Poet and want custom task aliases, the toolbox automatically includes these tasks:

```yaml
tasks:
  list:
    cmd: box list
    help: List all open tasks

  bug:
    cmd: box bug
    help: Create a new bug task

  task:
    cmd: box task
    help: Create a new task

  idea:
    cmd: box idea
    help: Create a new idea task

  resolve:
    cmd: box resolve
    help: Resolve (close) tasks by number

  delete:
    cmd: box delete
    help: Delete tasks permanently by number
```

Then use:

```bash
poe list
poe bug
poe resolve 1 2 3
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