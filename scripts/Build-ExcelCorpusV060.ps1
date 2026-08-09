[CmdletBinding()]
param(
    [string]$OutputRoot = "artifacts\office-tests\v060\excel",
    [string]$VersionLabel = "v0.060",
    [string]$VersionTag = "v060",
    [string]$TishteFontName = "Tishte Serif Prototype"
)

$ErrorActionPreference = "Stop"
$root = [System.IO.Path]::GetFullPath((Join-Path (Get-Location) $OutputRoot))
New-Item -ItemType Directory -Path $root -Force | Out-Null

$xlOpenXMLWorkbook = 51
$xlLandscape = 2
$xlCenter = -4108
$xlLeft = -4131
$xlRight = -4152
$xlContinuous = 1
$xlThin = 2
$accent = 0x34248F
$accentSoft = 0xE9E2F4
$surface = 0xF7F4EF
$border = 0xD2CCC4
$nbsp = [char]0x00A0

function Set-Font {
    param($Range, [string]$FontName, [double]$Size = 11, [bool]$Bold = $false, [bool]$Italic = $false)
    $Range.Font.Name = $FontName
    $Range.Font.Size = $Size
    $Range.Font.Bold = $Bold
    $Range.Font.Italic = $Italic
}

function Style-Range {
    param($Range, [int]$Color = $border)
    $Range.Borders.LineStyle = $xlContinuous
    $Range.Borders.Weight = $xlThin
    $Range.Borders.Color = $Color
}

function Configure-Sheet {
    param($Sheet)
    $Sheet.Activate()
    $Sheet.Application.ActiveWindow.DisplayGridlines = $false
    $Sheet.PageSetup.Orientation = $xlLandscape
    $Sheet.PageSetup.PaperSize = 9
    $Sheet.PageSetup.LeftMargin = $Sheet.Application.CentimetersToPoints(1.5)
    $Sheet.PageSetup.RightMargin = $Sheet.Application.CentimetersToPoints(1.5)
    $Sheet.PageSetup.TopMargin = $Sheet.Application.CentimetersToPoints(1.5)
    $Sheet.PageSetup.BottomMargin = $Sheet.Application.CentimetersToPoints(1.5)
    $Sheet.PageSetup.Zoom = $false
    $Sheet.PageSetup.FitToPagesWide = 1
    $Sheet.PageSetup.FitToPagesTall = 1
}

