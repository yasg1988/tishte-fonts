[CmdletBinding()]
param(
    [string]$OutputRoot = "artifacts\office-tests\v060\powerpoint",
    [string]$VersionLabel = "v0.060",
    [string]$VersionTag = "v060",
    [string]$TishteFontName = "Tishte Serif Prototype"
)

$ErrorActionPreference = "Stop"
$root = [System.IO.Path]::GetFullPath((Join-Path (Get-Location) $OutputRoot))
New-Item -ItemType Directory -Path $root -Force | Out-Null

$ppLayoutBlank = 12
$ppSaveAsOpenXMLPresentation = 24
$ppSaveAsPDF = 32
$msoTextOrientationHorizontal = 1
$msoFalse = 0
$msoTrue = -1
$white = 0xFFFFFF
$ink = 0x24211F
$accent = 0x34248F
$muted = 0x817A72
$paper = 0xF7F4EF
$nbsp = [char]0x00A0

function Add-Text {
    param(
        $Slide,
        [string]$Text,
        [double]$Left,
        [double]$Top,
        [double]$Width,
        [double]$Height,
        [string]$FontName,
        [double]$Size,
        [bool]$Bold = $false,
        [bool]$Italic = $false,
        [int]$Color = $ink
    )
    $shape = $Slide.Shapes.AddTextbox($msoTextOrientationHorizontal, $Left, $Top, $Width, $Height)
    $shape.TextFrame2.TextRange.Text = $Text
    $shape.TextFrame2.TextRange.Font.Name = $FontName
    $shape.TextFrame2.TextRange.Font.Size = $Size
    $shape.TextFrame2.TextRange.Font.Bold = if ($Bold) { $msoTrue } else { $msoFalse }
    $shape.TextFrame2.TextRange.Font.Italic = if ($Italic) { $msoTrue } else { $msoFalse }
    $shape.TextFrame2.TextRange.Font.Fill.ForeColor.RGB = $Color
    $shape.TextFrame2.MarginLeft = 0
    $shape.TextFrame2.MarginRight = 0
    $shape.TextFrame2.MarginTop = 0
    $shape.TextFrame2.MarginBottom = 0
    $shape.TextFrame2.WordWrap = $msoTrue
    return $shape
}

function Add-Footer {
    param($Slide, [string]$FontName, [int]$Page)
    [void](Add-Text $Slide "TISHTE SERIF $VersionLabel · КОНТРОЛЬ POWERPOINT" 42 510 650 16 $FontName 8 $false $false $muted)
    [void](Add-Text $Slide ([string]$Page) 900 510 20 16 $FontName 8 $false $false $muted)
}

