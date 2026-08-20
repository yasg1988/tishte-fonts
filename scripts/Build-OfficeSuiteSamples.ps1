param(
    [string]$Root = (Split-Path -Parent $PSScriptRoot),
    [string]$OutputDirectory = "partner-kit\samples",
    [string]$QaDirectory = "build\partner-kit-qa"
)

$ErrorActionPreference = "Stop"
$rootPath = (Resolve-Path -LiteralPath $Root).Path
$outputPath = Join-Path $rootPath $OutputDirectory
$qaPath = Join-Path $rootPath $QaDirectory
New-Item -ItemType Directory -Force -Path $outputPath, $qaPath | Out-Null

$sampleRussian = "Съешь ещё этих мягких французских булок, да выпей чаю."
$sampleMari = "Луговой марийский: Ӓӓ Ӧӧ Ӱӱ Ҥҥ.  Горномарийский: Ӓӓ Ӧӧ Ӱӱ Ӹӹ."
$sampleLatin = "The quick brown fox jumps over the lazy dog.  0123456789  ₽ € $ £ ¥"

$word = $null
$originalWordUserName = $null
try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
    $originalWordUserName = $word.UserName
    $word.UserName = "Tishte Project"
    $document = $word.Documents.Add()
    $section = $document.Sections.Item(1)
    $section.PageSetup.PaperSize = 2 # wdPaperLetter
    $section.PageSetup.TopMargin = 72
    $section.PageSetup.BottomMargin = 72
    $section.PageSetup.LeftMargin = 72
    $section.PageSetup.RightMargin = 72

    $wordLines = @(
        @("Tishte: проверка в текстовом редакторе", "Tishte Serif", 24, $true, $false),
        @("Tishte Serif — документный текст", "Tishte Serif", 16, $true),
        @($sampleRussian, "Tishte Serif", 12, $false),
        @($sampleMari, "Tishte Serif", 12, $false),
        @($sampleLatin, "Tishte Serif", 12, $false),
        @("Tishte Sans — интерфейсы и презентации", "Tishte Sans", 16, $true),
        @($sampleRussian, "Tishte Sans", 12, $false),
        @($sampleMari, "Tishte Sans", 12, $false),
        @($sampleLatin, "Tishte Sans", 12, $false),
        @("Проверка начертаний: обычный, полужирный, курсив, полужирный курсив.", "Tishte Serif", 12, $false, $true)
    )
    $document.Content.Text = (($wordLines | ForEach-Object { $_[0] }) -join "`r")
    for ($index = 0; $index -lt $wordLines.Count; $index++) {
        $item = $wordLines[$index]
        $paragraph = $document.Paragraphs.Item($index + 1)
        $paragraph.Range.Font.Name = $item[1]
        $paragraph.Range.Font.NameAscii = $item[1]
        $paragraph.Range.Font.NameOther = $item[1]
        $paragraph.Range.Font.Size = $item[2]
        $paragraph.Range.Font.Bold = if ($item[3]) { -1 } else { 0 }
        $paragraph.Range.Font.Italic = if ($item.Count -gt 4 -and $item[4]) { -1 } else { 0 }
        $paragraph.Format.SpaceAfter = if ($index -in @(0, 4)) { 14 } else { 8 }
    }

    $docxPath = Join-Path $outputPath "Tishte-office-test.docx"
    $odtPath = Join-Path $outputPath "Tishte-office-test.odt"
    $pdfPath = Join-Path $qaPath "Tishte-office-test-word.pdf"
    $document.SaveAs2($docxPath, 16) # wdFormatDocumentDefault
    $document.ExportAsFixedFormat($pdfPath, 17) # wdExportFormatPDF
    $document.Close(0)
    $document = $word.Documents.Open($docxPath, $false, $false)
    $document.SaveAs2($odtPath, 23) # wdFormatOpenDocumentText
    $document.Close(0)
    $document = $word.Documents.Open($odtPath, $false, $true)
    $document.ExportAsFixedFormat((Join-Path $qaPath "Tishte-office-test-odt.pdf"), 17)
    $document.Close(0)
}
finally {
    if ($word) {
        if ($null -ne $originalWordUserName) { $word.UserName = $originalWordUserName }
        $word.Quit()
    }
}

