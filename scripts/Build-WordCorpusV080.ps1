[CmdletBinding()]
param(
    [string]$OutputRoot = "artifacts\document-tests\v080"
)

$ErrorActionPreference = "Stop"
& (Join-Path $PSScriptRoot "Build-WordCorpusV050.ps1") `
    -OutputRoot $OutputRoot `
    -MilestoneLabel "v0.080" `
    -TishteLabel "TISHTE SERIF v0.080 · SPACE AND SHAPING AUDIT" `
    -IncludeStyleMatrix
