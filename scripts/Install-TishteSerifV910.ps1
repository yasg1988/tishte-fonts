[CmdletBinding()]
param([string]$BuildDirectory = "build")

& (Join-Path $PSScriptRoot "Install-TishteSerifFamilyV060.ps1") `
    -BuildDirectory $BuildDirectory -Version 910 -FamilyName "Tishte Serif"