$excel = $null
$originalExcelUserName = $null
try {
    $excel = New-Object -ComObject Excel.Application
    $excel.Visible = $false
    $excel.DisplayAlerts = $false
    $originalExcelUserName = $excel.UserName
    $excel.UserName = "Tishte Project"
    $workbook = $excel.Workbooks.Add()
    $sheet = $workbook.Worksheets.Item(1)
    $sheet.Name = "Tishte"
    $sheet.Cells.Font.Name = "Tishte Sans"
    $sheet.Range("A1:F1").Merge()
    $sheet.Range("A1").Value2 = "Tishte: проверка в электронной таблице"
    $sheet.Range("A1").Font.Name = "Tishte Serif"
    $sheet.Range("A1").Font.Size = 22
    $sheet.Range("A1").Font.Bold = $true
    $headers = @("Язык", "Пример", "Количество", "Цена", "Сумма", "Проверка")
    for ($column = 0; $column -lt $headers.Count; $column++) {
        $sheet.Cells.Item(3, $column + 1).Value2 = $headers[$column]
    }
    $sheet.Range("A4").Value2 = "Русский"
    $sheet.Range("B4").Value2 = $sampleRussian
    $sheet.Range("C4").Value2 = 3.0
    $sheet.Range("D4").Value2 = 1250.50
    $sheet.Range("F4").Value2 = "№ 1"
    $sheet.Range("A5").Value2 = "Луговой марийский"
    $sheet.Range("B5").Value2 = "Ӓӓ Ӧӧ Ӱӱ Ҥҥ"
    $sheet.Range("C5").Value2 = 5.0
    $sheet.Range("D5").Value2 = 980.25
    $sheet.Range("F5").Value2 = "≤ ≥ ≠"
    $sheet.Range("A6").Value2 = "Горномарийский"
    $sheet.Range("B6").Value2 = "Ӓӓ Ӧӧ Ӱӱ Ӹӹ"
    $sheet.Range("C6").Value2 = 7.0
    $sheet.Range("D6").Value2 = 745.00
    $sheet.Range("F6").Value2 = "© ® ™"
    $sheet.Range("E4").Formula = "=C4*D4"
    $sheet.Range("E4:E6").FillDown()
    $sheet.Range("A8").Value2 = "Начертание"
    $sheet.Range("B8").Value2 = "Обычный"
    $sheet.Range("C8").Value2 = "Полужирный"
    $sheet.Range("D8").Value2 = "Курсив"
    $sheet.Range("A9").Value2 = "Tishte Serif"
    $sheet.Range("B9:D9").Value2 = "Текст"
    $sheet.Range("A10").Value2 = "Tishte Sans"
    $sheet.Range("B10:D10").Value2 = "Текст"
    $sheet.Range("C9:C10").Font.Bold = $true
    $sheet.Range("D9:D10").Font.Italic = $true
    $sheet.Range("A3:F3").Font.Bold = $true
    $sheet.Range("A8:D8").Font.Bold = $true
    $sheet.Range("A3:F6").Borders.LineStyle = 1
    $sheet.Range("A8:D10").Borders.LineStyle = 1
    $sheet.Range("D4:E6").NumberFormat = "#,##0.00 [$₽-ru-RU]"
    $sheet.Columns.Item("A").ColumnWidth = 21
    $sheet.Columns.Item("B").ColumnWidth = 58
    $sheet.Columns.Item("C").ColumnWidth = 13
    $sheet.Columns.Item("D").ColumnWidth = 14
    $sheet.Columns.Item("E").ColumnWidth = 16
    $sheet.Columns.Item("F").ColumnWidth = 16
    $sheet.Range("A1:F10").WrapText = $true
    $sheet.Rows.Item(1).RowHeight = 34
    $sheet.Rows.Item("3:10").AutoFit() | Out-Null
    $sheet.PageSetup.PrintArea = '$A$1:$F$10'
    $sheet.PageSetup.Orientation = 2
    $sheet.PageSetup.Zoom = $false
    $sheet.PageSetup.FitToPagesWide = 1
    $sheet.PageSetup.FitToPagesTall = 1

    $xlsxPath = Join-Path $outputPath "Tishte-office-test.xlsx"
    $pdfPath = Join-Path $qaPath "Tishte-office-test-excel.pdf"
    $excel.CalculateFullRebuild()
    $workbook.SaveAs($xlsxPath, 51)
    $sheet.ExportAsFixedFormat(0, $pdfPath)
    $workbook.Close($false)
    $workbook = $excel.Workbooks.Open($xlsxPath, 0, $true)
    $excel.CalculateFullRebuild()
    $workbook.Close($false)
}
finally {
    if ($excel) {
        if ($null -ne $originalExcelUserName) { $excel.UserName = $originalExcelUserName }
        $excel.Quit()
    }
}

