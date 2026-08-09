[CmdletBinding()]
param([string]$OutputRoot = "dist")

$ErrorActionPreference = "Stop"
$workspace = [System.IO.Path]::GetFullPath((Get-Location).Path)
$dist = [System.IO.Path]::GetFullPath((Join-Path $workspace $OutputRoot))
$stage = [System.IO.Path]::GetFullPath((Join-Path $dist "Tishte-Serif-v0.900-RC"))
$archive = [System.IO.Path]::GetFullPath((Join-Path $dist "Tishte-Serif-v0.900-RC.zip"))
if (-not $stage.StartsWith($dist + [IO.Path]::DirectorySeparatorChar)) { throw "Unsafe package path: $stage" }
if (Test-Path -LiteralPath $stage) { Remove-Item -LiteralPath $stage -Recurse -Force }
New-Item -ItemType Directory -Path $stage -Force | Out-Null
foreach ($directory in @("ttf", "woff2", "docs", "reports", "scripts")) {
    New-Item -ItemType Directory -Path (Join-Path $stage $directory) -Force | Out-Null
}

Copy-Item -Path "build\TishteSerif-*-v900.ttf" -Destination (Join-Path $stage "ttf")
Copy-Item -Path "build\web\TishteSerif-*-v900.woff2" -Destination (Join-Path $stage "woff2")
Copy-Item -LiteralPath "build\web\tishte-serif-v900.css" -Destination (Join-Path $stage "woff2")
Copy-Item -LiteralPath "licenses\TINOS-OFL-1.1.txt" -Destination (Join-Path $stage "OFL.txt")
foreach ($file in @(
    "docs\release-candidate-v900.md",
    "docs\quality-policy-v090.md",
    "docs\opentype-v120.md",
    "docs\platform-validation-v130.md"
)) { Copy-Item -LiteralPath $file -Destination (Join-Path $stage "docs") }
foreach ($file in @(
    "artifacts\reports\metric-contract-v900.json",
    "artifacts\reports\unicode-normalization-v900.json",
    "artifacts\reports\language-corpus-v900.json",
    "artifacts\reports\opentype-v900.json",
    "artifacts\reports\webfonts-v900.json",
    "artifacts\reports\fontbakery-v900.md"
)) { Copy-Item -LiteralPath $file -Destination (Join-Path $stage "reports") }
foreach ($file in @(
    "scripts\Install-TishteSerifV900.ps1",
    "scripts\Uninstall-TishteSerifV900.ps1",
    "scripts\Install-TishteSerifFamilyV060.ps1",
    "scripts\Uninstall-TishteSerifFamilyV060.ps1"
)) { Copy-Item -LiteralPath $file -Destination (Join-Path $stage "scripts") }

Get-ChildItem -LiteralPath $stage -Recurse -File | Sort-Object FullName | Get-FileHash -Algorithm SHA256 |
    ForEach-Object { "$($_.Hash.ToLower())  $([IO.Path]::GetRelativePath($stage, $_.Path).Replace('\', '/'))" } |
    Set-Content -LiteralPath (Join-Path $stage "SHA256SUMS.txt") -Encoding UTF8
Compress-Archive -LiteralPath $stage -DestinationPath $archive -CompressionLevel Optimal -Force
[ordered]@{
    package = $archive
    files = (Get-ChildItem $stage -Recurse -File).Count
    bytes = (Get-Item $archive).Length
} | ConvertTo-Json
