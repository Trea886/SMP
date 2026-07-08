# Generate Chinese font bitmaps for 01Studio LCD library
# Fixed version: better character centering in bitmap

Add-Type -AssemblyName System.Drawing

$fontPaths = @(
    "C:\Windows\Fonts\NotoSansSC-VF.ttf",
    "C:\Windows\Fonts\Noto Sans SC (TrueType).otf",
    "C:\Windows\Fonts\Noto Sans SC Bold (TrueType).otf",
    "C:\Windows\Fonts\Noto Sans SC Medium (TrueType).otf",
    "C:\Windows\Fonts\HYZhongHeiTi-197.ttf"
)

$fontPath = $null
foreach ($p in $fontPaths) {
    if (Test-Path $p) {
        $fontPath = $p
        break
    }
}
if (-not $fontPath) { Write-Error "No Chinese font found!"; exit 1 }
Write-Host "Font: $fontPath"

$charsStr = "反应挑战按下钮或挥手开始选择模式上前确认手势箭头提示回答超声波靠近远离组合混连击奖励分数题转立即燃烧难度最大新纪录平均速已排名传线保存重试返回菜单结束游戏演示停止向传感器秒"
$charArray = [char[]]$charsStr
Write-Host "Total chars: $($charArray.Count)"

$sizeList = @(
    @{Dict="hanzi_16x16_dict"; Px=16},
    @{Dict="hanzi_24x24_dict"; Px=24}
)

$sb = [System.Text.StringBuilder]::new()
[void]$sb.AppendLine("'''")
[void]$sb.AppendLine("Reaction Challenge 中文字库")
[void]$sb.AppendLine("字体: Noto Sans SC / 阴码逐行式顺向高位在前")
[void]$sb.AppendLine("'''")
[void]$sb.AppendLine()

foreach ($info in $sizeList) {
    $dictName = $info.Dict
    $sizePx = $info.Px

    Write-Host "Generating size=${sizePx}x${sizePx}..."
    [void]$sb.AppendLine("'''")
    [void]$sb.AppendLine("size = $($sizeList.IndexOf($info)+1)")
    [void]$sb.AppendLine("${sizePx} x ${sizePx} 汉字字库")
    [void]$sb.AppendLine("阴码，逐行式，顺向（高位在前）")
    [void]$sb.AppendLine("'''")
    [void]$sb.AppendLine("${dictName} = {")

    foreach ($ch in $charArray) {
        $chStr = [string]$ch

        # ---- Render with larger canvas, no StringFormat centering ----
        # Use TRIPLE size canvas to avoid clipping
        $margin = [int]($sizePx * 1.5)
        $canvasSize = $sizePx + $margin * 2

        $bmp = New-Object System.Drawing.Bitmap($canvasSize, $canvasSize)
        $g = [System.Drawing.Graphics]::FromImage($bmp)
        $g.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::SingleBitPerPixelGridFit
        $g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::None
        $g.Clear([System.Drawing.Color]::Black)

        # 字号缩小到 75%，确保实际字形 ≤ 目标像素尺寸
        $fontSize = $sizePx * 0.75
        $font = New-Object System.Drawing.Font($fontPath, [float]$fontSize, [System.Drawing.FontStyle]::Regular)

        # Measure the actual character pixel bounds
        $sf = [System.Drawing.StringFormat]::GenericTypographic
        $sf.FormatFlags = [System.Drawing.StringFormatFlags]::MeasureTrailingSpaces

        # Draw at (margin, margin) to give plenty of space
        $g.DrawString($chStr, $font, [System.Drawing.Brushes]::White, [float]$margin, [float]$margin, $sf)
        $g.Flush()
        $g.Dispose()
        $font.Dispose()

        # ---- Find actual glyph bounding box ----
        $minX = $canvasSize
        $minY = $canvasSize
        $maxX = 0
        $maxY = 0

        for ($y = 0; $y -lt $canvasSize; $y++) {
            for ($x = 0; $x -lt $canvasSize; $x++) {
                $px = $bmp.GetPixel($x, $y)
                if ($px.R -gt 128) {
                    if ($x -lt $minX) { $minX = $x }
                    if ($y -lt $minY) { $minY = $y }
                    if ($x -gt $maxX) { $maxX = $x }
                    if ($y -gt $maxY) { $maxY = $y }
                }
            }
        }

        # If no pixels found (blank char), use default region
        if ($minX -gt $maxX) {
            $minX = $margin; $maxX = $margin + $sizePx - 1
            $minY = $margin; $maxY = $margin + $sizePx - 1
        }

        # Calculate center of actual glyph
        $glyphW = $maxX - $minX + 1
        $glyphH = $maxY - $minY + 1
        $glyphCX = [int](($minX + $maxX) / 2.0)
        $glyphCY = [int](($minY + $maxY) / 2.0)

        # Crop: center $sizePx × $sizePx window on glyph center
        $cropX = [math]::Max(0, $glyphCX - [int]($sizePx / 2))
        $cropY = [math]::Max(0, $glyphCY - [int]($sizePx / 2))
        if ($cropX + $sizePx -gt $canvasSize) { $cropX = $canvasSize - $sizePx }
        if ($cropY + $sizePx -gt $canvasSize) { $cropY = $canvasSize - $sizePx }

        $cropRect = New-Object System.Drawing.Rectangle($cropX, $cropY, $sizePx, $sizePx)
        $cropped = $bmp.Clone($cropRect, [System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
        $bmp.Dispose()

        # ---- Convert to bitmap bytes (阴码、逐行式、顺向、高位在前) ----
        $bytesPerRow = [math]::Ceiling($sizePx / 8)
        $totalBytes = $sizePx * $bytesPerRow
        $bitmapBytes = New-Object byte[] $totalBytes

        for ($row = 0; $row -lt $sizePx; $row++) {
            for ($byteIdx = 0; $byteIdx -lt $bytesPerRow; $byteIdx++) {
                $byteVal = [byte]0
                for ($bit = 0; $bit -lt 8; $bit++) {
                    $col = $byteIdx * 8 + $bit
                    if ($col -ge $sizePx) { break }
                    $pxColor = $cropped.GetPixel($col, $row)
                    if ($pxColor.R -gt 128) {
                        $byteVal = $byteVal -bor ([byte](1 -shl (7 - $bit)))
                    }
                }
                $bitmapBytes[$row * $bytesPerRow + $byteIdx] = $byteVal
            }
        }
        $cropped.Dispose()

        # ---- Format as Python bytes literal ----
        $hexStr = ($bitmapBytes | ForEach-Object { '\x{0:X2}' -f $_ }) -join ""
        [void]$sb.AppendLine("    '${chStr}': b'${hexStr}',")
        [void]$sb.AppendLine()

        Write-Host "  ${chStr} OK (glyph: ${glyphW}x${glyphH}, crop: ${cropX},${cropY})"
    }

    [void]$sb.AppendLine("}")
    [void]$sb.AppendLine()
}

$outPath = "D:\gitfork\code\smp\reaction_challenge\fonts.py"
[System.IO.File]::WriteAllText($outPath, $sb.ToString(), [System.Text.UTF8Encoding]::new($true))
Write-Host "`nDone! -> $outPath"
