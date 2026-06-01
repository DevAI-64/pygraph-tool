$ErrorActionPreference = "Stop"
$PSNativeCommandUseErrorActionPreference = $true

$versions = @("3.12", "3.13", "3.14")

function Invoke-Check {
    param (
        [string] $Description,
        [scriptblock] $Command
    )

    Write-Host $Description -ForegroundColor Yellow
    & $Command

    if ($LASTEXITCODE -ne 0) {
        throw "Command failed: $Description"
    }
}

Write-Host "Installing requested Python versions with uv..." -ForegroundColor Cyan
Invoke-Check "Install Python versions" {
    uv python install @versions
}

foreach ($version in $versions) {
    $safeVersion = $version.Replace(".", "")
    $envName = ".venv-py$safeVersion"

    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "Checking Python $version using $envName" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan

    $env:UV_PROJECT_ENVIRONMENT = $envName

    try {
        Invoke-Check "Show Python version" {
            uv run --python $version python --version
        }

        Invoke-Check "Compile check" {
            uv run --python $version python -m compileall -q pygraph_tool tests
        }

        Invoke-Check "Ruff format check" {
            uv run --python $version ruff format --check .
        }

        Invoke-Check "Ruff lint check" {
            uv run --python $version ruff check .
        }

        Invoke-Check "Mypy check" {
            uv run --python $version mypy pygraph_tool
        }

        Invoke-Check "Pytest with coverage" {
            uv run --python $version coverage run --branch -m pytest
        }

        Invoke-Check "Coverage report" {
            uv run --python $version coverage report -m
        }
    }
    finally {
        Remove-Item Env:\UV_PROJECT_ENVIRONMENT -ErrorAction SilentlyContinue
    }
}

Write-Host ""
Write-Host "Cleaning dist directory..." -ForegroundColor Cyan
Invoke-Check "Remove dist directory" {
    if (Test-Path "dist") {
        Remove-Item -Recurse -Force "dist"
    }
}

Write-Host ""
Write-Host "Building package..." -ForegroundColor Cyan
Invoke-Check "Build package" {
    uv build --no-sources
}

Write-Host ""
Write-Host "Validating dist artifacts..." -ForegroundColor Cyan
Invoke-Check "Validate dist artifacts" {
    $wheels = Get-ChildItem "dist" -Filter "*.whl"
    $sdists = Get-ChildItem "dist" -Filter "*.tar.gz"

    if ($wheels.Count -ne 1) {
        throw "Expected exactly 1 wheel in dist, found $($wheels.Count)."
    }

    if ($sdists.Count -ne 1) {
        throw "Expected exactly 1 source distribution in dist, found $($sdists.Count)."
    }

    Write-Host "Wheel: $($wheels[0].Name)" -ForegroundColor Green
    Write-Host "Sdist: $($sdists[0].Name)" -ForegroundColor Green
}

Write-Host ""
Write-Host "All checks passed." -ForegroundColor Green
