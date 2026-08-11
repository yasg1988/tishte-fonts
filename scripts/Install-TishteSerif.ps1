[CmdletBinding()]
param(
    [string]$FontDirectory = (Join-Path $PSScriptRoot "..\fonts\ttf")
)

$ErrorActionPreference = "Stop"
$fontStore = Join-Path $env:LOCALAPPDATA "Microsoft\Windows\Fonts"
$registryPath = "HKCU:\Software\Microsoft\Windows NT\CurrentVersion\Fonts"
New-Item -ItemType Directory -Path $fontStore -Force | Out-Null
New-Item -Path $registryPath -Force | Out-Null

$styles = @(
    @{ File = "TishteSerif-Regular-v1100.ttf"; Registry = "Tishte Serif (TrueType)" },
    @{ File = "TishteSerif-Bold-v1100.ttf"; Registry = "Tishte Serif Bold (TrueType)" },
    @{ File = "TishteSerif-Italic-v1100.ttf"; Registry = "Tishte Serif Italic (TrueType)" },
    @{ File = "TishteSerif-BoldItalic-v1100.ttf"; Registry = "Tishte Serif Bold Italic (TrueType)" }
)

foreach ($style in $styles) {
    $source = (Resolve-Path -LiteralPath (Join-Path $FontDirectory $style.File)).Path
    $destination = Join-Path $fontStore $style.File
    Copy-Item -LiteralPath $source -Destination $destination -Force
    New-ItemProperty -Path $registryPath -Name $style.Registry -Value $destination `
        -PropertyType String -Force | Out-Null
}

Write-Host "Tishte Serif установлен. Перезапустите открытые приложения."
