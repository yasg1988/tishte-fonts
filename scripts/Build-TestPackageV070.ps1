[CmdletBinding()]
param([string]$OutputRoot = "dist")

$ErrorActionPreference = "Stop"
$workspace = [System.IO.Path]::GetFullPath((Get-Location).Path)
$dist = [System.IO.Path]::GetFullPath((Join-Path $workspace $OutputRoot))
$stage = [System.IO.Path]::GetFullPath((Join-Path $dist "Tishte-Serif-v070-office-tests"))
$archive = [System.IO.Path]::GetFullPath((Join-Path $dist "Tishte-Serif-v070-office-tests.zip"))
if (-not $stage.StartsWith($dist + [System.IO.Path]::DirectorySeparatorChar)) {
    throw "Unsafe test staging path: $stage"
}
if (Test-Path -LiteralPath $stage) { Remove-Item -LiteralPath $stage -Recurse -Force }
New-Item -ItemType Directory -Path $stage -Force | Out-Null
Copy-Item -LiteralPath "artifacts\document-tests\v070" -Destination (Join-Path $stage "word") -Recurse
Copy-Item -LiteralPath "artifacts\office-tests\v070\excel" -Destination (Join-Path $stage "excel") -Recurse
Copy-Item -LiteralPath "artifacts\office-tests\v070\powerpoint" -Destination (Join-Path $stage "powerpoint") -Recurse
Compress-Archive -LiteralPath $stage -DestinationPath $archive -CompressionLevel Optimal -Force
[ordered]@{
    package = $archive
    bytes = (Get-Item -LiteralPath $archive).Length
    files = (Get-ChildItem -LiteralPath $stage -Recurse -File).Count
} | ConvertTo-Json
