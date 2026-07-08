"""
中文字体位图生成脚本
用法: python generate_fonts.py > fonts.py

需要安装: pip install Pillow
使用系统自带的 "Noto Sans SC" 中文字体（Windows 11 自带）。
如果找不到该字体，修改 FONT_PATH 为任意中文字体路径。

生成格式: 阴码、逐行式、顺向（高位在前），与 01Studio LCD 库兼容。
"""

from PIL import Image, ImageFont, ImageDraw
import os
import sys

# ==================== 配置 ====================

# 字体路径（按优先级尝试）
FONT_PATHS = [
    "C:/Windows/Fonts/NotoSansSC-VF.ttf",
    "C:/Windows/Fonts/Noto Sans SC (TrueType).otf",
    "C:/Windows/Fonts/Noto Sans SC Bold (TrueType).otf",
    "C:/Windows/Fonts/simsun.ttc",
    "C:/Windows/Fonts/simhei.ttf",
    "C:/Windows/Fonts/msyh.ttc",
    "/System/Library/Fonts/PingFang.ttc",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
]

# 需要的所有中文字符（从 display_demo.py 界面文本提取）
# 下面列出所有需要用到的独体中文字符
CHINESE_CHARS = """
反应挑战按下钮或挥手开始
选择模式上前确认手势箭头
提示回答超声波靠近远离组合
混连击奖励分数题转立即燃烧
难度最大新纪录平均速已排名
传线保存重试返回菜单结束游
戏演示停止向
"""

# 去掉空白
CHINESE_CHARS = CHINESE_CHARS.replace("\n", "").replace(" ", "")

# 需要生成的字体尺寸
SIZES = {
    1: 16,   # size=1 → 16x16
    2: 24,   # size=2 → 24x24
    3: 32,   # size=3 → 32x32
    4: 40,   # size=4 → 40x40
    5: 48,   # size=5 → 48x48
}


def find_font():
    """查找可用的中文字体"""
    for path in FONT_PATHS:
        if os.path.exists(path):
            return path
    # 最后尝试 PIL 默认
    return None


def char_to_bitmap(char, font_path, size):
    """
    将单个中文字符渲染为位图，
    返回 bytes（阴码、逐行式、高位在前）
    """
    font = ImageFont.truetype(font_path, size)

    # 创建足够大的画布
    img_size = size + 4
    img = Image.new("L", (img_size, img_size), 0)  # 黑色背景
    draw = ImageDraw.Draw(img)

    # 计算字符实际尺寸，居中绘制
    bbox = font.getbbox(char)
    char_w = bbox[2] - bbox[0]
    char_h = bbox[3] - bbox[1]

    x = (img_size - char_w) // 2 - bbox[0]
    y = (img_size - char_h) // 2 - bbox[1]

    draw.text((x, y), char, font=font, fill=255)  # 白色文字

    # 裁剪到目标尺寸
    crop_x = (img_size - size) // 2
    crop_y = (img_size - size) // 2
    img = img.crop((crop_x, crop_y, crop_x + size, crop_y + size))

    # 转换为 阴码（白底黑字→1, 黑底白字→0）
    # 逐行式、顺向、高位在前
    pixel_data = img.load()
    result = bytearray()

    for row in range(size):
        byte = 0
        bit_pos = 7
        for col in range(size):
            # 阴码：有笔画的地方为 1
            pixel = pixel_data[col, row]
            if pixel > 128:  # 白色=有笔画
                byte |= (1 << bit_pos)
            bit_pos -= 1
            if bit_pos < 0:
                result.append(byte)
                byte = 0
                bit_pos = 7
        if bit_pos < 7:  # 行尾剩余
            result.append(byte)

    return bytes(result)


def format_hex(data):
    """将 bytes 格式化为 0xHH,0xHH,... 的 C/Python 风格"""
    return ",".join(f"0x{b:02X}" for b in data)


def main():
    font_path = find_font()
    if not font_path:
        print("# ERROR: 找不到中文字体!", file=sys.stderr)
        print("# 请修改 FONT_PATHS 列表，指向你的中文字体文件", file=sys.stderr)
        sys.exit(1)

    print(f"# 使用字体: {font_path}", file=sys.stderr)
    print(f"# 共 {len(CHINESE_CHARS)} 个独体中文字符", file=sys.stderr)

    # 输出文件头
    print("'''")
    print("Reaction Challenge 中文字库")
    print("由 generate_fonts.py 自动生成")
    print(f"字体: {font_path}")
    print("")
    print("宋体/Noto Sans SC、阴码，逐行式，顺向（高位在前）")
    print("'''")
    print()

    # 生成各尺寸的字库
    for size_key, size_px in SIZES.items():
        dict_name = f"hanzi_{size_px}x{size_px}_dict"
        print(f"'''")
        print(f"size = {size_key}")
        print(f"{size_px} x {size_px} 汉字字库")
        print(f"阴码，逐行式，顺向（高位在前）")
        print(f"'''")
        print(f"{dict_name} = {{")
        print()

        for char in CHINESE_CHARS:
            try:
                bitmap = char_to_bitmap(char, font_path, size_px)
                hex_str = format_hex(bitmap)
                # 每行最多放 16 个字节
                lines = []
                for i in range(0, len(bitmap), 16):
                    chunk = bitmap[i:i+16]
                    lines.append("        " + format_hex(chunk) + ",")
                print(f"    '{char}' : ({chr(10).join(lines)})")
                print()
                print(f"    # {char} OK ({len(bitmap)} bytes)", file=sys.stderr)
            except Exception as e:
                print(f"    # '{char}' ERROR: {e}", file=sys.stderr)

        print("}")
        print()

    print("# 生成完成!", file=sys.stderr)


if __name__ == "__main__":
    main()
