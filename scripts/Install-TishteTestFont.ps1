[CmdletBinding()]
param(
    [string]$Source = "build\TishteSerif-Regular-v040.ttf"
)

$resolved = (Resolve-Path -LiteralPath $Source).Path
$fontDir = Join-Path $env:LOCALAPPDATA "Microsoft\Windows\Fonts"
if (-not (Test-Path -LiteralPath $fontDir)) {
    New-Item -ItemType Directory -Path $fontDir -Force | Out-Null
}
$destination = Join-Path $fontDir "TishteSerif-Regular-v040.ttf"
Copy-Item -LiteralPath $resolved -Destination $destination -Force

$registryPath = "HKCU:\Software\Microsoft\Windows NT\CurrentVersion\Fonts"
if (-not (Test-Path -LiteralPath $registryPath)) {
    New-Item -Path $registryPath -Force | Out-Null
}
New-ItemProperty `
    -Path $registryPath `
    -Name "Tishte Serif Prototype Regular (TrueType)" `
    -Value $destination `
    -PropertyType String `
    -Force | Out-Null

if (-not ("Tishte.FontBroadcast" -as [type])) {
    Add-Type @"
using System;
using System.Runtime.InteropServices;
namespace Tishte {
    public static class FontBroadcast {
        [DllImport("gdi32.dll", CharSet = CharSet.Unicode)]
        public static extern int AddFontResourceEx(string file, uint flags, IntPtr reserved);
        [DllImport("user32.dll", CharSet = CharSet.Unicode)]
        public static extern IntPtr SendMessageTimeout(
            IntPtr hwnd, uint msg, UIntPtr wParam, string lParam,
            uint flags, uint timeout, out UIntPtr result);
    }
}
"@
}

[void][Tishte.FontBroadcast]::AddFontResourceEx($destination, 0, [IntPtr]::Zero)
$broadcastResult = [UIntPtr]::Zero
[void][Tishte.FontBroadcast]::SendMessageTimeout(
    [IntPtr]0xffff, 0x001D, [UIntPtr]::Zero, $null, 2, 1000, [ref]$broadcastResult
)

[ordered]@{
    source = $resolved
    installed_path = $destination
    registry_name = "Tishte Serif Prototype Regular (TrueType)"
    installed = (Test-Path -LiteralPath $destination)
} | ConvertTo-Json
