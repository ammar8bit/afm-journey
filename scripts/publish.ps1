# Validate, build, commit and push. GitHub Actions then deploys to
# https://ammar8bit.github.io/afm-journey/
#   .\scripts\publish.ps1                      # default message
#   .\scripts\publish.ps1 "Mark Garnod 18/25"  # custom message
param([string]$Message = "Update journey $(Get-Date -Format yyyy-MM-dd)")
$ErrorActionPreference = "Stop"
Push-Location (Split-Path $PSScriptRoot -Parent)
try {
    python scripts/check_data.py
    if ($LASTEXITCODE -ne 0) { throw "Data check failed" }
    python scripts/build.py
    git add -A
    git diff --cached --quiet
    if ($LASTEXITCODE -eq 0) { Write-Host "Nothing to publish."; return }
    git commit -m $Message
    git push
}
finally { Pop-Location }
