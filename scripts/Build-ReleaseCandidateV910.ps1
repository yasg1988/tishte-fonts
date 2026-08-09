[CmdletBinding()]
param([string]$OutputRoot = "dist")

$ErrorActionPreference = "Stop"
$workspace = [System.IO.Path]::GetFullPath((Get-Location).Path)
$dist = [System.IO.Path]::GetFullPath((Join-Path $workspace $OutputRoot))
$stage = [System.IO.Path]::GetFullPath((Join-Path $dist "Tishte-Serif-v0.910-RC"))
$archive = [System.IO.Path]::GetFullPath((Join-Path $dist "Tishte-Serif-v0.910-RC.zip"))
if (-not $stage.StartsWith($dist + [IO.Path]::DirectorySeparatorChar)) { throw "Unsafe package path: $stage" }
if (Test-Path -LiteralPath $stage) { Remove-Item -LiteralPath $stage -Recurse -Force }
New-Item -ItemType Directory -Path $stage -Force | Out-Null
foreach ($directory in @("ttf", "woff2", "docs", "reports", "scripts", "provenance")) {
    New-Item -ItemType Directory -Path (Join-Path $stage $directory) -Force | Out-Null
}

Copy-Item -Path "build\TishteSerif-*-v910.ttf" -Destination (Join-Path $stage "ttf")
Copy-Item -Path "build\web\TishteSerif-*-v910.woff2" -Destination (Join-Path $stage "woff2")
Copy-Item -LiteralPath "build\web\tishte-serif-v910.css" -Destination (Join-Path $stage "woff2")
Copy-Item -LiteralPath "licenses\TINOS-OFL-1.1.txt" -Destination (Join-Path $stage "OFL.txt")
foreach ($file in @(
    "docs\release-candidate-v900.md",
    "docs\hardening-v910.md",
    "docs\review-kits-v910.md",
    "docs\quality-policy-v090.md",
    "docs\metrics-contract.md",
    "docs\opentype-v120.md",
    "docs\platform-validation-v130.md"
)) { Copy-Item -LiteralPath $file -Destination (Join-Path $stage "docs") }
foreach ($file in @(
    "artifacts\reports\metric-contract-v910.json",
    "artifacts\reports\metric-pair-deltas-v910.json",
    "artifacts\reports\production-subset-v910.json",
    "artifacts\reports\unicode-normalization-v910.json",
    "artifacts\reports\language-corpus-v910.json",
    "artifacts\reports\opentype-v910.json",
    "artifacts\reports\outline-originality-v910.json",
    "artifacts\reports\reproducible-build-v910.json",
    "artifacts\reports\webfonts-v910.json",
    "artifacts\reports\fontbakery-v910.md"
)) { Copy-Item -LiteralPath $file -Destination (Join-Path $stage "reports") }
foreach ($file in @(
    "scripts\Install-TishteSerifV910.ps1",
    "scripts\Uninstall-TishteSerifV910.ps1",
    "scripts\Install-TishteSerifFamilyV060.ps1",
    "scripts\Uninstall-TishteSerifFamilyV060.ps1"
)) { Copy-Item -LiteralPath $file -Destination (Join-Path $stage "scripts") }
Copy-Item -LiteralPath "data\times-new-roman-metrics.json" -Destination (Join-Path $stage "provenance")
Copy-Item -LiteralPath "requirements-lock.txt" -Destination (Join-Path $stage "provenance")
Copy-Item -LiteralPath "requirements-audit-lock.txt" -Destination (Join-Path $stage "provenance")

Get-ChildItem -LiteralPath $stage -Recurse -File | Sort-Object FullName | Get-FileHash -Algorithm SHA256 |
    ForEach-Object { "$($_.Hash.ToLower())  $([IO.Path]::GetRelativePath($stage, $_.Path).Replace('\', '/'))" } |
    Set-Content -LiteralPath (Join-Path $stage "SHA256SUMS.txt") -Encoding UTF8
Compress-Archive -LiteralPath $stage -DestinationPath $archive -CompressionLevel Optimal -Force
[ordered]@{
    package = $archive
    files = (Get-ChildItem $stage -Recurse -File).Count
    bytes = (Get-Item $archive).Length
} | ConvertTo-Json
