[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$fontStore = Join-Path $env:LOCALAPPDATA "Microsoft\Windows\Fonts"
$registryPath = "HKCU:\Software\Microsoft\Windows NT\CurrentVersion\Fonts"
$styles = @(
    @{ File = "TishteSerif-Regular-v1100.ttf"; Registry = "Tishte Serif (TrueType)" },
    @{ File = "TishteSerif-Bold-v1100.ttf"; Registry = "Tishte Serif Bold (TrueType)" },
    @{ File = "TishteSerif-Italic-v1100.ttf"; Registry = "Tishte Serif Italic (TrueType)" },
    @{ File = "TishteSerif-BoldItalic-v1100.ttf"; Registry = "Tishte Serif Bold Italic (TrueType)" }
)

foreach ($style in $styles) {
    Remove-ItemProperty -Path $registryPath -Name $style.Registry -ErrorAction SilentlyContinue
    $path = Join-Path $fontStore $style.File
    if (Test-Path -LiteralPath $path) {
        Remove-Item -LiteralPath $path -Force
    }
}

Write-Host "Tishte Serif удалён. Перезапустите открытые приложения."
