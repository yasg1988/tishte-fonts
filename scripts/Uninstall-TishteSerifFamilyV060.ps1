[CmdletBinding()]
param([string]$Version = "060")

$ErrorActionPreference = "Stop"
$fontDir = Join-Path $env:LOCALAPPDATA "Microsoft\Windows\Fonts"
$registryPath = "HKCU:\Software\Microsoft\Windows NT\CurrentVersion\Fonts"
$styles = @(
    @{ File = "TishteSerif-Regular-v$Version.ttf"; Registry = "Tishte Serif Prototype (TrueType)" },
    @{ File = "TishteSerif-Bold-v$Version.ttf"; Registry = "Tishte Serif Prototype Bold (TrueType)" },
    @{ File = "TishteSerif-Italic-v$Version.ttf"; Registry = "Tishte Serif Prototype Italic (TrueType)" },
    @{ File = "TishteSerif-BoldItalic-v$Version.ttf"; Registry = "Tishte Serif Prototype Bold Italic (TrueType)" }
)

foreach ($style in $styles) {
    Remove-ItemProperty -Path $registryPath -Name $style.Registry -ErrorAction SilentlyContinue
    $path = Join-Path $fontDir $style.File
    if (Test-Path -LiteralPath $path) { Remove-Item -LiteralPath $path -Force }
}

[ordered]@{ removed = $styles.Count; family = "Tishte Serif Prototype" } | ConvertTo-Json
