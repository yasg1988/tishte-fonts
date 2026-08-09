[CmdletBinding()]
param(
    [string]$OutputRoot = "artifacts\document-tests\v050",
    [string]$MilestoneLabel = "v0.050",
    [string]$TishteLabel = "TISHTE SERIF v0.040",
    [switch]$IncludeStyleMatrix
)

$ErrorActionPreference = "Stop"
$root = [System.IO.Path]::GetFullPath((Join-Path (Get-Location) $OutputRoot))
$docxDir = Join-Path $root "docx"
New-Item -ItemType Directory -Path $docxDir -Force | Out-Null

$wdStyleTypeParagraph = 1
$wdAlignLeft = 0
$wdAlignCenter = 1
$wdAlignRight = 2
$wdAlignJustify = 3
$wdLineSpaceSingle = 0
$wdPageBreak = 7
$wdFormatDocumentDefault = 16
$wdFieldPage = 33
$wdCollapseEnd = 0
$wdBorderNone = 0
$nbsp = [char]0x00A0

function Set-StyleFont {
    param(
        $Style,
        [string]$FontName,
        [double]$Size,
        [bool]$Bold = $false,
        [bool]$Italic = $false
    )
    $Style.Font.Name = $FontName
    $Style.Font.NameAscii = $FontName
    $Style.Font.Size = $Size
    $Style.Font.Bold = if ($Bold) { -1 } else { 0 }
    $Style.Font.Italic = if ($Italic) { -1 } else { 0 }
}

function Add-CorpusStyles {
    param($Document, [string]$FontName)
    $styles = @(
        @{ Name = "Tishte Body"; Size = 14; Bold = $false; Italic = $false; Align = $wdAlignJustify; Before = 0; After = 0 },
        @{ Name = "Tishte Title"; Size = 14; Bold = $true; Italic = $false; Align = $wdAlignCenter; Before = 0; After = 12 },
        @{ Name = "Tishte Heading"; Size = 14; Bold = $true; Italic = $false; Align = $wdAlignLeft; Before = 12; After = 6 },
        @{ Name = "Tishte Italic"; Size = 14; Bold = $false; Italic = $true; Align = $wdAlignLeft; Before = 0; After = 0 },
        @{ Name = "Tishte Bold Italic"; Size = 14; Bold = $true; Italic = $true; Align = $wdAlignLeft; Before = 0; After = 0 },
        @{ Name = "Tishte Small"; Size = 10; Bold = $false; Italic = $false; Align = $wdAlignLeft; Before = 0; After = 0 },
        @{ Name = "Tishte Table"; Size = 11; Bold = $false; Italic = $false; Align = $wdAlignLeft; Before = 0; After = 0 }
    )
    foreach ($spec in $styles) {
        $style = $Document.Styles.Add($spec.Name, $wdStyleTypeParagraph)
        Set-StyleFont $style $FontName $spec.Size $spec.Bold $spec.Italic
        $style.ParagraphFormat.Alignment = $spec.Align
        $style.ParagraphFormat.SpaceBefore = $spec.Before
        $style.ParagraphFormat.SpaceAfter = $spec.After
        $style.ParagraphFormat.LineSpacingRule = $wdLineSpaceSingle
        $style.ParagraphFormat.WidowControl = -1
    }
}

function Add-Paragraph {
    param(
        $Document,
        [string]$Text,
        [string]$StyleName = "Tishte Body",
        [int]$Alignment = -1,
        [double]$FirstLineIndent = 35.45,
        [bool]$KeepWithNext = $false
    )
    $range = $Document.Range($Document.Content.End - 1, $Document.Content.End - 1)
    $range.Style = $Document.Styles.Item($StyleName)
    if ($Alignment -ge 0) { $range.ParagraphFormat.Alignment = $Alignment }
    $range.ParagraphFormat.FirstLineIndent = $FirstLineIndent
    $range.ParagraphFormat.KeepWithNext = if ($KeepWithNext) { -1 } else { 0 }
    $range.InsertAfter($Text)
    $range.InsertParagraphAfter()
}

