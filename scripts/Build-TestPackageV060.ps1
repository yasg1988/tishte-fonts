[CmdletBinding()]
param(
    [string]$OutputRoot = "dist"
)

$ErrorActionPreference = "Stop"
$workspace = [System.IO.Path]::GetFullPath((Get-Location).Path)
$dist = [System.IO.Path]::GetFullPath((Join-Path $workspace $OutputRoot))
$stage = [System.IO.Path]::GetFullPath((Join-Path $dist "Tishte-Serif-v060-office-tests"))
$archive = [System.IO.Path]::GetFullPath((Join-Path $dist "Tishte-Serif-v060-office-tests.zip"))
if (-not $stage.StartsWith($dist + [System.IO.Path]::DirectorySeparatorChar)) {
    throw "Unsafe test staging path: $stage"
}
if (Test-Path -LiteralPath $stage) { Remove-Item -LiteralPath $stage -Recurse -Force }
New-Item -ItemType Directory -Path $stage -Force | Out-Null

$wordTarget = Join-Path $stage "word"
$excelTarget = Join-Path $stage "excel"
$powerPointTarget = Join-Path $stage "powerpoint"
New-Item -ItemType Directory -Path $wordTarget, $excelTarget, $powerPointTarget -Force | Out-Null

Copy-Item -LiteralPath "artifacts\document-tests\v060\docx" -Destination $wordTarget -Recurse
Copy-Item -LiteralPath "artifacts\document-tests\v060\pdf" -Destination $wordTarget -Recurse
Copy-Item -LiteralPath "artifacts\document-tests\v060\layout-comparison.json" -Destination $wordTarget
Copy-Item -LiteralPath "artifacts\document-tests\v060\word-render-report.json" -Destination $wordTarget

Get-ChildItem "artifacts\office-tests\v060\excel" -File |
    Where-Object { $_.Extension -in ".xlsx", ".pdf", ".json" } |
    Copy-Item -Destination $excelTarget
Get-ChildItem "artifacts\office-tests\v060\powerpoint" -File |
    Where-Object { $_.Extension -in ".pptx", ".pdf", ".json" } |
    Copy-Item -Destination $powerPointTarget

Compress-Archive -LiteralPath $stage -DestinationPath $archive -CompressionLevel Optimal -Force
[ordered]@{
    package = $archive
    bytes = (Get-Item -LiteralPath $archive).Length
    files = (Get-ChildItem -LiteralPath $stage -Recurse -File).Count
} | ConvertTo-Json