$powerPoint = $null
try {
    $powerPoint = New-Object -ComObject PowerPoint.Application
    $presentation = $powerPoint.Presentations.Add()
    $presentation.PageSetup.SlideWidth = 960
    $presentation.PageSetup.SlideHeight = 540
    $slide = $presentation.Slides.Add(1, 12) # ppLayoutBlank
    $title = $slide.Shapes.AddTextbox(1, 54, 30, 850, 55)
    $title.TextFrame.TextRange.Text = "Tishte: проверка в презентации"
    $title.TextFrame.TextRange.Font.Name = "Tishte Serif"
    $title.TextFrame.TextRange.Font.Size = 26
    $title.TextFrame.TextRange.Font.Bold = -1

    $left = $slide.Shapes.AddTextbox(1, 54, 110, 410, 360)
    $left.TextFrame.WordWrap = -1
    $left.TextFrame.AutoSize = 0
    $left.TextFrame.TextRange.Text = "Tishte Serif`r`n`r`n$sampleRussian`r`n`r`n$sampleMari`r`n`r`n$sampleLatin"
    $left.TextFrame.TextRange.Font.Name = "Tishte Serif"
    $left.TextFrame.TextRange.Font.Size = 16
    $left.TextFrame.TextRange.Paragraphs(1).Font.Size = 24
    $left.TextFrame.TextRange.Paragraphs(1).Font.Bold = -1

    $right = $slide.Shapes.AddTextbox(1, 500, 110, 360, 360)
    $right.TextFrame.WordWrap = -1
    $right.TextFrame.AutoSize = 0
    $right.TextFrame.TextRange.Text = "Tishte Sans`r`n`r`n$sampleRussian`r`n`r`n$sampleMari`r`n`r`n$sampleLatin"
    $right.TextFrame.TextRange.Font.Name = "Tishte Sans"
    $right.TextFrame.TextRange.Font.Size = 16
    $right.TextFrame.TextRange.Paragraphs(1).Font.Size = 24
    $right.TextFrame.TextRange.Paragraphs(1).Font.Bold = -1

    $pptxPath = Join-Path $outputPath "Tishte-office-test.pptx"
    $pdfPath = Join-Path $qaPath "Tishte-office-test-powerpoint.pdf"
    $pngPath = Join-Path $qaPath "Tishte-office-test-powerpoint.png"
    $presentation.SaveAs($pptxPath, 24) # ppSaveAsOpenXMLPresentation
    $presentation.SaveAs($pdfPath, 32) # ppSaveAsPDF
    $slide.Export($pngPath, "PNG", 1600, 900)
    $presentation.Close()
    $presentation = $powerPoint.Presentations.Open($pptxPath, $true, $false, $false)
    $presentation.Close()
}
finally {
    if ($powerPoint) {
        $powerPoint.Quit()
    }
}

python (Join-Path $PSScriptRoot "scrub_office_sample_metadata.py") --directory $outputPath
if ($LASTEXITCODE -ne 0) { throw "Office sample metadata scrub failed" }

Get-ChildItem -LiteralPath $outputPath -File | Sort-Object Name | Select-Object Name, Length
