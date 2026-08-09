[CmdletBinding()]
param([string]$OutputRoot = "dist")

$ErrorActionPreference = "Stop"
$workspace = [System.IO.Path]::GetFullPath((Get-Location).Path)
$dist = [System.IO.Path]::GetFullPath((Join-Path $workspace $OutputRoot))
$stage = [System.IO.Path]::GetFullPath((Join-Path $dist "Tishte-Serif-v0.920-Design-Candidate"))
$archive = [System.IO.Path]::GetFullPath((Join-Path $dist "Tishte-Serif-v0.920-Design-Candidate.zip"))
if (-not $stage.StartsWith($dist + [IO.Path]::DirectorySeparatorChar)) { throw "Unsafe package path: $stage" }
if (Test-Path -LiteralPath $stage) { Remove-Item -LiteralPath $stage -Recurse -Force }
New-Item -ItemType Directory -Path $stage -Force | Out-Null
foreach ($directory in @("ttf", "woff2", "docs", "reports", "scripts", "provenance")) {
    New-Item -ItemType Directory -Path (Join-Path $stage $directory) -Force | Out-Null
}

Copy-Item -Path "build\TishteSerif-*-v920.ttf" -Destination (Join-Path $stage "ttf")
Copy-Item -Path "build\web\TishteSerif-*-v920.woff2" -Destination (Join-Path $stage "woff2")
Copy-Item -LiteralPath "build\web\tishte-serif-v920.css" -Destination (Join-Path $stage "woff2")
Copy-Item -LiteralPath "licenses\TINOS-OFL-1.1.txt" -Destination (Join-Path $stage "OFL.txt")
foreach ($file in @(
    "docs\design-capitals-v920.md",
    "docs\originalisation-v920.md",
    "docs\review-kits-v910.md",
    "docs\quality-policy-v090.md",
    "docs\metrics-contract.md"
)) { Copy-Item -LiteralPath $file -Destination (Join-Path $stage "docs") }
foreach ($file in @(
    "artifacts\reports\metric-contract-v920.json",
    "artifacts\reports\metric-pair-deltas-v920.json",
    "artifacts\reports\production-subset-v920.json",
    "artifacts\reports\unicode-normalization-v920.json",
    "artifacts\reports\language-corpus-v920.json",
    "artifacts\reports\opentype-v920.json",
    "artifacts\reports\outline-originality-v920.json",
    "artifacts\reports\reproducible-build-v920.json",
    "artifacts\reports\webfonts-v920.json",
    "artifacts\reports\fontbakery-v920.md",
    "artifacts\reports\capitals-v920-Regular.png",
    "artifacts\reports\capitals-v920-Bold.png",
    "artifacts\reports\capitals-v920-Italic.png",
    "artifacts\reports\capitals-v920-BoldItalic.png"
)) { Copy-Item -LiteralPath $file -Destination (Join-Path $stage "reports") }
foreach ($file in @(
    "scripts\Install-TishteSerifV920.ps1",
    "scripts\Uninstall-TishteSerifV920.ps1",
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
