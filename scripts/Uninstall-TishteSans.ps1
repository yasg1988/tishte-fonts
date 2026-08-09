[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$fontStore = Join-Path $env:LOCALAPPDATA "Microsoft\Windows\Fonts"
$registryPath = "HKCU:\Software\Microsoft\Windows NT\CurrentVersion\Fonts"
$styles = @(
    @{ File = "TishteSans-Regular-v1000.ttf"; Registry = "Tishte Sans (TrueType)" },
    @{ File = "TishteSans-Italic-v1000.ttf"; Registry = "Tishte Sans Italic (TrueType)" },
    @{ File = "TishteSans-Medium-v1000.ttf"; Registry = "Tishte Sans Medium (TrueType)" },
    @{ File = "TishteSans-MediumItalic-v1000.ttf"; Registry = "Tishte Sans Medium Italic (TrueType)" },
    @{ File = "TishteSans-SemiBold-v1000.ttf"; Registry = "Tishte Sans SemiBold (TrueType)" },
    @{ File = "TishteSans-SemiBoldItalic-v1000.ttf"; Registry = "Tishte Sans SemiBold Italic (TrueType)" },
    @{ File = "TishteSans-Bold-v1000.ttf"; Registry = "Tishte Sans Bold (TrueType)" },
    @{ File = "TishteSans-BoldItalic-v1000.ttf"; Registry = "Tishte Sans Bold Italic (TrueType)" }
)

foreach ($style in $styles) {
    Remove-ItemProperty -Path $registryPath -Name $style.Registry -ErrorAction SilentlyContinue
    $path = Join-Path $fontStore $style.File
    if (Test-Path -LiteralPath $path) {
        Remove-Item -LiteralPath $path -Force
    }
}

Write-Host "Tishte Sans удалён. Перезапустите открытые приложения."
