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
    @{ File = "TishteSans-Regular-v1100.ttf"; Registry = "Tishte Sans (TrueType)" },
    @{ File = "TishteSans-Italic-v1100.ttf"; Registry = "Tishte Sans Italic (TrueType)" },
    @{ File = "TishteSans-Medium-v1100.ttf"; Registry = "Tishte Sans Medium (TrueType)" },
    @{ File = "TishteSans-MediumItalic-v1100.ttf"; Registry = "Tishte Sans Medium Italic (TrueType)" },
    @{ File = "TishteSans-SemiBold-v1100.ttf"; Registry = "Tishte Sans SemiBold (TrueType)" },
    @{ File = "TishteSans-SemiBoldItalic-v1100.ttf"; Registry = "Tishte Sans SemiBold Italic (TrueType)" },
    @{ File = "TishteSans-Bold-v1100.ttf"; Registry = "Tishte Sans Bold (TrueType)" },
    @{ File = "TishteSans-BoldItalic-v1100.ttf"; Registry = "Tishte Sans Bold Italic (TrueType)" },
    @{ File = "TishteSans-ExtraBold-v1100.ttf"; Registry = "Tishte Sans ExtraBold (TrueType)" },
    @{ File = "TishteSans-ExtraBoldItalic-v1100.ttf"; Registry = "Tishte Sans ExtraBold Italic (TrueType)" }
)

foreach ($style in $styles) {
    $source = (Resolve-Path -LiteralPath (Join-Path $FontDirectory $style.File)).Path
    $destination = Join-Path $fontStore $style.File
    Copy-Item -LiteralPath $source -Destination $destination -Force
    New-ItemProperty -Path $registryPath -Name $style.Registry -Value $destination `
        -PropertyType String -Force | Out-Null
}

Write-Host "Tishte Sans установлен. Перезапустите открытые приложения."
