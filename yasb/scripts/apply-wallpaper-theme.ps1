param([Parameter(Mandatory = $true)][string]$ImagePath)

$ErrorActionPreference = 'Stop'
$python = Join-Path $PSScriptRoot '.venv/Scripts/python.exe'
$generator = Join-Path $PSScriptRoot 'wallpaper_theme.py'
if (-not (Test-Path -LiteralPath $python)) {
    throw 'Falta scripts/.venv. Sigue la preparación de theme/README.md.'
}
& $python $generator $ImagePath --apply
exit $LASTEXITCODE
