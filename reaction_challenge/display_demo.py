"""
Reaction Challenge - LCD UI Demo
Single file, no sensors, no dependencies
Just the board + LCD + buzzer

Copy to ESP32 as main.py, or:
    import display_demo
    display_demo.run()
"""

from tftlcd import LCD24
import time
import _thread
import fonts
import gc

# MQTT (optional - game works without it)
try:
    from mqtt_handler import upload_score, check_command
    _has_mqtt = True
    print('[OK] MQTT module loaded')
except ImportError:
    _has_mqtt = False
    check_command = None
    upload_score = None
    print('[WARN] mqtt_handler.py not found, playing offline')

# ==================== Colors ====================
BLACK   = (0, 0, 0)
WHITE   = (255, 255, 255)
RED     = (255, 0, 0)
GREEN   = (0, 255, 0)
CYAN    = (0, 255, 255)
YELLOW  = (255, 255, 0)
ORANGE  = (255, 140, 0)
DIM     = (80, 80, 80)
DARK_BG = (10, 10, 20)

lcd = LCD24(portrait=1)
lcd.fill(BLACK)

# ============ 中文字体 ============

FONT_SIZES = [0, 16, 24, 32, 40, 48]  # size=1~5 对应的像素尺寸

def printChinese(text, x, y, color=WHITE, backcolor=None, size=2):
    """在LCD上显示中文，size=1~5 对应 16~48px 字库"""
    if backcolor is None:
        backcolor = DARK_BG

    # 选择字库
    dict_map = {
        1: fonts.hanzi_16x16_dict,
        2: fonts.hanzi_24x24_dict,
        3: fonts.hanzi_32x32_dict,
        4: fonts.hanzi_40x40_dict,
        5: fonts.hanzi_48x48_dict,
    }
    chinese_dict = dict_map.get(size) if size in dict_map else dict_map[2]

    px = FONT_SIZES[size]

    # RGB888 → RGB565
    fc = ((color[0] >> 3) << 11) + ((color[1] >> 2) << 5) + (color[2] >> 3)
    bc = ((backcolor[0] >> 3) << 11) + ((backcolor[1] >> 2) << 5) + (backcolor[2] >> 3)

    xs = x
    for ch in text:
        if ch not in chinese_dict:
            # 非汉字（数字/符号），用内置字体显示
            lcd.printStr(ch, xs, y, color, size=1)
            xs += 8  # ASCII 字符宽度约 8px
            continue
        buf = chinese_dict[ch]
        rgb_buf = []

        for byte_val in buf:
            for j in range(8):
                if (byte_val << j) & 0x80 == 0x00:
                    rgb_buf.append(bc & 0xFF)
                    rgb_buf.append(bc >> 8)
                else:
                    rgb_buf.append(fc & 0xFF)
                    rgb_buf.append(fc >> 8)

        lcd.write_buf(bytearray(rgb_buf), xs, y, px, px)
        xs += px

    gc.collect()


def putCN(text, x, y, color=WHITE, backcolor=None, size=2):
    """中文显示"""
    printChinese(text, x, y, color, backcolor, size)


