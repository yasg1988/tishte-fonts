[CmdletBinding()]
param(
    [string]$OutputRoot = "dist"
)

$ErrorActionPreference = "Stop"
$workspace = [System.IO.Path]::GetFullPath((Get-Location).Path)
$dist = [System.IO.Path]::GetFullPath((Join-Path $workspace $OutputRoot))
$stage = [System.IO.Path]::GetFullPath((Join-Path $dist "Tishte-Serif-v060"))
$archive = [System.IO.Path]::GetFullPath((Join-Path $dist "Tishte-Serif-v060-engineering.zip"))
if (-not $stage.StartsWith($dist + [System.IO.Path]::DirectorySeparatorChar)) {
    throw "Unsafe package staging path: $stage"
}
if (Test-Path -LiteralPath $stage) { Remove-Item -LiteralPath $stage -Recurse -Force }
New-Item -ItemType Directory -Path $stage -Force | Out-Null

$files = @(
    "build\TishteSerif-Regular-v060.ttf",
    "build\TishteSerif-Bold-v060.ttf",
    "build\TishteSerif-Italic-v060.ttf",
    "build\TishteSerif-BoldItalic-v060.ttf",
    "licenses\TINOS-OFL-1.1.txt",
    "docs\engineering-family-v060.md",
    "scripts\Install-TishteSerifFamilyV060.ps1",
    "scripts\Uninstall-TishteSerifFamilyV060.ps1"
)
foreach ($file in $files) {
    Copy-Item -LiteralPath (Join-Path $workspace $file) -Destination $stage -Force
}

$hashes = Get-ChildItem -LiteralPath $stage -File | Sort-Object Name | Get-FileHash -Algorithm SHA256
$hashLines = $hashes | ForEach-Object { "$($_.Hash.ToLower())  $([System.IO.Path]::GetFileName($_.Path))" }
$hashLines | Set-Content -LiteralPath (Join-Path $stage "SHA256SUMS.txt") -Encoding UTF8
Compress-Archive -LiteralPath $stage -DestinationPath $archive -CompressionLevel Optimal -Force

[ordered]@{
    package = $archive
    files = (Get-ChildItem -LiteralPath $stage -File).Count
    bytes = (Get-Item -LiteralPath $archive).Length
} | ConvertTo-Json
