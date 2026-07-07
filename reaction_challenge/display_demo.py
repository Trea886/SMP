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
        putc('REACTION', 80, WHITE, size=3)
        putc('CHALLENGE', 120, CYAN, size=2)
        line(40, 155, 200, 155, DIM)
        putc('Press Button or Wave', 200, WHITE, size=1)
        putc('to Start', 225, DIM, size=1)
        put('v0.1  MQTT OK', 10, 295, GREEN, size=1)

    # 闪电闪烁
    c = YELLOW if ticks % 5 < 3 else DARK_BG
    line(100, 20, 140, 20, c)
    line(140, 20, 120, 40, c)
    line(120, 40, 160, 40, c)
    line(160, 40, 110, 70, c)


# ==================== Page 2: Menu ====================

MODES = [
    ('GESTURE',    'Arrow cues - wave to answer',   YELLOW),
    ('ULTRASONIC', 'Move hand near or far',          GREEN),
    ('COMBO',      'Mixed cues - chain bonus',       ORANGE),
]
HIGHLIGHT_BOX = (0, 80, 180)  # 选中框颜色，不和文字色混用

def page_menu(selected, first):
    if first:
        lcd.fill(DARK_BG)
        putc('SELECT MODE', 15, CYAN, size=2)
        line(20, 45, 220, 45, DIM)
        put('UP/DN: Select', 10, 270, DIM, size=1)
        put('FWD:   Confirm', 10, 290, DIM, size=1)

    for i, (name, desc, color) in enumerate(MODES):
        y = 72 + i * 62
        sel = (i == selected)
        fill(15, y - 3, 210, 52, HIGHLIGHT_BOX if sel else DARK_BG)

        cursor = '>' if sel else ' '
        put(cursor + name, 25, y + 4, color, size=2)
        put(desc, 25, y + 28, WHITE if sel else DIM, size=1)

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
    put('SCORE: {}'.format(sim['score']), 8, 5, WHITE, size=1)
    put('Q {}/20'.format(q), 155, 5, CYAN, size=1)

    # 箭头
    arrow = ARROWS.get(direction, '?')
    ac = RED if trap else CYAN
    fill(20, 38, 200, 82, DARK_BG)
    putc(arrow, 50, ac, size=4)
    putc('!! REVERSE !!' if trap else 'WAVE NOW', 105, RED if trap else GREEN, size=2)

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
        putc('COMBO x{}'.format(combo), 210, cc, size=cs)
        if combo >= 3:
            putc('FIRE!', 240, ORANGE, size=1)

    # 底栏
    fill(5, 278, 120, 18, DARK_BG)
    put('DIFF:' + '*' * sim.get('difficulty', 1), 8, 280, DIM, size=1)

    if trap:
        fill(125, 278, 110, 18, DARK_BG)
        put('WAVE OPPOSITE!', 110, 280, RED, size=1)


# ==================== Page 4: Result ====================

def page_result(sim, first):
    if not first:
        return  # 静态页，画一次就行

    lcd.fill(DARK_BG)

    putc('** NEW RECORD **' if sim.get('new_record') else 'GAME OVER',
         10, YELLOW if sim.get('new_record') else WHITE, size=2)

    line(30, 40, 210, 40, DIM)

    rows = [
        ('Score',      '{} pts'.format(sim['score']),                YELLOW),
        ('Max COMBO',  'x{}'.format(sim['max_combo']),               ORANGE),
        ('Answered',   '{} Q'.format(sim['q_num'] - 1),              WHITE),
        ('Avg Speed',  '{:.2f}s'.format(sim.get('avg_reaction', 0.34)), GREEN),
    ]

    for i, (label, value, color) in enumerate(rows):
        y = 60 + i * 38
        put(label, 15, y, DIM, size=1)
        put(value, 120, y, color, size=2)

    line(30, 218, 210, 218, DIM)

    rank = sim.get('rank', 3)
    putc('RANK: #{}'.format(rank), 235, YELLOW, size=2)

    putc('Score Uploaded!' if sim.get('uploaded') else 'Uploading...',
         270, GREEN if sim.get('uploaded') else DIM, size=1)

    put('Wave: Retry', 5, 298, DIM, size=1)
    put('Back: Menu',  145, 298, DIM, size=1)


# ==================== Simulator ====================

def simulate(phase, ticks):
    if phase == 'result':
        return {
            'score': 147 + (ticks // 30) * 5,
            'max_combo': 8 + (ticks // 30) % 5,
            'q_num': 18,
            'avg_reaction': 0.28 + (ticks % 3) * 0.05,
            'rank': max(1, 3 - (ticks // 30) % 3),
            'new_record': (ticks // 30) % 3 == 0,
            'uploaded': ticks > 15,
        }

    if phase == 'gaming':
        qc = ticks // 10
        q = (qc % 15) + 1
        combo = min(12, q % 8)
        timeout = max(700, 2000 - (q // 5) * 200)

        return {
            'score': q * 10 + combo * 5,
            'q_num': q,
            'direction': DIRS[(q + qc) % 4],
            'trap': q >= 12 and (qc % 3 == 0),
            'deadline': time.ticks_ms() + timeout - (ticks % 10) * 100,
            'timeout': timeout,
            'combo': combo,
            'difficulty': min(5, 1 + q // 5),
        }

    if phase == 'menu':
        return {'selected': (ticks // 20) % 3}

    return None


# ==================== Main ====================

def run():
    DUR = {'title': 40, 'menu': 55, 'gaming': 100, 'result': 40}
    ORDER = ['title', 'menu', 'gaming', 'result']

    phase = ORDER[0]
    idx   = 0
    t     = 0
    first = True

    print('========================================')
    print('  Reaction Challenge - LCD UI Demo')
    print('========================================')

    while True:
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

        if t >= DUR[phase]:
            idx = (idx + 1) % 4
            phase = ORDER[idx]
            t = 0
            first = True


if __name__ == '__main__':
    try:
        run()
    except KeyboardInterrupt:
        lcd.fill(BLACK)
        putc('Demo Stopped', 140, WHITE, size=2)
        print('Demo stopped.')
