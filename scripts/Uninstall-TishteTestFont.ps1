[CmdletBinding()]
param()

$fontPath = Join-Path $env:LOCALAPPDATA "Microsoft\Windows\Fonts\TishteSerif-Regular-v040.ttf"
$registryPath = "HKCU:\Software\Microsoft\Windows NT\CurrentVersion\Fonts"
$registryName = "Tishte Serif Prototype Regular (TrueType)"

if (Test-Path -LiteralPath $registryPath) {
    Remove-ItemProperty -Path $registryPath -Name $registryName -ErrorAction SilentlyContinue
}
if (Test-Path -LiteralPath $fontPath) {
    Remove-Item -LiteralPath $fontPath -Force
}

[ordered]@{
    removed_path = $fontPath
    installed = (Test-Path -LiteralPath $fontPath)
} | ConvertTo-Json
