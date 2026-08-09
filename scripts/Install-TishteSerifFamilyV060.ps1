[CmdletBinding()]
param(
    [string]$BuildDirectory = "build",
    [string]$Version = "060"
)

$ErrorActionPreference = "Stop"
$fontDir = Join-Path $env:LOCALAPPDATA "Microsoft\Windows\Fonts"
$registryPath = "HKCU:\Software\Microsoft\Windows NT\CurrentVersion\Fonts"
New-Item -ItemType Directory -Path $fontDir -Force | Out-Null
New-Item -Path $registryPath -Force | Out-Null

$styles = @(
    @{ File = "TishteSerif-Regular-v$Version.ttf"; Registry = "Tishte Serif Prototype (TrueType)" },
    @{ File = "TishteSerif-Bold-v$Version.ttf"; Registry = "Tishte Serif Prototype Bold (TrueType)" },
    @{ File = "TishteSerif-Italic-v$Version.ttf"; Registry = "Tishte Serif Prototype Italic (TrueType)" },
    @{ File = "TishteSerif-BoldItalic-v$Version.ttf"; Registry = "Tishte Serif Prototype Bold Italic (TrueType)" }
)

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

$installed = @()
foreach ($style in $styles) {
    $source = (Resolve-Path -LiteralPath (Join-Path $BuildDirectory $style.File)).Path
    $destination = Join-Path $fontDir $style.File
    Copy-Item -LiteralPath $source -Destination $destination -Force
    New-ItemProperty -Path $registryPath -Name $style.Registry -Value $destination -PropertyType String -Force | Out-Null
    [void][Tishte.FontBroadcast]::AddFontResourceEx($destination, 0, [IntPtr]::Zero)
    $installed += [ordered]@{ style = $style.Registry; path = $destination }
}

# Remove the obsolete single-face v0.040 registration after v0.060 is present.
Remove-ItemProperty -Path $registryPath -Name "Tishte Serif Prototype Regular (TrueType)" -ErrorAction SilentlyContinue
$oldFont = Join-Path $fontDir "TishteSerif-Regular-v040.ttf"
if (Test-Path -LiteralPath $oldFont) { Remove-Item -LiteralPath $oldFont -Force }
if ($Version -ne "060") {
    foreach ($oldStyle in @("Regular", "Bold", "Italic", "BoldItalic")) {
        $oldFamilyFont = Join-Path $fontDir "TishteSerif-$oldStyle-v060.ttf"
        if (Test-Path -LiteralPath $oldFamilyFont) { Remove-Item -LiteralPath $oldFamilyFont -Force }
    }
}

$broadcastResult = [UIntPtr]::Zero
[void][Tishte.FontBroadcast]::SendMessageTimeout(
    [IntPtr]0xffff, 0x001D, [UIntPtr]::Zero, $null, 2, 1000, [ref]$broadcastResult
)

$installed | ConvertTo-Json -Depth 3
