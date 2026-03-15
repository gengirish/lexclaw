Write-Host "Installing Node dependencies..."
npm install

Write-Host "Ensuring uv is available..."
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
  python -m pip install uv
}

Write-Host "Installing API dependencies with uv..."
uv sync --project apps/api --frozen --group dev

Write-Host "LexClaw Phase 1 setup complete."