function Add-PageBreak {
    param($Document)
    $range = $Document.Range($Document.Content.End - 1, $Document.Content.End - 1)
    $range.InsertBreak($wdPageBreak)
}

function Set-CellText {
    param($Cell, [string]$Text, [string]$FontName, [double]$Size = 11, [bool]$Bold = $false, [int]$Alignment = 0)
    $Cell.Range.Text = $Text
    $Cell.Range.Font.Name = $FontName
    $Cell.Range.Font.NameAscii = $FontName
    $Cell.Range.Font.Size = $Size
    $Cell.Range.Font.Bold = if ($Bold) { -1 } else { 0 }
    $Cell.Range.ParagraphFormat.Alignment = $Alignment
    $Cell.Range.ParagraphFormat.SpaceAfter = 0
    $Cell.Range.ParagraphFormat.LineSpacingRule = $wdLineSpaceSingle
    $Cell.VerticalAlignment = 1
}

function Add-SignatureTable {
    param($Document, [string]$FontName, [string]$Role = "Руководитель", [string]$Name = "И.О. Фамилия")
    $range = $Document.Range($Document.Content.End - 1, $Document.Content.End - 1)
    $table = $Document.Tables.Add($range, 1, 3)
    $table.AllowAutoFit = $false
    $table.Columns.Item(1).Width = 180
    $table.Columns.Item(2).Width = 110
    $table.Columns.Item(3).Width = 177
    Set-CellText $table.Cell(1, 1) $Role $FontName 14 $false $wdAlignLeft
    Set-CellText $table.Cell(1, 2) "____________" $FontName 14 $false $wdAlignCenter
    Set-CellText $table.Cell(1, 3) $Name $FontName 14 $false $wdAlignRight
    $table.Borders.Enable = $false
    $after = $Document.Range($table.Range.End, $table.Range.End)
    $after.InsertParagraphAfter()
}

function Configure-Document {
    param($Document, [string]$FontName, [string]$Label)
    $section = $Document.Sections.Item(1)
    $section.PageSetup.PageWidth = 595.28
    $section.PageSetup.PageHeight = 841.89
    $section.PageSetup.LeftMargin = 85.04
    $section.PageSetup.RightMargin = 42.52
    $section.PageSetup.TopMargin = 56.69
    $section.PageSetup.BottomMargin = 56.69
    $section.PageSetup.HeaderDistance = 28.35
    $section.PageSetup.FooterDistance = 28.35

    Add-CorpusStyles $Document $FontName
    $Document.EmbedTrueTypeFonts = $true
    $Document.SaveSubsetFonts = $true
    $Document.DoNotEmbedSystemFonts = $false

    $header = $section.Headers.Item(1).Range
    $header.Text = "TISHTE $MilestoneLabel · КОНТРОЛЬНЫЙ ОБРАЗЕЦ · $Label"
    $header.Font.Name = $FontName
    $header.Font.NameAscii = $FontName
    $header.Font.Size = 9
    $header.Font.Color = 0x777777
    $header.ParagraphFormat.Alignment = $wdAlignCenter

    $footer = $section.Footers.Item(1).Range
    $footer.Text = "Страница "
    $footer.Font.Name = $FontName
    $footer.Font.NameAscii = $FontName
    $footer.Font.Size = 9
    $footer.ParagraphFormat.Alignment = $wdAlignCenter
    $footer.Collapse($wdCollapseEnd)
    [void]$section.Footers.Item(1).Range.Fields.Add($footer, $wdFieldPage)
}

function Add-TestNotice {
    param($Document)
    Add-Paragraph $Document "ТЕСТОВЫЙ ОБРАЗЕЦ — НЕ ЯВЛЯЕТСЯ ОФИЦИАЛЬНЫМ ДОКУМЕНТОМ" "Tishte Small" $wdAlignCenter 0 $true
}

