[CmdletBinding()]
param(
    [string]$OutputRoot = "artifacts\document-tests\v070"
)

$ErrorActionPreference = "Stop"
& (Join-Path $PSScriptRoot "Build-WordCorpusV050.ps1") `
    -OutputRoot $OutputRoot `
    -MilestoneLabel "v0.070" `
    -TishteLabel "TISHTE SERIF v0.070 · CLEAN FOUR-STYLE FAMILY" `
    -IncludeStyleMatrix
