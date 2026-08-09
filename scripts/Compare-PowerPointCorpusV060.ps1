[CmdletBinding()]
param(
    [string]$Times = "artifacts\office-tests\v060\powerpoint\tishte-serif-v060-times.pptx",
    [string]$Tishte = "artifacts\office-tests\v060\powerpoint\tishte-serif-v060-tishte.pptx",
    [string]$Output = "artifacts\office-tests\v060\powerpoint\layout-report.json"
)

$ErrorActionPreference = "Stop"
$powerPoint = $null
$left = $null
$right = $null
try {
    $powerPoint = New-Object -ComObject PowerPoint.Application
    $powerPoint.Visible = -1
    $left = $powerPoint.Presentations.Open((Resolve-Path -LiteralPath $Times).Path, $true, $false, $false)
    $right = $powerPoint.Presentations.Open((Resolve-Path -LiteralPath $Tishte).Path, $true, $false, $false)
    $slides = @()
    $heightMismatches = @()
    $overflow = @()
    $count = [Math]::Min($left.Slides.Count, $right.Slides.Count)
    for ($slideIndex = 1; $slideIndex -le $count; $slideIndex++) {
        $leftSlide = $left.Slides.Item($slideIndex)
        $rightSlide = $right.Slides.Item($slideIndex)
        $textShapes = 0
        $shapeCount = [Math]::Min($leftSlide.Shapes.Count, $rightSlide.Shapes.Count)
        for ($shapeIndex = 1; $shapeIndex -le $shapeCount; $shapeIndex++) {
            $leftShape = $leftSlide.Shapes.Item($shapeIndex)
            $rightShape = $rightSlide.Shapes.Item($shapeIndex)
            if ($leftShape.HasTextFrame -and $leftShape.TextFrame2.HasText -and $rightShape.HasTextFrame -and $rightShape.TextFrame2.HasText) {
                $textShapes++
                $leftHeight = [Math]::Round($leftShape.TextFrame2.TextRange.BoundHeight, 2)
                $rightHeight = [Math]::Round($rightShape.TextFrame2.TextRange.BoundHeight, 2)
                if ([Math]::Abs($leftHeight - $rightHeight) -gt 0.05) {
                    $heightMismatches += [ordered]@{
                        slide = $slideIndex
                        shape = $shapeIndex
                        times_height = $leftHeight
                        tishte_height = $rightHeight
                    }
                }
                if ($leftHeight -gt $leftShape.Height -or $rightHeight -gt $rightShape.Height) {
                    $overflow += [ordered]@{ slide = $slideIndex; shape = $shapeIndex }
                }
            }
        }
        $slides += [ordered]@{
            slide = $slideIndex
            times_shapes = $leftSlide.Shapes.Count
            tishte_shapes = $rightSlide.Shapes.Count
            text_shapes_compared = $textShapes
        }
    }
    $summary = [ordered]@{
        times_slides = $left.Slides.Count
        tishte_slides = $right.Slides.Count
        slides = $slides
        text_height_mismatches = $heightMismatches
        text_overflow = $overflow
        passed = (
            $left.Slides.Count -eq $right.Slides.Count -and
            $heightMismatches.Count -eq 0 -and
            $overflow.Count -eq 0
        )
    }
    $outputPath = [System.IO.Path]::GetFullPath((Join-Path (Get-Location) $Output))
    $summary | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $outputPath -Encoding UTF8
    $summary | ConvertTo-Json -Depth 8
}
finally {
    if ($left) { $left.Close() }
    if ($right) { $right.Close() }
    if ($powerPoint) { $powerPoint.Quit() }
    if ($left) { [void][Runtime.InteropServices.Marshal]::ReleaseComObject($left) }
    if ($right) { [void][Runtime.InteropServices.Marshal]::ReleaseComObject($right) }
    if ($powerPoint) { [void][Runtime.InteropServices.Marshal]::ReleaseComObject($powerPoint) }
    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()
}