function Build-Order {
    param($Document, [string]$FontName)
    Add-TestNotice $Document
    Add-Paragraph $Document "ПРАВИТЕЛЬСТВО РЕСПУБЛИКИ МАРИЙ ЭЛ" "Tishte Title" $wdAlignCenter 0 $true
    Add-Paragraph $Document "РАСПОРЯЖЕНИЕ" "Tishte Title" $wdAlignCenter 0 $true
    Add-Paragraph $Document "от 9 августа 2026 г. № 147-р" "Tishte Body" $wdAlignCenter 0 $true
    Add-Paragraph $Document "О проведении испытаний региональной типографической системы" "Tishte Heading" $wdAlignCenter 0 $true
    Add-Paragraph $Document "В целях проверки сохранения структуры электронных документов, переносов строк, пагинации, таблиц и служебных реквизитов при замене Times New Roman на Tishte Serif:"
    $items = @(
        "1. Утвердить контрольный набор документов для сравнительных испытаний шрифта.",
        "2. Проверить основной текст размером 14 пунктов, одностраничные документы размером 13 и 13,5 пункта, а также таблицы размером от 10 до 12 пунктов.",
        "3. Сопоставить количество страниц, строк и абзацев, положение заголовков, подписей, колонтитулов и нумерации страниц.",
        "4. Обеспечить проверку русского, луговомарийского и горномарийского языковых наборов, латиницы, цифр и специальных символов.",
        "5. Зафиксировать случаи изменения переноса строк, разрыва таблиц, появления пустых страниц или отсутствующих знаков.",
        "6. Результаты испытаний оформить машинным отчётом и визуальными контрольными листами.",
        "7. Не использовать инженерную версию шрифта для подготовки подлинных нормативных правовых актов.",
        "8. Провести лингвистическую экспертизу марийских текстов с участием специалистов по обоим литературным языкам.",
        "9. После устранения замечаний повторить испытания в Microsoft Word, Microsoft Excel и Microsoft PowerPoint.",
        "10. Контроль за исполнением настоящего тестового распоряжения оставить за руководителем проекта."
    )
    foreach ($item in $items) { Add-Paragraph $Document $item "Tishte Body" $wdAlignJustify 0 }
    Add-SignatureTable $Document $FontName "Председатель Правительства" "И.О. Фамилия"
}

function Build-Letter {
    param($Document, [string]$FontName)
    Add-TestNotice $Document
    Add-Paragraph $Document "МИНИСТЕРСТВО ЦИФРОВОГО РАЗВИТИЯ РЕСПУБЛИКИ МАРИЙ ЭЛ" "Tishte Title" $wdAlignCenter 0 $true
    Add-Paragraph $Document "Начальнику управления`rИ.О. Фамилия`r424000, г. Йошкар-Ола" "Tishte Body" $wdAlignRight 0 $false
    Add-Paragraph $Document "О направлении контрольных материалов" "Tishte Heading" $wdAlignLeft 0 $true
    $paras = @(
        "Направляем контрольные материалы для оценки метрической совместимости шрифта Tishte Serif с Times New Roman в документах органов исполнительной власти Республики Марий Эл.",
        "Просим проверить отображение реквизитов, переносы строк, положение номера и даты, подписи, таблицы, маркированные и нумерованные перечни, а также корректность русского, луговомарийского и горномарийского языковых наборов.",
        "Особое внимание следует уделить документам, созданным в разных версиях Microsoft Word, сохранённым с внедрённым шрифтом и экспортированным в формат PDF. Результаты необходимо сопоставить с эталонными файлами без ручной корректировки абзацев.",
        "При обнаружении расхождений просим указать приложение, версию операционной системы, номер страницы, абзац и характер изменения. Скриншоты следует выполнять при масштабе просмотра 100 процентов.",
        "Приложение: комплект контрольных документов на 10 файлах в электронном виде."
    )
    foreach ($p in $paras) { Add-Paragraph $Document $p }
    Add-SignatureTable $Document $FontName "Заместитель министра" "И.О. Фамилия"
    Add-Paragraph $Document "Исполнитель: И.О. Фамилия, +7 (8362) 00-00-00, test@example.ru" "Tishte Small" $wdAlignLeft 0
}

