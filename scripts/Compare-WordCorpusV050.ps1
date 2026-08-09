[CmdletBinding()]
param(
    [string]$CorpusRoot = "artifacts\document-tests\v050"
)

$ErrorActionPreference = "Stop"
$root = [System.IO.Path]::GetFullPath((Join-Path (Get-Location) $CorpusRoot))
$docxDir = Join-Path $root "docx"
$kinds = @("order", "letter", "protocol", "table", "languages")
$word = $null
$pairs = @()

function Read-Layout {
    param($Word, [string]$Path)
    $doc = $null
    try {
        $doc = $Word.Documents.Open($Path, $false, $true)
        $doc.Repaginate()
        $paragraphs = @()
        for ($index = 1; $index -le $doc.Paragraphs.Count; $index++) {
            $paragraph = $doc.Paragraphs.Item($index)
            $text = ($paragraph.Range.Text -replace "[\r\a]", " ").Trim()
            $paragraphs += [ordered]@{
                index = $index
                text = if ($text.Length -gt 100) { $text.Substring(0, 100) } else { $text }
                lines = $paragraph.Range.ComputeStatistics(1)
                page = $paragraph.Range.Information(3)
                bold = $paragraph.Range.Font.Bold
                font = $paragraph.Range.Font.Name
            }
        }
        return [ordered]@{
            pages = $doc.ComputeStatistics(2)
            lines = $doc.ComputeStatistics(1)
            paragraphs = $paragraphs
        }
    }
    finally {
        if ($doc) {
            $doc.Close($false)
            [void][Runtime.InteropServices.Marshal]::ReleaseComObject($doc)
        }
    }
}

try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
    foreach ($kind in $kinds) {
        $timesPath = Join-Path $docxDir "$kind-times.docx"
        $tishtePath = Join-Path $docxDir "$kind-tishte.docx"
        $times = Read-Layout $word $timesPath
        $tishte = Read-Layout $word $tishtePath
        $differences = @()
        $count = [Math]::Min($times.paragraphs.Count, $tishte.paragraphs.Count)
        for ($index = 0; $index -lt $count; $index++) {
            $left = $times.paragraphs[$index]
            $right = $tishte.paragraphs[$index]
            if ($left.lines -ne $right.lines -or $left.page -ne $right.page) {
                $differences += [ordered]@{
                    paragraph = $index + 1
                    text = $left.text
                    times_lines = $left.lines
                    tishte_lines = $right.lines
                    times_page = $left.page
                    tishte_page = $right.page
                    times_bold = $left.bold
                    tishte_bold = $right.bold
                }
            }
        }
        $pairs += [ordered]@{
            kind = $kind
            times_pages = $times.pages
            tishte_pages = $tishte.pages
            times_lines = $times.lines
            tishte_lines = $tishte.lines
            layout_equal = ($times.pages -eq $tishte.pages -and $differences.Count -eq 0)
            differences = $differences
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

$summary = [ordered]@{
    corpus = $root
    pairs = $pairs
    all_pages_equal = (($pairs | Where-Object { $_.times_pages -ne $_.tishte_pages }).Count -eq 0)
    all_layout_equal = (($pairs | Where-Object { -not $_.layout_equal }).Count -eq 0)
}
$output = Join-Path $root "layout-comparison.json"
$summary | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $output -Encoding UTF8
$summary | ConvertTo-Json -Depth 8
