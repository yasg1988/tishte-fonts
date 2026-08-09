[CmdletBinding()]
param(
    [string]$CorpusRoot = "artifacts\document-tests\v070"
)

$ErrorActionPreference = "Stop"
$root = [System.IO.Path]::GetFullPath((Join-Path (Get-Location) $CorpusRoot))
$docxDir = Join-Path $root "docx"
$pdfDir = Join-Path $root "pdf"
New-Item -ItemType Directory -Path $pdfDir -Force | Out-Null
$word = $null
$exported = @()
try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
    foreach ($source in Get-ChildItem -LiteralPath $docxDir -Filter *.docx | Sort-Object Name) {
        $document = $null
        try {
            $document = $word.Documents.Open($source.FullName, $false, $true)
            $target = Join-Path $pdfDir ($source.BaseName + ".pdf")
            $document.ExportAsFixedFormat($target, 17)
            $exported += $target
        }
        finally {
            if ($document) {
                $document.Close($false)
                [void][Runtime.InteropServices.Marshal]::ReleaseComObject($document)
            }
        }
    }
}
finally {
    if ($word) {
        $word.Quit()
        [void][Runtime.InteropServices.Marshal]::ReleaseComObject($word)
    }
    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()
}
$exported | ConvertTo-Json
