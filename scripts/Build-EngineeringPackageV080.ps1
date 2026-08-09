[CmdletBinding()]
param([string]$OutputRoot = "dist")

$ErrorActionPreference = "Stop"
$workspace = [System.IO.Path]::GetFullPath((Get-Location).Path)
$dist = [System.IO.Path]::GetFullPath((Join-Path $workspace $OutputRoot))
$stage = [System.IO.Path]::GetFullPath((Join-Path $dist "Tishte-Serif-v080"))
$archive = [System.IO.Path]::GetFullPath((Join-Path $dist "Tishte-Serif-v080-engineering.zip"))
if (-not $stage.StartsWith($dist + [IO.Path]::DirectorySeparatorChar)) { throw "Unsafe package path: $stage" }
if (Test-Path -LiteralPath $stage) { Remove-Item -LiteralPath $stage -Recurse -Force }
New-Item -ItemType Directory -Path $stage -Force | Out-Null
$files = @(
    "build\TishteSerif-Regular-v080.ttf",
    "build\TishteSerif-Bold-v080.ttf",
    "build\TishteSerif-Italic-v080.ttf",
    "build\TishteSerif-BoldItalic-v080.ttf",
    "licenses\TINOS-OFL-1.1.txt",
    "docs\engineering-family-v080.md",
    "scripts\Install-TishteSerifFamilyV080.ps1",
    "scripts\Uninstall-TishteSerifFamilyV080.ps1",
    "scripts\Install-TishteSerifFamilyV060.ps1",
    "scripts\Uninstall-TishteSerifFamilyV060.ps1"
)
foreach ($file in $files) { Copy-Item -LiteralPath (Join-Path $workspace $file) -Destination $stage -Force }
Get-ChildItem -LiteralPath $stage -File | Sort-Object Name | Get-FileHash -Algorithm SHA256 |
    ForEach-Object { "$($_.Hash.ToLower())  $([IO.Path]::GetFileName($_.Path))" } |
    Set-Content -LiteralPath (Join-Path $stage "SHA256SUMS.txt") -Encoding UTF8
Compress-Archive -LiteralPath $stage -DestinationPath $archive -CompressionLevel Optimal -Force
[ordered]@{ package = $archive; files = (Get-ChildItem $stage -File).Count; bytes = (Get-Item $archive).Length } | ConvertTo-Json
