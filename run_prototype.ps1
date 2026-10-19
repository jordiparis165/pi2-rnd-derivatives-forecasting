$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$juliaExe = Join-Path $projectRoot '.tools\julia-1.10.10\bin\julia.exe'

python (Join-Path $projectRoot 'src\spx_breeden_litzenberger.py')
& $juliaExe (Join-Path $projectRoot 'src\breeden_litzenberger.jl')

Write-Host "Résultats disponibles dans $projectRoot\results"
