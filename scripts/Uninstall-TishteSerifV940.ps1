[CmdletBinding()]
param()

& (Join-Path $PSScriptRoot "Uninstall-TishteSerifFamilyV060.ps1") `
    -Version 940 -FamilyName "Tishte Serif"
