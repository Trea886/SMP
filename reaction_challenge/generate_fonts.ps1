# Generate Chinese font bitmaps for 01Studio LCD library
# Output: fonts.py

Add-Type -AssemblyName System.Drawing

# Find a Chinese font
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

if (-not $fontPath) {
    Write-Error "No Chinese font found!"
    exit 1
}
Write-Host "Font: $fontPath"

# All unique Chinese characters needed
$charsStr = "反应挑战按下钮或挥手开始选择模式上前确认手势箭头提示回答超声波靠近远离组合混连击奖励分数题转立即燃烧难度最大新纪录平均速已排名传线保存重试返回菜单结束游戏演示停止向传感器秒"
$charArray = [char[]]$charsStr
Write-Host "Total chars: $($charArray.Count)"

# Sizes to generate
$sizeList = @(
    @{Dict="hanzi_16x16_dict"; Px=16},
    @{Dict="hanzi_24x24_dict"; Px=24},
    @{Dict="hanzi_32x32_dict"; Px=32},
    @{Dict="hanzi_40x40_dict"; Px=40},
    @{Dict="hanzi_48x48_dict"; Px=48}
)

# Build output
$sb = [System.Text.StringBuilder]::new()
[void]$sb.AppendLine("'''")
[void]$sb.AppendLine("Reaction Challenge 中文字库")
[void]$sb.AppendLine("由 generate_fonts.ps1 自动生成")
[void]$sb.AppendLine("字体: Noto Sans SC")
[void]$sb.AppendLine("阴码，逐行式，顺向（高位在前）")
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

        # --- Render character ---
        $font = New-Object System.Drawing.Font($fontPath, [float]$sizePx, [System.Drawing.FontStyle]::Regular)
        $canvasSize = [int]($sizePx * 2)
        $bmp = New-Object System.Drawing.Bitmap($canvasSize, $canvasSize)
        $g = [System.Drawing.Graphics]::FromImage($bmp)
        $g.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::SingleBitPerPixelGridFit
        $g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::None

        $sf = New-Object System.Drawing.StringFormat
        $sf.Alignment = [System.Drawing.StringAlignment]::Center
        $sf.LineAlignment = [System.Drawing.StringAlignment]::Center

        $rect = New-Object System.Drawing.RectangleF(0, 0, [float]$canvasSize, [float]$canvasSize)
        $g.Clear([System.Drawing.Color]::Black)
        $g.DrawString($chStr, $font, [System.Drawing.Brushes]::White, $rect, $sf)
        $g.Flush()
        $g.Dispose()

        # Crop center
        $off = [int]($sizePx / 2)
        $cropRect = New-Object System.Drawing.Rectangle($off, $off, $sizePx, $sizePx)
        $cropped = $bmp.Clone($cropRect, [System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
        $bmp.Dispose()
        $font.Dispose()

        # --- Convert to bitmap bytes ---
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
                    # White (R>128) = stroke = 1
                    if ($pxColor.R -gt 128) {
                        $byteVal = $byteVal -bor ([byte](1 -shl (7 - $bit)))
                    }
                }
                $bitmapBytes[$row * $bytesPerRow + $byteIdx] = $byteVal
            }
        }
        $cropped.Dispose()

        # --- Format hex ---
        [void]$sb.Append("    '${chStr}' : (")
        $first = $true
        for ($i = 0; $i -lt $bitmapBytes.Count; $i += 16) {
            $endIdx = [math]::Min($i + 15, $bitmapBytes.Count - 1)
            if ($first) {
                [void]$sb.AppendLine()
                $first = $false
            }
            $hexParts = ($bitmapBytes[$i..$endIdx] | ForEach-Object { "0x{0:X2}" -f $_ }) -join ","
            [void]$sb.AppendLine("        ${hexParts},")
        }
        [void]$sb.AppendLine("    ),")
        [void]$sb.AppendLine()

        Write-Host "  ${chStr} OK"
    }

    [void]$sb.AppendLine("}")
    [void]$sb.AppendLine()
}

# Write output file
$outPath = "D:\gitfork\code\smp\reaction_challenge\fonts.py"
$sb.ToString() | Out-File -FilePath $outPath -Encoding UTF8 -NoNewline
Write-Host "`nDone! -> $outPath"
