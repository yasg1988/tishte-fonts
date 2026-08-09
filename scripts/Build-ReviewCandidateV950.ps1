[CmdletBinding()]
param([string]$OutputRoot = "dist")

$ErrorActionPreference = "Stop"
$workspace = [System.IO.Path]::GetFullPath((Get-Location).Path)
$dist = [System.IO.Path]::GetFullPath((Join-Path $workspace $OutputRoot))
$stage = [System.IO.Path]::GetFullPath((Join-Path $dist "Tishte-Serif-v0950-review.1"))
$archive = [System.IO.Path]::GetFullPath((Join-Path $dist "Tishte-Serif-v0950-review.1.zip"))
$prefix = $dist.TrimEnd([IO.Path]::DirectorySeparatorChar) + [IO.Path]::DirectorySeparatorChar
if (-not $stage.StartsWith($prefix, [StringComparison]::OrdinalIgnoreCase)) {
    throw "Unsafe package path: $stage"
}

New-Item -ItemType Directory -Path $dist -Force | Out-Null
if (Test-Path -LiteralPath $stage) { Remove-Item -LiteralPath $stage -Recurse -Force }
New-Item -ItemType Directory -Path $stage -Force | Out-Null

$mappings = @(
    @{ Source = "build\TishteSerif-Regular-v950.ttf"; Target = "fonts\ttf" },
    @{ Source = "build\TishteSerif-Bold-v950.ttf"; Target = "fonts\ttf" },
    @{ Source = "build\TishteSerif-Italic-v950.ttf"; Target = "fonts\ttf" },
    @{ Source = "build\TishteSerif-BoldItalic-v950.ttf"; Target = "fonts\ttf" },
    @{ Source = "build\web\TishteSerif-Regular-v950.woff2"; Target = "fonts\web" },
    @{ Source = "build\web\TishteSerif-Bold-v950.woff2"; Target = "fonts\web" },
    @{ Source = "build\web\TishteSerif-Italic-v950.woff2"; Target = "fonts\web" },
    @{ Source = "build\web\TishteSerif-BoldItalic-v950.woff2"; Target = "fonts\web" },
    @{ Source = "build\web\tishte-serif-v950.css"; Target = "fonts\web" },
    @{ Source = "artifacts\review\v0950\pdf"; Target = "review" },
    @{ Source = "artifacts\document-tests\v950"; Target = "evidence\word" },
    @{ Source = "artifacts\office-tests\v950\excel"; Target = "evidence\excel" },
    @{ Source = "artifacts\office-tests\v950\powerpoint"; Target = "evidence\powerpoint" },
    @{ Source = "licenses\TINOS-OFL-1.1.txt"; Target = "legal" },
    @{ Source = "AUTHORS.txt"; Target = "legal" },
    @{ Source = "CONTRIBUTORS.txt"; Target = "legal" },
    @{ Source = "docs\expert-review-v950.md"; Target = "documentation" },
    @{ Source = "docs\legal-review-v950.md"; Target = "documentation" },
    @{ Source = "docs\release-candidate-v950.md"; Target = "documentation" },
    @{ Source = "scripts\Install-TishteSerifV950.ps1"; Target = "tools" },
    @{ Source = "scripts\Uninstall-TishteSerifV950.ps1"; Target = "tools" }
)

foreach ($mapping in $mappings) {
    $source = Join-Path $workspace $mapping.Source
    if (-not (Test-Path -LiteralPath $source)) { throw "Missing package input: $source" }
    $target = Join-Path $stage $mapping.Target
    New-Item -ItemType Directory -Path $target -Force | Out-Null
    Copy-Item -LiteralPath $source -Destination $target -Recurse -Force
}

$reviewDocxTarget = Join-Path $stage "review\docx"
New-Item -ItemType Directory -Path $reviewDocxTarget -Force | Out-Null
foreach ($name in @(
    "00-Guide-v0950.docx",
    "01-Typography-Review-v0950.docx",
    "02-Meadow-Mari-Review-v0950.docx",
    "03-Hill-Mari-Review-v0950.docx",
    "04-Legal-Review-v0950.docx",
    "05-Internal-Evidence-v0950.docx"
)) {
    $source = Join-Path $workspace ("artifacts\review\v0950\docx\" + $name)
    if (-not (Test-Path -LiteralPath $source)) { throw "Missing review document: $source" }
    Copy-Item -LiteralPath $source -Destination $reviewDocxTarget -Force
}

$reportTarget = Join-Path $stage "evidence\reports"
New-Item -ItemType Directory -Path $reportTarget -Force | Out-Null
$reports = @(Get-ChildItem -LiteralPath (Join-Path $workspace "artifacts\reports") -File | Where-Object Name -Match "v950")
if ($reports.Count -eq 0) { throw "Missing v0.950 quality reports" }
foreach ($report in $reports) { Copy-Item -LiteralPath $report.FullName -Destination $reportTarget -Force }

$manifest = [ordered]@{
    package = "Tishte Serif v0.950 review.1"
    status = "Independent review candidate; not an official government font"
    generated_utc = [DateTime]::UtcNow.ToString("yyyy-MM-ddTHH:mm:ssZ")
    files = @()
}
foreach ($file in Get-ChildItem -LiteralPath $stage -Recurse -File | Sort-Object FullName) {
    $relative = $file.FullName.Substring($stage.Length + 1).Replace("\", "/")
    $manifest.files += [ordered]@{
        path = $relative
        bytes = $file.Length
        sha256 = (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
    }
}
$manifest | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $stage "MANIFEST.json") -Encoding UTF8

Get-ChildItem -LiteralPath $stage -Recurse -File | Sort-Object FullName |
    Where-Object Name -ne "SHA256SUMS.txt" |
    ForEach-Object {
        $relative = $_.FullName.Substring($stage.Length + 1).Replace("\", "/")
        "$((Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash.ToLowerInvariant())  $relative"
    } | Set-Content -LiteralPath (Join-Path $stage "SHA256SUMS.txt") -Encoding UTF8

Compress-Archive -LiteralPath $stage -DestinationPath $archive -CompressionLevel Optimal -Force
[ordered]@{
    package = $archive
    files = (Get-ChildItem -LiteralPath $stage -Recurse -File).Count
    bytes = (Get-Item -LiteralPath $archive).Length
    sha256 = (Get-FileHash -LiteralPath $archive -Algorithm SHA256).Hash.ToLowerInvariant()
} | ConvertTo-Json