function Build-Protocol {
    param($Document, [string]$FontName)
    Add-TestNotice $Document
    Add-Paragraph $Document "ПРОТОКОЛ" "Tishte Title" $wdAlignCenter 0 $true
    Add-Paragraph $Document "рабочего совещания по испытанию Tishte Serif" "Tishte Heading" $wdAlignCenter 0 $true
    Add-Paragraph $Document "9 августа 2026 г.                                               № 5" "Tishte Body" $wdAlignLeft 0
    Add-Paragraph $Document "Председательствовал: И.О. Фамилия" "Tishte Body" $wdAlignLeft 0
    Add-Paragraph $Document "Присутствовали: представители органов исполнительной власти, специалисты по делопроизводству, информационным технологиям, луговомарийскому и горномарийскому языкам." "Tishte Body" $wdAlignLeft 0
    Add-Paragraph $Document "ПОВЕСТКА ДНЯ" "Tishte Heading" $wdAlignCenter 0 $true
    Add-Paragraph $Document "1. О результатах метрической проверки Regular." "Tishte Body" $wdAlignLeft 0
    Add-Paragraph $Document "2. О языковом покрытии двух марийских литературных языков." "Tishte Body" $wdAlignLeft 0
    Add-Paragraph $Document "3. О подготовке начертаний Bold, Italic и Bold Italic." "Tishte Body" $wdAlignLeft 0
    foreach ($topic in 1..3) {
        Add-Paragraph $Document "$topic. СЛУШАЛИ" "Tishte Heading" $wdAlignLeft 0 $true
        Add-Paragraph $Document "Доклад о результатах контрольного этапа. Проверены ширины знаков, вертикальные метрики, встраивание, языковой состав и поведение текста в типовых служебных документах."
        Add-Paragraph $Document "ВЫСТУПИЛИ" "Tishte Heading" $wdAlignLeft 0 $true
        Add-Paragraph $Document "Участники отметили необходимость сохранять нейтральный деловой характер, различимость марийских диакритических знаков и устойчивую растеризацию в размерах от 10 до 14 пунктов."
        Add-Paragraph $Document "РЕШИЛИ" "Tishte Heading" $wdAlignLeft 0 $true
        foreach ($decision in 1..4) {
            Add-Paragraph $Document "$topic.$decision. Продолжить испытания по утверждённой методике и внести результаты в сводный отчёт проекта." "Tishte Body" $wdAlignJustify 0
        }
    }
    Add-SignatureTable $Document $FontName "Председательствующий" "И.О. Фамилия"
    Add-SignatureTable $Document $FontName "Секретарь" "И.О. Фамилия"
}

