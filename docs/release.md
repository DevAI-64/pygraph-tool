# Release guide

This guide describes the release process for `pygraph-tool`.

## 1. Check the working tree

```bash
git status
```

Make sure all intended changes are committed or ready to be committed.

## 2. Run local checks

```bash
uv run ruff format .
uv run ruff check .
uv run mypy pygraph_tool
uv run coverage run --branch -m pytest
uv run coverage report -m
```

## 3. Update release files

Update:

- `pyproject.toml`
- `CHANGELOG.md`
- `README.md`
- documentation files in `docs/` if needed

The version in `pyproject.toml` and the Commitizen version should stay aligned.

## 4. Clean previous build artifacts

```bash
rm -rf dist
```

On Windows PowerShell:

```powershell
Remove-Item -Recurse -Force dist
```

## 5. Build the package

```bash
uv build --no-sources
```

Check `dist/`:

```bash
ls dist
```

On Windows PowerShell:

```powershell
Get-ChildItem dist
```

For a release `X.Y.Z`, `dist/` should contain only:

```text
pygraph_tool-X.Y.Z-py3-none-any.whl
pygraph_tool-X.Y.Z.tar.gz
```

Do not publish if older versions are still present in `dist/`.

## 6. Commit and push

```bash
git add .
git commit -m "feat: add ..."
git push origin <branch-name>
```

Open a pull request, wait for checks, then merge into `main`.

## 7. Tag the release

After merging:

```bash
git checkout main
git pull
git tag vX.Y.Z
git push origin vX.Y.Z
```

## 8. Create a GitHub release

Create a GitHub release from tag `vX.Y.Z`.

Use the relevant section of `CHANGELOG.md` as release notes.

## 9. Publish to PyPI

Use a PyPI token.

Recommended PowerShell flow:

```powershell
$env:UV_PUBLISH_TOKEN = "pypi-XXXXXXXXXXXXXXXXXXXXXXXX"
uv publish
Remove-Item Env:UV_PUBLISH_TOKEN
```

Alternative direct command:

```bash
uv publish --token "pypi-XXXXXXXXXXXXXXXXXXXXXXXX"
```

## 10. Verify installation

Create a temporary environment and install from PyPI:

```bash
pip install pygraph-tool==X.Y.Z
```

Then test a minimal import:

```bash
python -c "from pygraph_tool import Graph; g = Graph(); g.add_node('hello', node_id='n1'); print(g.get_node('n1').value)"
```

Expected output:

```text
hello
```
