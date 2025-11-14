<#
Run development servers (backend + frontend) with the project's venv.

Usage:
  Open PowerShell, from project root:
    .\run_dev.ps1

This script will:
 - create a `.venv` if missing
 - activate the venv
 - install backend/frontend requirements if missing
 - run `python dev.py`
#>

Set-StrictMode -Version Latest

$venvDir = Join-Path (Get-Location) '.venv'
$activate = Join-Path $venvDir 'Scripts\Activate.ps1'

if (-not (Test-Path $activate)) {
    Write-Host "Creating virtualenv at $venvDir..."
    python -m venv .venv
}

Write-Host "Activating venv..."
& $activate

Write-Host "Upgrading pip and installing requirements if needed..."
python -m pip install --upgrade pip setuptools wheel
if (Test-Path 'backend/requirements.txt') {
    python -m pip install -r backend/requirements.txt
}
if (Test-Path 'frontend/requirements.txt') {
    python -m pip install -r frontend/requirements.txt
}

Write-Host "Starting dev.py (backend + frontend)..."
python dev.py
