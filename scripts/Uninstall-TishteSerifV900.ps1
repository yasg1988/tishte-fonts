[CmdletBinding()]
param()

& (Join-Path $PSScriptRoot "Uninstall-TishteSerifFamilyV060.ps1") `
    -Version 900 -FamilyName "Tishte Serif"