function Build-TableDocument {
    param($Document, [string]$FontName)
    Add-TestNotice $Document
    Add-Paragraph $Document "СРАВНИТЕЛЬНАЯ ТАБЛИЦА ИСПЫТАНИЙ" "Tishte Title" $wdAlignCenter 0 $true
    Add-Paragraph $Document "Таблица проверяет переносы в ячейках, числа, валюты, даты, проценты и марийские специальные буквы при допустимых размерах 10–12 пунктов."
    $range = $Document.Range($Document.Content.End - 1, $Document.Content.End - 1)
    $table = $Document.Tables.Add($range, 21, 5)
    $table.AllowAutoFit = $false
    $widths = @(38, 172, 92, 78, 87)
    for ($column = 1; $column -le 5; $column++) { $table.Columns.Item($column).Width = $widths[$column - 1] }
    $headers = @("№", "Показатель", "Значение", "Дата", "Статус")
    for ($column = 1; $column -le 5; $column++) { Set-CellText $table.Cell(1, $column) $headers[$column - 1] $FontName 11 $true $wdAlignCenter }
    for ($row = 2; $row -le 21; $row++) {
        $size = 10 + (($row - 2) % 3)
        Set-CellText $table.Cell($row, 1) ([string]($row - 1)) $FontName $size $false $wdAlignCenter
        Set-CellText $table.Cell($row, 2) "Контроль строки Ӓ ӓ Ӧ ӧ Ӱ ӱ Ӹ ӹ Ҥ ҥ" $FontName $size $false $wdAlignLeft
        Set-CellText $table.Cell($row, 3) ("{0:N2} ₽" -f (125000 + $row * 137.45)) $FontName $size $false $wdAlignRight
        Set-CellText $table.Cell($row, 4) ("{0:00}.08.2026" -f (($row % 28) + 1)) $FontName $size $false $wdAlignCenter
        Set-CellText $table.Cell($row, 5) "проверено" $FontName $size $false $wdAlignCenter
    }
    $table.Rows.Item(1).HeadingFormat = -1
    $table.Rows.AllowBreakAcrossPages = 0
    $after = $Document.Range($table.Range.End, $table.Range.End)
    $after.InsertParagraphAfter()
    Add-Paragraph $Document "Примечание. Значения являются тестовыми и не относятся к финансовой отчётности." "Tishte Small" $wdAlignLeft 0
}

function Build-LanguageDocument {
    param($Document, [string]$FontName)
    Add-TestNotice $Document
    Add-Paragraph $Document "ЯЗЫКОВОЙ КОНТРОЛЬНЫЙ ДОКУМЕНТ" "Tishte Title" $wdAlignCenter 0 $true
    Add-Paragraph $Document "РУССКИЙ ЯЗЫК" "Tishte Heading" $wdAlignLeft 0 $true
    Add-Paragraph $Document "Республика Марий Эл обеспечивает применение государственных языков в установленных законом сферах. Данный текст используется только для проверки шрифтового состава и раскладки документа."

    Add-Paragraph $Document "ЛУГОВОМАРИЙСКИЙ ЯЗЫК" "Tishte Heading" $wdAlignLeft 0 $true
    Add-Paragraph $Document "Марий Эл Республикын Кугыжаныш Погынжо" "Tishte Body" $wdAlignLeft 0
    Add-Paragraph $Document "Марий Эл Республикын Вуйлатышыже" "Tishte Body" $wdAlignLeft 0
    Add-Paragraph $Document "Марий Эл Республикын тӱвыра, печать да калык-влакын пашашт шотышто министерствыже" "Tishte Body" $wdAlignLeft 0
    Add-Paragraph $Document "Контроль букв: Ӓ ӓ, Ӧ ӧ, Ӱ ӱ, Ҥ ҥ. Йошкар-Ола, Кугыжаныш, тӱвыра, калык-влак." "Tishte Body" $wdAlignLeft 0

    Add-Paragraph $Document "ГОРНОМАРИЙСКИЙ ЯЗЫК" "Tishte Heading" $wdAlignLeft 0 $true
    Add-Paragraph $Document "Мары Эл Республикын Вуйлатышы" "Tishte Body" $wdAlignLeft 0
    Add-Paragraph $Document "Шачмы йӹлмем ылеш сӹлнӹ." "Tishte Body" $wdAlignLeft 0
    Add-Paragraph $Document "Яратыда, перегӹдӓ ӹшке туан йӹлмӹдӓм!" "Tishte Body" $wdAlignLeft 0
    Add-Paragraph $Document "Контроль букв: Ӓ ӓ, Ӧ ӧ, Ӱ ӱ, Ӹ ӹ. Кырык мары, шачмы вӓр, йӹлмӹ." "Tishte Body" $wdAlignLeft 0

    Add-Paragraph $Document "ЛАТИНИЦА, ЦИФРЫ И СПЕЦИАЛЬНЫЕ ЗНАКИ" "Tishte Heading" $wdAlignLeft 0 $true
    Add-Paragraph $Document "ABCDEFGHIJKLMNOPQRSTUVWXYZ · abcdefghijklmnopqrstuvwxyz · 0123456789 · № 147 · 1${nbsp}250${nbsp}000,00 ₽ · пробел: A B · NBSP: A${nbsp}B · € £ ¥ · ± × ÷ ≠ ≤ ≥ · ← ↑ → ↓ ↔" "Tishte Body" $wdAlignLeft 0
    if ($IncludeStyleMatrix) {
        Add-Paragraph $Document "КОНТРОЛЬ НАЧЕРТАНИЙ" "Tishte Heading" $wdAlignLeft 0 $true
        Add-Paragraph $Document "Regular: Республика Марий Эл · Ӓ ӓ Ӧ ӧ Ӱ ӱ Ӹ ӹ Ҥ ҥ · 0123456789" "Tishte Body" $wdAlignLeft 0
        Add-Paragraph $Document "Italic: Республика Марий Эл · Ӓ ӓ Ӧ ӧ Ӱ ӱ Ӹ ӹ Ҥ ҥ · 0123456789" "Tishte Italic" $wdAlignLeft 0
        Add-Paragraph $Document "Bold Italic: Республика Марий Эл · Ӓ ӓ Ӧ ӧ Ӱ ӱ Ӹ ӹ Ҥ ҥ · 0123456789" "Tishte Bold Italic" $wdAlignLeft 0
    }
    Add-Paragraph $Document "Примечание: марийские строки требуют окончательной лингвистической проверки специалистами по луговомарийскому и горномарийскому литературным языкам." "Tishte Small" $wdAlignLeft 0
}

