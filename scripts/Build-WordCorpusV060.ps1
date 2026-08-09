[CmdletBinding()]
param(
    [string]$OutputRoot = "artifacts\document-tests\v060"
)

$ErrorActionPreference = "Stop"
& (Join-Path $PSScriptRoot "Build-WordCorpusV050.ps1") `
    -OutputRoot $OutputRoot `
    -MilestoneLabel "v0.060" `
    -TishteLabel "TISHTE SERIF v0.060 · FOUR-STYLE FAMILY" `
    -IncludeStyleMatrix
