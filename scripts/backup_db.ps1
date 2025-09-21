# Usage: powershell -File scripts/backup_db.ps1 -OutDir backups -DbUrl "postgresql://appuser:apppass@localhost:5432/certificates"
param(
    [string]$OutDir = "backups",
    [string]$DbUrl = "postgresql://appuser:apppass@localhost:5432/certificates"
)

if (!(Test-Path $OutDir)) { New-Item -ItemType Directory -Path $OutDir | Out-Null }

$ts = Get-Date -Format "yyyyMMdd_HHmmss"
$backup = Join-Path $OutDir "certificates_$ts.sql"

Write-Host "Backing up to $backup"
& pg_dump $DbUrl > $backup
if ($LASTEXITCODE -ne 0) { Write-Error "pg_dump failed"; exit 1 }
Write-Host "Done"





