# Development guide

This guide explains how to work on `pygraph-tool` locally.

## Requirements

The project uses:

- Python as defined in `pyproject.toml`
- `uv` for dependency management, build and publication
- `pytest` for tests
- `coverage` for test coverage
- `ruff` for formatting and linting
- `mypy` for type checking

## Install development dependencies

From the project root:

```bash
uv sync --dev
```

## Run tests

```bash
uv run pytest
```

Run tests with branch coverage:

```bash
uv run coverage run --branch -m pytest
uv run coverage report -m
```

## Format code

```bash
uv run ruff format .
```

## Lint code

```bash
uv run ruff check .
```

## Type checking

```bash
uv run mypy pygraph_tool
```

## Build the package

```bash
uv build --no-sources
```

Before building a release, clean previous build artifacts:

```bash
rm -rf dist
```

On Windows PowerShell:

```powershell
Remove-Item -Recurse -Force dist
```

Then build again:

```bash
uv build --no-sources
```

## Recommended local validation

Before opening a pull request or publishing a release, run:

```bash
uv run ruff format .
uv run ruff check .
uv run mypy pygraph_tool
uv run coverage run --branch -m pytest
uv run coverage report -m
uv build --no-sources
```
