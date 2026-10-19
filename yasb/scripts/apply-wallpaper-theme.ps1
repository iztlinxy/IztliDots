param([Parameter(Mandatory = $true)][string]$ImagePath)

$ErrorActionPreference = 'Stop'
$python = Join-Path $PSScriptRoot '.venv/Scripts/python.exe'
$generator = Join-Path $PSScriptRoot 'wallpaper_theme.py'
if (-not (Test-Path -LiteralPath $python)) {
    throw 'Falta scripts/.venv. Instala las dependencias con scripts/.venv/Scripts/python.exe -m pip install -r scripts/requirements.txt.'
}
& $python $generator $ImagePath --apply
exit $LASTEXITCODE