def putcCN(text, y, color=WHITE, backcolor=None, size=2):
    """居中中文"""
    px = FONT_SIZES[size]
    w = len(text) * px
    x = max(0, (240 - w) // 2)
    printChinese(text, x, y, color, backcolor, size)


# ============ Helpers ============

def line(x1, y1, x2, y2, color):
    try:
        lcd.drawLine(x1, y1, x2, y2, color)
    except:
        pass

def fill(x, y, w, h, color):
    try:
        lcd.drawRect(x, y, w, h, color, True)
    except:
        pass

def rect(x, y, w, h, color):
    try:
        lcd.drawRect(x, y, w, h, color, False)
    except:
        pass

def put(text, x, y, color, size=2):
    lcd.printStr(text, x, y, color, size=size)

def putc(text, y, color, size=2):
    """居中文字"""
    w = len(text) * 6 * size
    x = max(0, (240 - w) // 2)
    lcd.printStr(text, x, y, color, size=size)


# ==================== Page 1: Title ====================

def page_title(ticks, first):
    if first:
        lcd.fill(DARK_BG)
        putcCN('反应', 65, WHITE, size=2)
        putcCN('挑战', 110, CYAN, size=1)
        line(40, 155, 200, 155, DIM)
        putcCN('按下按钮或挥手', 200, WHITE, size=1)
        putcCN('开始游戏', 225, DIM, size=1)
        mqtt_ok = _has_mqtt
        put('v0.1  MQTT' + (' OK' if mqtt_ok else ' ---'), 10, 295,
            GREEN if mqtt_ok else DIM, size=1)

    # 闪电闪烁
    c = YELLOW if ticks % 5 < 3 else DARK_BG
    line(100, 20, 140, 20, c)
    line(140, 20, 120, 40, c)
    line(120, 40, 160, 40, c)
    line(160, 40, 110, 70, c)


# ==================== Page 2: Menu ====================

MODES = [
    ('手势',    '箭头提示 - 挥手回答',   YELLOW),
    ('超声波',  '手靠近或远离传感器',    GREEN),
    ('组合',    '混合提示 - 连击奖励',   ORANGE),
]
HIGHLIGHT_BOX = (0, 80, 180)  # 选中框颜色，不和文字色混用

def page_menu(selected, first):
    if first:
        lcd.fill(DARK_BG)
        putcCN('选择模式', 15, CYAN, size=1)
        line(20, 45, 220, 45, DIM)
        put('上/下: 选择', 10, 270, DIM, size=1)
        put('前:   确认', 10, 290, DIM, size=1)

    for i, (name, desc, color) in enumerate(MODES):
        y = 72 + i * 62
        sel = (i == selected)
        fill(15, y - 3, 210, 52, HIGHLIGHT_BOX if sel else DARK_BG)

        cursor = '>' if sel else ' '
        put(cursor, 25, y + 4, color, size=2)
        putCN(name, 45, y + 4, color, size=2)
        putCN(desc, 25, y + 28, WHITE if sel else DIM, size=1)

    # 滚动条
    bar_y = 72 + selected * 62
    fill(232, 68, 4, 178, DARK_BG)
    rect(232, 68, 4, 178, DIM)
    fill(232, bar_y, 4, 48, CYAN)


# ==================== Page 3: Gaming ====================

ARROWS = {'UP': '^', 'DOWN': 'v', 'LEFT': '<', 'RIGHT': '>'}
DIRS   = ['UP', 'DOWN', 'LEFT', 'RIGHT']

def page_gaming(sim, first):
    if first:
        lcd.fill(DARK_BG)
        line(5, 25, 235, 25, DIM)
        line(20, 190, 220, 190, DIM)

    q = sim['q_num']
    direction = sim['direction']
    trap = sim.get('trap', False)
    combo = sim['combo']

    # 顶栏
    fill(5, 2, 235, 22, DARK_BG)
    putCN('分数', 8, 5, WHITE, size=1)
    put(str(sim['score']), 44, 5, YELLOW, size=1)
    putCN('题', 155, 5, DIM, size=1)
    put('{}/20'.format(q), 175, 5, CYAN, size=1)

    # 箭头
    arrow = ARROWS.get(direction, '?')
    ac = RED if trap else CYAN
    fill(20, 38, 200, 82, DARK_BG)
    putc(arrow, 50, ac, size=4)
    putcCN('!!反转!!' if trap else '立即挥手', 105, RED if trap else GREEN, size=2)

    # 进度条
    remain = sim['deadline'] - time.ticks_ms()
    total  = sim['timeout']
    pct = max(0, min(1, remain / total))

    if pct > 0.5:   bc = GREEN
    elif pct > 0.25: bc = YELLOW
    else:            bc = RED

    fill(20, 140, 200, 12, DIM)
    fw = int(200 * pct)
    if fw > 0:
        fill(20, 140, fw, 12, bc)
    rect(20, 140, 200, 12, WHITE)

    fill(20, 157, 200, 22, DARK_BG)
    putc('{:.1f}s'.format(max(0, remain / 1000)), 160, bc, size=1)

    # COMBO
    fill(20, 195, 200, 58, DARK_BG)
    if combo > 0:
        cs = 3 if combo >= 5 else (2 if combo >= 3 else 1)
        cc = RED if combo >= 5 else (ORANGE if combo >= 3 else CYAN)
        putcCN('连击 x{}'.format(combo), 205, cc, size=cs)
        if combo >= 3:
            putcCN('燃烧!', 240, ORANGE, size=1)

    # 底栏
    fill(5, 278, 120, 18, DARK_BG)
    putCN('难度', 8, 280, DIM, size=1)
    put(':' + '*' * sim.get('difficulty', 1), 42, 280, DIM, size=1)

    if trap:
        fill(125, 278, 110, 18, DARK_BG)
        putCN('反向挥手!', 115, 280, RED, size=1)


# ==================== Page 4: Result ====================

def page_result(sim, first):
    if not first:
        return

    lcd.fill(DARK_BG)

    putcCN('**新纪录**' if sim.get('new_record') else '游戏结束',
           10, YELLOW if sim.get('new_record') else WHITE, size=2)

    line(30, 40, 210, 40, DIM)

    rows_cn = [
        ('分数',     '{}'.format(sim['score']),      '分', YELLOW),
        ('最大连击', 'x{}'.format(sim['max_combo']),  '',   ORANGE),
        ('已答',     '{}'.format(sim['q_num'] - 1),   '题', WHITE),
        ('平均速度', '{:.2f}'.format(sim.get('avg_reaction', 0.34)), '秒', GREEN),
    ]

    for i, (label, num_val, unit, color) in enumerate(rows_cn):
        y = 60 + i * 38
        putCN(label, 15, y, DIM, size=1)
        put(num_val, 120, y, color, size=2)
        if unit:
            putCN(unit, 120 + len(num_val) * 12, y + 2, color, size=1)

    line(30, 218, 210, 218, DIM)

    rank = sim.get('rank', 3)
    putcCN('排名: #{}'.format(rank), 235, YELLOW, size=2)

    # MQTT upload
    uploaded = False
    if _has_mqtt:
        uploaded = upload_score(
            sim['score'],
            mode='gesture',
            combo=sim.get('max_combo', 0),
            avg_ms=int(sim.get('avg_reaction', 0.34) * 1000),
            questions=sim['q_num'] - 1
        )

    if uploaded:
        putcCN('分数已上传!', 270, GREEN, size=1)
    else:
        putcCN('离线(已保存)', 270, DIM, size=1)

    putCN('挥手:重试', 5, 295, DIM, size=1)
    putCN('返回:菜单', 145, 295, DIM, size=1)


# ==================== Simulator ====================

_gaming_q_start = 0
_gaming_q_idx   = -1

def simulate(phase, ticks):
    global _gaming_q_start, _gaming_q_idx

    if phase == 'result':
        return {
            'score': 147 + (ticks // 30) * 5,
            'max_combo': 8 + (ticks // 30) % 5,
            'q_num': 18,
            'avg_reaction': 0.28 + (ticks % 3) * 0.05,
            'rank': max(1, 3 - (ticks // 30) % 3),
            'new_record': (ticks // 30) % 3 == 0,
        }

    if phase == 'gaming':
        qc = ticks // 10
        q = (qc % 15) + 1
        combo = min(12, q % 8)
        timeout = max(700, 2000 - (q // 5) * 200)

        # 新题目开始 → 记录真实时钟起始点
        if qc != _gaming_q_idx:
            _gaming_q_start = time.ticks_ms()
            _gaming_q_idx = qc

        return {
            'score': q * 10 + combo * 5,
            'q_num': q,
            'direction': DIRS[(q + qc) % 4],
            'trap': q >= 12 and (qc % 3 == 0),
            'deadline': _gaming_q_start + timeout,
            'timeout': timeout,
            'combo': combo,
            'difficulty': min(5, 1 + q // 5),
        }

    if phase == 'menu':
        return {'selected': (ticks // 20) % 3}

    return None


# ==================== MQTT Init (background) ====================

def _mqtt_init():
    """Run in a thread at boot - connect WiFi + MQTT"""
    try:
        from mqtt_handler import connect_wifi, connect_mqtt
        if connect_wifi():
            connect_mqtt()
    except:
        pass  # Offline is OK


# ==================== Main ====================

def run():
    DUR = {'title': 40, 'menu': 55, 'gaming': 100, 'result': 40}
    ORDER = ['title', 'menu', 'gaming', 'result']

    phase = ORDER[0]
    idx   = 0
    t     = 0
    first = True

    print('========================================')
    print('  反应挑战机 - LCD 界面演示')
    print('  MQTT: {}'.format('是' if _has_mqtt else '否'))
    print('========================================')

    # Start WiFi/MQTT connection in background (non-blocking)
    if _has_mqtt:
        try:
            _thread.start_new_thread(_mqtt_init, ())
        except:
            pass

    while True:
        # ---- Check for web remote commands ----
        cmd = None
        if _has_mqtt:
            try:
                raw = check_command()
                if raw:
                    # Web sends '{"cmd":"gesture"}', extract the value
                    if '"gesture"' in raw:    cmd = 'gesture'
                    elif '"sonic"' in raw:    cmd = 'sonic'
                    elif '"combo"' in raw:    cmd = 'combo'
                    elif '"back"' in raw:     cmd = 'back'
                    print('[CMD] Web remote:', cmd)
            except:
                pass

        # ---- Handle command ----
        if cmd == 'gesture':
            phase = 'gaming'
            t = 0; first = True
        elif cmd == 'sonic':
            phase = 'gaming'
            t = 0; first = True
        elif cmd == 'combo':
            phase = 'gaming'
            t = 0; first = True
        elif cmd == 'back':
            phase = 'title'
            idx = 0; t = 0; first = True

        # ---- Render current phase ----
        sim = simulate(phase, t)

        if phase == 'title':
            page_title(t, first)
        elif phase == 'menu':
            page_menu(sim['selected'] if sim else 0, first)
        elif phase == 'gaming':
            if sim:
                page_gaming(sim, first)
        elif phase == 'result':
            page_result(sim, first)

        first = False
        time.sleep_ms(100)
        t += 1

        # Auto-cycle only if no web command received
        if cmd is None and t >= DUR[phase]:
            idx = (idx + 1) % 4
            phase = ORDER[idx]
            t = 0
            first = True


if __name__ == '__main__':
    try:
        run()
    except KeyboardInterrupt:
        lcd.fill(BLACK)
        putcCN('演示已停止', 140, WHITE, size=2)
        print('演示已停止。')