function Build-Deck {
    param($PowerPoint, [string]$FontName, [string]$Variant)
    $deck = $PowerPoint.Presentations.Add()
    try {
        $deck.PageSetup.SlideWidth = 960
        $deck.PageSetup.SlideHeight = 540
        try { $deck.EmbedTrueTypeFonts = $msoTrue } catch { }

        $slide = $deck.Slides.Add(1, $ppLayoutBlank)
        $slide.Background.Fill.ForeColor.RGB = $paper
        $bar = $slide.Shapes.AddShape(1, 0, 0, 20, 540)
        $bar.Fill.ForeColor.RGB = $accent
        $bar.Line.Visible = $msoFalse
        [void](Add-Text $slide "ИНЖЕНЕРНЫЙ КОМПЛЕКТ" 70 74 760 24 $FontName 13 $true $false $accent)
        [void](Add-Text $slide "Четыре начертания теперь сохраняют раскладку Times New Roman." 70 122 780 130 $FontName 34 $true)
        [void](Add-Text $slide "Tishte Serif $VersionLabel · $Variant" 70 300 600 30 $FontName 18 $false $true $muted)
        [void](Add-Text $slide "Regular · Bold · Italic · Bold Italic" 70 356 650 34 $FontName 22)
        Add-Footer $slide $FontName 1

        $slide = $deck.Slides.Add(2, $ppLayoutBlank)
        $slide.Background.Fill.ForeColor.RGB = $paper
        [void](Add-Text $slide "ДВА МАРИЙСКИХ ЯЗЫКА" 48 34 500 20 $FontName 11 $true $false $accent)
        [void](Add-Text $slide "Луговомарийский и горномарийский проверяются отдельно." 48 70 820 60 $FontName 28 $true)
        [void](Add-Text $slide "ЛУГОВОМАРИЙСКИЙ" 48 164 360 24 $FontName 13 $true $false $accent)
        [void](Add-Text $slide "Ӓ ӓ   Ӧ ӧ   Ӱ ӱ   Ҥ ҥ`nМарий Эл Республикын Кугыжаныш Погынжо" 48 202 390 110 $FontName 24)
        [void](Add-Text $slide "ГОРНОМАРИЙСКИЙ" 510 164 360 24 $FontName 13 $true $false $accent)
        [void](Add-Text $slide "Ӓ ӓ   Ӧ ӧ   Ӱ ӱ   Ӹ ӹ`nШачмы йӹлмем ылеш сӹлнӹ." 510 202 390 110 $FontName 24)
        [void](Add-Text $slide "ABC xyz · 0123456789 · пробел: A B · NBSP: A${nbsp}B · № ₽ € £ ¥ · ± × ÷ ≠ ≤ ≥ · ← ↑ → ↓ ↔" 48 390 850 34 $FontName 18)
        Add-Footer $slide $FontName 2

        $slide = $deck.Slides.Add(3, $ppLayoutBlank)
        $slide.Background.Fill.ForeColor.RGB = $paper
        [void](Add-Text $slide "НАЧЕРТАНИЯ" 48 34 260 20 $FontName 11 $true $false $accent)
        [void](Add-Text $slide "Одно семейство, четыре реальных файла." 48 70 820 50 $FontName 28 $true)
        $rows = @(
            @{ Y = 150; Label = "Regular"; Bold = $false; Italic = $false },
            @{ Y = 222; Label = "Bold"; Bold = $true; Italic = $false },
            @{ Y = 294; Label = "Italic"; Bold = $false; Italic = $true },
            @{ Y = 366; Label = "Bold Italic"; Bold = $true; Italic = $true }
        )
        foreach ($row in $rows) {
            [void](Add-Text $slide $row.Label 48 $row.Y 150 28 $FontName 12 $true $false $accent)
            [void](Add-Text $slide "Республика Марий Эл · Ӓ ӓ Ӧ ӧ Ӱ ӱ Ӹ ӹ Ҥ ҥ · 0123456789" 210 $row.Y 690 38 $FontName 20 $row.Bold $row.Italic)
        }
        Add-Footer $slide $FontName 3

        $slide = $deck.Slides.Add(4, $ppLayoutBlank)
        $slide.Background.Fill.ForeColor.RGB = $paper
        [void](Add-Text $slide "ПЛОТНАЯ ТАБЛИЦА" 48 34 300 20 $FontName 11 $true $false $accent)
        [void](Add-Text $slide "Числа и служебные знаки остаются читаемыми на 10–12 pt." 48 70 820 48 $FontName 27 $true)
        $tableShape = $slide.Shapes.AddTable(9, 5, 48, 142, 864, 304)
        $table = $tableShape.Table
        $headers = @("№", "Язык", "Контроль", "Сумма", "Статус")
        for ($column = 1; $column -le 5; $column++) { $table.Cell(1, $column).Shape.TextFrame2.TextRange.Text = $headers[$column - 1] }
        $langs = @("Русский", "Луговой", "Горный", "Latin")
        $glyphs = @("Ё ё · № ₽", "Ӓ ӓ Ӧ ӧ Ӱ ӱ Ҥ ҥ", "Ӓ ӓ Ӧ ӧ Ӱ ӱ Ӹ ӹ", "ABC xyz · € ±")
        for ($row = 2; $row -le 9; $row++) {
            $idx = ($row - 2) % 4
            $values = @([string]($row - 1), $langs[$idx], $glyphs[$idx], ("{0:N2} ₽" -f (125000 + $row * 137.45)), "проверено")
            for ($column = 1; $column -le 5; $column++) { $table.Cell($row, $column).Shape.TextFrame2.TextRange.Text = $values[$column - 1] }
        }
        for ($row = 1; $row -le 9; $row++) {
            for ($column = 1; $column -le 5; $column++) {
                $cell = $table.Cell($row, $column).Shape
                $cell.TextFrame2.TextRange.Font.Name = $FontName
                $cell.TextFrame2.TextRange.Font.Size = if ($row -eq 1) { 11 } else { 10 }
                $cell.TextFrame2.TextRange.Font.Bold = if ($row -eq 1) { $msoTrue } else { $msoFalse }
                $cell.TextFrame2.TextRange.Font.Fill.ForeColor.RGB = if ($row -eq 1) { $white } else { $ink }
                $cell.Fill.Solid()
                $fillColor = if ($row -eq 1) { $accent } elseif ($row % 2 -eq 0) { $paper } else { $white }
                $cell.Fill.ForeColor.RGB = $fillColor
                $cell.TextFrame2.MarginLeft = 6
                $cell.TextFrame2.MarginRight = 6
                $cell.TextFrame2.MarginTop = 3
                $cell.TextFrame2.MarginBottom = 3
            }
        }
        Add-Footer $slide $FontName 4

        $pptx = Join-Path $root "tishte-serif-$VersionTag-$($Variant.ToLower()).pptx"
        $pdf = Join-Path $root "tishte-serif-$VersionTag-$($Variant.ToLower()).pdf"
        $deck.SaveAs($pptx, $ppSaveAsOpenXMLPresentation, $msoTrue)
        $deck.SaveAs($pdf, $ppSaveAsPDF)
        return [ordered]@{ pptx = $pptx; pdf = $pdf; slides = $deck.Slides.Count }
    }
    finally {
        $deck.Close()
        [void][Runtime.InteropServices.Marshal]::ReleaseComObject($deck)
    }
}

$powerPoint = $null
try {
    $powerPoint = New-Object -ComObject PowerPoint.Application
    $powerPoint.Visible = $msoTrue
    $results = @(
        (Build-Deck $powerPoint "Times New Roman" "Times"),
        (Build-Deck $powerPoint $TishteFontName "Tishte")
    )
    $results | ConvertTo-Json -Depth 4
}
finally {
    if ($powerPoint) {
        $powerPoint.Quit()
        [void][Runtime.InteropServices.Marshal]::ReleaseComObject($powerPoint)
    }
    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()
}
