[CmdletBinding()]
param(
    [string]$Version = "060",
    [string]$FamilyName = "Tishte Serif Prototype"
)

$ErrorActionPreference = "Stop"
$fontDir = Join-Path $env:LOCALAPPDATA "Microsoft\Windows\Fonts"
$registryPath = "HKCU:\Software\Microsoft\Windows NT\CurrentVersion\Fonts"
$styles = @(
    @{ File = "TishteSerif-Regular-v$Version.ttf"; Registry = "$FamilyName (TrueType)" },
    @{ File = "TishteSerif-Bold-v$Version.ttf"; Registry = "$FamilyName Bold (TrueType)" },
    @{ File = "TishteSerif-Italic-v$Version.ttf"; Registry = "$FamilyName Italic (TrueType)" },
    @{ File = "TishteSerif-BoldItalic-v$Version.ttf"; Registry = "$FamilyName Bold Italic (TrueType)" }
)

foreach ($style in $styles) {
    Remove-ItemProperty -Path $registryPath -Name $style.Registry -ErrorAction SilentlyContinue
    $path = Join-Path $fontDir $style.File
    if (Test-Path -LiteralPath $path) { Remove-Item -LiteralPath $path -Force }
}

[ordered]@{ removed = $styles.Count; family = $FamilyName } | ConvertTo-Json
