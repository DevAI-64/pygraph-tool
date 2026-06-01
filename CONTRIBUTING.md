# Contributing to pygraph-tool

Thank you for considering contributing to `pygraph-tool`.

This project aims to stay lightweight, readable and focused on object-oriented graph manipulation in Python.

## Before contributing

Please make sure your contribution fits the project goals:

- keep the library lightweight,
- avoid unnecessary runtime dependencies,
- preserve backward compatibility when possible,
- add tests for new behavior,
- keep public methods documented,
- prefer explicit and readable code over clever abstractions.

## Development setup

Clone the repository:

```bash
git clone https://github.com/DevAI-64/pygraph-tool.git
cd pygraph-tool
```

Install development dependencies:

```bash
uv sync --dev
```

## Run checks locally

Before opening a pull request, run:

```bash
uv run ruff format .
uv run ruff check .
uv run mypy pygraph_tool
uv run coverage run --branch -m pytest
uv run coverage report -m
```

Build the package:

```bash
uv build --no-sources
```

## Tests

Add or update tests when you change behavior.

Tests are located in:

```text
tests/
```

## Code style

The project uses:

- `ruff` for formatting and linting,
- `mypy` for type checking,
- Google-style docstrings for public methods.

## Commit messages

Use clear commit messages.

Examples:

```text
feat: add chained node queries
fix: preserve metadata when extracting subgraphs
docs: update query documentation
test: add edge query tests
chore: normalize line endings
```

## Pull requests

A good pull request should include:

- a clear description of the change,
- the motivation behind the change,
- tests when relevant,
- documentation updates when public behavior changes,
- confirmation that local checks pass.

## Backward compatibility

Avoid breaking existing public methods unless there is a strong reason.

Breaking changes should be reserved for major versions.

## Questions

If you are unsure whether a change fits the project, open an issue before starting a large implementation.
