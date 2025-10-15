# CLAUDE.md

AI maintainer context for the toolbox project.

## Architecture

### Project Structure
```
toolbox/
├── cli.py          # CLI orchestrator using Typer
├── taskman.py      # GitHub issue management core
├── publisher.py    # PyPI publishing workflow
└── __init__.py     # Package initialization
```

### Module Responsibilities

**cli.py** - Command routing and CLI interface
- Exposes all commands via Typer decorators
- Routes user input to appropriate modules (taskman or publisher)
- Entry point: `box` command defined in pyproject.toml scripts section

**taskman.py** - GitHub issue operations
- Creates/lists/closes/deletes GitHub issues via REST + GraphQL APIs
- Auto-detects repository from git remote URL parsing
- Uses GraphQL for delete operations (REST API only supports close)
- Rich terminal formatting with label colors (hex to RGB conversion)

**publisher.py** - PyPI release automation
- Full release workflow: version bump → build → publish → tag → GitHub release
- Dry-run mode for validation without changes
- Rollback capability on failure
- PyPI polling to confirm publication success
- Requires PYPI_API_TOKEN and optionally GITHUB_TOKEN

## Design Decisions

### Why GraphQL for Delete?
GitHub REST API v3 only supports closing issues, not permanent deletion. The GraphQL API exposes `deleteIssue` mutation, requiring:
1. REST call to get issue metadata
2. GraphQL query to get issue node ID
3. GraphQL mutation to delete issue

This is implemented in taskman.py:258-336.

### Why Git Remote Auto-Detection?
Eliminates need for explicit repo configuration. Uses `git remote get-url origin` and regex pattern matching to extract owner/name from:
- SSH format: `git@github.com:owner/repo.git`
- HTTPS format: `https://github.com/owner/repo.git`

Shared implementation between taskman.py:34-67 and publisher.py:120-143.

### Why Rich for Terminal Output?
- Colored labels using actual GitHub label colors (hex → RGB)
- Structured tables for issue lists
- Clear visual feedback for operations (✓ symbols, colors)
- Better UX than plain print statements

## Environment Requirements

### Required Variables
- `GITHUB_TOKEN` - GitHub personal access token with `repo` scope
- `PYPI_API_TOKEN` - PyPI token for publishing (publisher only)

### Optional Variables
- None (all features require explicit tokens)

### Token Loading
Uses python-dotenv to load from `.env` file in project root or from shell environment.

## Development Workflow

### Testing Strategy
- Manual testing via `box` commands in dev environment
- Dry-run mode for publisher testing (`box release patch --dry-run`)
- Test against real GitHub repos (requires token)

### Adding New Commands
1. Add command function to taskman.py or create new module
2. Add Typer route in cli.py
3. Update README.md usage section

### Module Dependencies
- taskman: requests, rich, typer, python-dotenv
- publisher: rich, requests (optional for GitHub releases)
- cli: typer

Full dependency list in @pyproject.toml.

## Gotchas

### Git Remote Format Variations
Parser handles 4 formats but may fail on:
- Non-GitHub remotes
- Custom SSH ports
- Enterprise GitHub URLs

Error message shows unparsed URL for debugging.

### GraphQL Rate Limiting
Delete operations make 3 API calls per issue:
1. REST GET for metadata
2. GraphQL query for ID
3. GraphQL mutation for delete

May hit rate limits on bulk deletions.

### Publisher Rollback Limitations
Rollback cannot undo:
- PyPI publication (packages are immutable)
- Pushed tags (requires force delete)
- GitHub releases (API deletion not implemented)

Only rolls back local git changes.

### Color Rendering Edge Cases
Hex color conversion in taskman.py:95-105 returns None for:
- Invalid hex lengths (≠ 6 chars)
- Non-hex characters

Falls back to uncolored label text.

## Request Flow Examples

### List Tasks
```
user: box list
→ cli.py:12 list()
→ taskman.py:108 list_tasks()
  → get_github_token()
  → get_repo_info() [git command]
  → github_request() [REST: GET /repos/{repo}/issues]
  → github_request() [REST: GET /repos/{repo}/labels]
  → Rich table rendering
```

### Delete Task
```
user: box delete 42
→ cli.py:44 delete([42])
→ taskman.py:258 delete_tasks([42])
  → github_request() [REST: GET /repos/{repo}/issues/42]
  → requests.post() [GraphQL: query for issue ID]
  → requests.post() [GraphQL: deleteIssue mutation]
```

### Release Package
```
user: box release patch
→ cli.py:52 release()
→ publisher.py:430 main()
→ publisher.py:361 Publisher.release()
  → validate_clean_repository()
  → validate_pyproject()
  → bump_version() [poetry version patch]
  → build_package() [poetry build]
  → publish_to_pypi() [poetry publish]
  → git_commit_and_tag()
  → create_github_release() [REST: POST /repos/{repo}/releases]
  → poll_pypi() [PyPI JSON API polling]
```

## Installation as Dependency

See @README.md for user-facing installation instructions.

Key implementation detail: `[tool.poetry.scripts]` in pyproject.toml creates `box` executable, making CLI available immediately after Poetry install without manual PATH configuration.
