[CmdletBinding()]
param(
    [string]$CorpusRoot = "artifacts\office-tests\v070\excel",
    [string]$VersionTag = "v070"
)

$ErrorActionPreference = "Stop"
$root = [System.IO.Path]::GetFullPath((Join-Path (Get-Location) $CorpusRoot))
$excel = $null
$results = @()
try {
    $excel = New-Object -ComObject Excel.Application
    $excel.Visible = $false
    $excel.DisplayAlerts = $false
    foreach ($variant in @("times", "tishte")) {
        $path = Join-Path $root "tishte-serif-$VersionTag-$variant.xlsx"
        $book = $null
        try {
            $book = $excel.Workbooks.Open($path, 0, $true)
            $excel.CalculateFullRebuild()
            $formulaErrors = 0
            foreach ($sheet in $book.Worksheets) {
                foreach ($cell in $sheet.UsedRange.Cells) {
                    if ($cell.HasFormula -and [Runtime.InteropServices.Marshal]::IsComObject($cell)) {
                        $text = [string]$cell.Text
                        if ($text.StartsWith("#")) { $formulaErrors++ }
                    }
                    [void][Runtime.InteropServices.Marshal]::ReleaseComObject($cell)
                }
            }
            $pdf = Join-Path $root "tishte-serif-$VersionTag-$variant.pdf"
            $book.ExportAsFixedFormat(0, $pdf)
            $results += [ordered]@{
                variant = $variant
                sheets = $book.Worksheets.Count
                formula_errors = $formulaErrors
                pdf = $pdf
            }
        }
        finally {
            if ($book) {
                $book.Close($false)
                [void][Runtime.InteropServices.Marshal]::ReleaseComObject($book)
            }
        }
    }
}
finally {
    if ($excel) {
        $excel.Quit()
        [void][Runtime.InteropServices.Marshal]::ReleaseComObject($excel)
    }
    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()
}
$summary = [ordered]@{
    results = $results
    passed = (($results.Count -eq 2) -and (($results | Where-Object { $_.sheets -ne 2 -or $_.formula_errors -ne 0 }).Count -eq 0))
}
$summary | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $root "audit-report.json") -Encoding UTF8
$summary | ConvertTo-Json -Depth 5