function Build-Workbook {
    param($Excel, [string]$FontName, [string]$Variant)
    Write-Host "Starting workbook: $Variant"
    $book = $Excel.Workbooks.Add()
    Write-Host "Workbook created: $Variant"
    try {
        while ($book.Worksheets.Count -lt 2) { [void]$book.Worksheets.Add() }
        while ($book.Worksheets.Count -gt 2) { $book.Worksheets.Item($book.Worksheets.Count).Delete() }
        $registry = $book.Worksheets.Item(1)
        $registry.Name = "Реестр"
        $styles = $book.Worksheets.Item(2)
        $styles.Name = "Начертания"
        Write-Host "Sheets named: $Variant"

        # Populate the dense data block before page setup and visual styling.
        # Excel otherwise recalculates print pagination after every COM write.
        $languageRows = @(
            @{ Name = "Русский"; Glyphs = "Республика Марий Эл · Ё ё" },
            @{ Name = "Луговомарийский"; Glyphs = "Ӓ ӓ · Ӧ ӧ · Ӱ ӱ · Ҥ ҥ" },
            @{ Name = "Горномарийский"; Glyphs = "Ӓ ӓ · Ӧ ӧ · Ӱ ӱ · Ӹ ӹ" },
            @{ Name = "Latin"; Glyphs = "ABC xyz · № ₽ € ± ≤ ≥" }
        )
        $data = New-Object 'object[,]' 36, 8
        for ($index = 1; $index -le 36; $index++) {
            $language = $languageRows[($index - 1) % $languageRows.Count]
            $rowIndex = $index - 1
            $data[$rowIndex, 0] = $index
            $data[$rowIndex, 1] = "Контрольный документ № $index/2026"
            $data[$rowIndex, 2] = $language.Name
            $data[$rowIndex, 3] = $language.Glyphs
            $data[$rowIndex, 4] = [datetime]::new(2026, 8, (($index - 1) % 28) + 1).ToOADate()
            $data[$rowIndex, 5] = 125000 + ($index * 137.45)
            $data[$rowIndex, 6] = 0.55 + (($index % 10) / 20)
            $data[$rowIndex, 7] = if ($index % 3 -eq 0) { "проверено" } else { "в работе" }
        }
        $registry.Range("A5:H40").Value2 = $data
        Write-Host "Registry data ready: $Variant"

        $registry.Activate()
        $registry.Application.ActiveWindow.DisplayGridlines = $false
        $registry.Range("A1:H1").Merge()
        $registry.Range("A1").Value2 = "TISHTE SERIF $VersionLabel · КОНТРОЛЬ EXCEL · $Variant"
        Set-Font $registry.Range("A1") $FontName 18 $true
        $registry.Range("A1").Font.Color = 0xFFFFFF
        $registry.Range("A1:H1").Interior.Color = $accent
        $registry.Range("A1:H1").HorizontalAlignment = $xlLeft
        $registry.Rows.Item(1).RowHeight = 34

        $registry.Range("A2:H2").Merge()
        $registry.Range("A2").Value2 = "Тестовый реестр: русский, луговомарийский, горномарийский, латиница, цифры и специальные знаки"
        Set-Font $registry.Range("A2") $FontName 11 $false $true
        $registry.Range("A2:H2").Interior.Color = $surface
        $registry.Rows.Item(2).RowHeight = 24

        $headers = @("№", "Документ", "Язык", "Контрольные знаки", "Дата", "Сумма", "Исполнение", "Статус")
        for ($column = 1; $column -le $headers.Count; $column++) {
            $registry.Cells.Item(4, $column).Value2 = $headers[$column - 1]
        }
        Set-Font $registry.Range("A4:H4") $FontName 11 $true
        $registry.Range("A4:H4").Interior.Color = $accentSoft
        $registry.Range("A4:H4").HorizontalAlignment = $xlCenter
        $registry.Rows.Item(4).RowHeight = 27
        Write-Host "Registry header ready: $Variant"

        Set-Font $registry.Range("A5:H40") $FontName 10
        $registry.Range("E5:E40").NumberFormat = "dd.mm.yyyy"
        $registry.Range("F5:F40").NumberFormat = "# ##0,00 ₽"
        $registry.Range("G5:G40").NumberFormat = "0%"
        $registry.Range("A5:A40").HorizontalAlignment = $xlCenter
        $registry.Range("E5:E40").HorizontalAlignment = $xlCenter
        $registry.Range("F5:G40").HorizontalAlignment = $xlRight
        $registry.Range("H5:H40").HorizontalAlignment = $xlCenter
        for ($row = 5; $row -le 40; $row += 2) { $registry.Range("A$row:H$row").Interior.Color = $surface }
        Style-Range $registry.Range("A4:H40")

        $registry.Range("E42").Value2 = "Итого"
        $registry.Range("F42").Formula = "=SUM(F5:F40)"
        $registry.Range("G42").Formula = "=AVERAGE(G5:G40)"
        Set-Font $registry.Range("E42:G42") $FontName 11 $true
        $registry.Range("F42").NumberFormat = "# ##0,00 ₽"
        $registry.Range("G42").NumberFormat = "0%"
        $registry.Range("E42:G42").Interior.Color = $accentSoft
        Style-Range $registry.Range("E42:G42")

        $widths = @(5, 28, 19, 30, 12, 15, 12, 12)
        for ($column = 1; $column -le 8; $column++) { $registry.Columns.Item($column).ColumnWidth = $widths[$column - 1] }
        $registry.Range("A4:H40").WrapText = $false
        $registry.Range("A4:H40").AutoFilter() | Out-Null
        Write-Host "Registry formatted: $Variant"
        $registry.Application.ActiveWindow.SplitRow = 4
        $registry.Application.ActiveWindow.FreezePanes = $true
        Configure-Sheet $registry
        $registry.PageSetup.PrintArea = '$A$1:$H$42'
        Write-Host "Registry sheet ready: $Variant"

        $styles.Activate()
        $styles.Application.ActiveWindow.DisplayGridlines = $false
        $styles.Range("A1:F1").Merge()
        $styles.Range("A1").Value2 = "ЧЕТЫРЕ НАЧЕРТАНИЯ ОДНОГО СЕМЕЙСТВА"
        Set-Font $styles.Range("A1") $FontName 18 $true
        $styles.Range("A1:F1").Interior.Color = $accent
        $styles.Range("A1").Font.Color = 0xFFFFFF
        $styles.Rows.Item(1).RowHeight = 34
        $samples = @(
            @{ Row = 4; Label = "Regular"; Bold = $false; Italic = $false },
            @{ Row = 7; Label = "Bold"; Bold = $true; Italic = $false },
            @{ Row = 10; Label = "Italic"; Bold = $false; Italic = $true },
            @{ Row = 13; Label = "Bold Italic"; Bold = $true; Italic = $true }
        )
        foreach ($sample in $samples) {
            $styles.Range("A$($sample.Row):F$($sample.Row)").Merge()
            $styles.Cells.Item($sample.Row, 1).Value2 = $sample.Label
            Set-Font $styles.Cells.Item($sample.Row, 1) $FontName 11 $true
            $styles.Range("A$($sample.Row):F$($sample.Row)").Interior.Color = $accentSoft
            $textRow = $sample.Row + 1
            $styles.Range("A$textRow:F$textRow").Merge()
            $styles.Cells.Item($textRow, 1).Value2 = "Республика Марий Эл · Ӓ ӓ Ӧ ӧ Ӱ ӱ Ӹ ӹ Ҥ ҥ · ABC xyz · 0123456789 · № ₽ € ± ≤ ≥"
            Set-Font $styles.Cells.Item($textRow, 1) $FontName 16 $sample.Bold $sample.Italic
            $styles.Rows.Item($textRow).RowHeight = 30
        }
        $styles.Range("A17:F17").Merge()
        $styles.Range("A17").Value2 = "Формулы: 125${nbsp}000,00 ₽ + 25% · пробел: A B · NBSP: A${nbsp}B · даты: 09.08.2026 · знаки: ← ↑ → ↓ ↔"
        Set-Font $styles.Range("A17") $FontName 13
        $styles.Columns.Item(1).ColumnWidth = 24
        foreach ($column in 2..6) { $styles.Columns.Item($column).ColumnWidth = 15 }
        Configure-Sheet $styles
        $styles.PageSetup.PrintArea = '$A$1:$F$18'
        Write-Host "Styles sheet ready: $Variant"

        $Excel.CalculateFullRebuild()
        $path = Join-Path $root "tishte-serif-$VersionTag-$($Variant.ToLower()).xlsx"
        Write-Host "Saving: $path"
        $book.SaveAs($path, $xlOpenXMLWorkbook)
        Write-Host "Saved: $path"
        return $path
    }
    finally {
        $book.Close($true)
        [void][Runtime.InteropServices.Marshal]::ReleaseComObject($book)
    }
}

$excel = $null
try {
    $excel = New-Object -ComObject Excel.Application
    $excel.Visible = $false
    $excel.DisplayAlerts = $false
    $paths = @(
        (Build-Workbook $excel "Times New Roman" "Times"),
        (Build-Workbook $excel $TishteFontName "Tishte")
    )
    $paths | ConvertTo-Json
}
finally {
    if ($excel) {
        $excel.Quit()
        [void][Runtime.InteropServices.Marshal]::ReleaseComObject($excel)
    }
    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()
}
