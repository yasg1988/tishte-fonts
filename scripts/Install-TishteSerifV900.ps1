[CmdletBinding()]
param([string]$BuildDirectory = "build")

& (Join-Path $PSScriptRoot "Install-TishteSerifFamilyV060.ps1") `
    -BuildDirectory $BuildDirectory -Version 900 -FamilyName "Tishte Serif"