$word = $null
$manifest = @()
try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
    $availableFonts = @($word.FontNames)
    if ($availableFonts -notcontains "Tishte Serif Prototype") {
        throw "Microsoft Word does not enumerate 'Tishte Serif Prototype'. Run Install-TishteTestFont.ps1 and restart Word."
    }

    $variants = @(
        @{ Id = "times"; Font = "Times New Roman"; Label = "TIMES NEW ROMAN" },
        @{ Id = "tishte"; Font = "Tishte Serif Prototype"; Label = $TishteLabel }
    )
    $kinds = @("order", "letter", "protocol", "table", "languages")
    foreach ($variant in $variants) {
        foreach ($kind in $kinds) {
            $doc = $null
            try {
                $doc = $word.Documents.Add()
                Configure-Document $doc $variant.Font $variant.Label
                switch ($kind) {
                    "order" { Build-Order $doc $variant.Font }
                    "letter" { Build-Letter $doc $variant.Font }
                    "protocol" { Build-Protocol $doc $variant.Font }
                    "table" { Build-TableDocument $doc $variant.Font }
                    "languages" { Build-LanguageDocument $doc $variant.Font }
                }
                $doc.Fields.Update() | Out-Null
                $doc.Repaginate()
                $fileName = "$kind-$($variant.Id).docx"
                $path = Join-Path $docxDir $fileName
                $doc.SaveAs2($path, $wdFormatDocumentDefault)
                $manifest += [ordered]@{
                    kind = $kind
                    variant = $variant.Id
                    font = $variant.Font
                    path = $path
                    pages = $doc.ComputeStatistics(2)
                    lines = $doc.ComputeStatistics(1)
                    paragraphs = $doc.ComputeStatistics(4)
                    tables = $doc.Tables.Count
                }
            }
            finally {
                if ($doc) {
                    $doc.Close($false)
                    [void][Runtime.InteropServices.Marshal]::ReleaseComObject($doc)
                }
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

$manifestPath = Join-Path $root "build-manifest.json"
$manifest | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $manifestPath -Encoding UTF8
[ordered]@{
    root = $root
    documents = $manifest.Count
    manifest = $manifestPath
} | ConvertTo-Json
