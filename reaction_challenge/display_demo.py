"""
反应挑战机 - LCD 中文演示
需要 fonts.py 已上传到 ESP32
"""
from tftlcd import LCD24
from machine import Pin
import time
import fonts
import gc

lcd = LCD24(portrait=1)

BLACK=(0,0,0); WHITE=(255,255,255); RED=(255,0,0); GREEN=(0,255,0)
CYAN=(0,255,255); YELLOW=(255,255,0); ORANGE=(255,140,0)
DIM=(80,80,80); DARK_BG=(10,10,20)

# MQTT
try:
    from mqtt_handler import connect_wifi, connect_mqtt, upload_score
    _has_mqtt = True
except:
    _has_mqtt = False

# ===== 中文显示 =====
def pCN(text, x, y, color=WHITE, bg=DARK_BG):
    """显示中文 (16x16 字库)"""
    fc = ((color[0]>>3)<<11) | ((color[1]>>2)<<5) | (color[2]>>3)
    bc = ((bg[0]>>3)<<11) | ((bg[1]>>2)<<5) | (bg[2]>>3)
    xs = x
    for ch in text:
        if ch in fonts.hanzi_16x16_dict:
            buf = fonts.hanzi_16x16_dict[ch]
            rgb = bytearray()
            for b in buf:
                for j in range(8):
                    if (b << j) & 0x80:
                        rgb.append(fc & 0xFF); rgb.append(fc >> 8)
                    else:
                        rgb.append(bc & 0xFF); rgb.append(bc >> 8)
            lcd.write_buf(rgb, xs, y, 16, 16)
            xs += 16
        else:
            lcd.printStr(ch, xs, y+2, color, size=1)
            xs += 8
    gc.collect()

def ptcCN(text, y, color=WHITE, bg=DARK_BG):
    """居中显示中文"""
    x = max(0, (240 - len(text)*16) // 2)
    pCN(text, x, y, color, bg)

def pt(t,x,y,c,s=2): lcd.printStr(t,x,y,c,size=s)
def ptc(t,y,c,s=2):
    w=len(t)*6*s; x=max(0,(240-w)//2)
    lcd.printStr(t,x,y,c,size=s)
def ln(x1,y1,x2,y2,c):
    try: lcd.drawLine(x1,y1,x2,y2,c)
    except: pass
def fl(x,y,w,h,c):
    try: lcd.drawRect(x,y,w,h,c,True)
    except: pass
def fr(x,y,w,h,c):
    try: lcd.drawRect(x,y,w,h,c,False)
    except: pass

# ===== 页面1：标题 =====
def page_title(ticks, first):
    if first:
        lcd.fill(DARK_BG)
        ptcCN('反应挑战', 60, WHITE)
        ptcCN('手势答题器', 100, CYAN)
        ln(40, 145, 200, 145, DIM)
        ptcCN('按下按钮或挥手', 190, WHITE)
        ptcCN('开始游戏', 220, DIM)

# ===== 页面2：菜单 =====
MODES = [
    ('手势', '箭头提示-挥手回答', YELLOW),
    ('超声波', '手靠近或远离传感器', GREEN),
    ('组合', '混合提示-连击奖励', ORANGE),
]

def page_menu(selected, first):
    if first:
        lcd.fill(DARK_BG)
        ptcCN('选择模式', 15, CYAN)
        ln(20, 45, 220, 45, DIM)
        pt('UP/DN: Select', 10, 270, DIM, 1)
        pt('FWD:   Confirm', 10, 290, DIM, 1)

    for i, (name, desc, color) in enumerate(MODES):
        y = 72 + i * 62
        sel = (i == selected)
        fl(15, y-3, 210, 52, DIM if sel else DARK_BG)
        pt(('> ' if sel else '  ') + name, 25, y+4, color, 2)
        pCN(desc, 25, y+28, WHITE if sel else DIM)

    # 滚动条
    bar_y = 72 + selected * 62
    fl(232, 68, 4, 178, DARK_BG)
    fr(232, 68, 4, 178, DIM)
    fl(232, bar_y, 4, 48, CYAN)

# ===== 页面3：游戏 =====
ARROWS = {'UP':'^','DOWN':'v','LEFT':'<','RIGHT':'>'}

def page_gaming(sim, first):
    if first:
        lcd.fill(DARK_BG)
        ln(5, 25, 235, 25, DIM)
        ln(20, 190, 220, 190, DIM)

    q = sim.get('q_num', 0)
    direction = sim.get('direction', 'UP')
    trap = sim.get('trap', False)
    combo = sim.get('combo', 0)

    # 顶栏
    fl(5, 2, 235, 22, DARK_BG)
    pCN('分数', 8, 4, WHITE)
    pt(str(sim.get('score', 0)), 50, 5, YELLOW, 1)
    pCN('题', 170, 4, DIM)
    pt(str(q)+'/20', 190, 5, CYAN, 1)

    # 箭头
    arrow = ARROWS.get(direction, '?')
    ac = RED if trap else CYAN
    fl(20, 38, 200, 82, DARK_BG)
    ptc(arrow, 50, ac, 4)
    ptcCN('反转！' if trap else '立即挥手', 105, RED if trap else GREEN)

    # 进度条
    remain = sim.get('deadline', 0) - time.ticks_ms()
    total  = sim.get('timeout', 2000)
    pct = max(0, min(1, remain / total))
    bc = GREEN if pct > 0.5 else (YELLOW if pct > 0.25 else RED)
    fl(20, 140, 200, 12, DIM)
    fw = int(200 * pct)
    if fw > 0: fl(20, 140, fw, 12, bc)
    fr(20, 140, 200, 12, WHITE)
    ptc('{:.1f}s'.format(max(0, remain/1000)), 160, bc, 1)

    # 连击
    fl(20, 195, 200, 58, DARK_BG)
    if combo > 0:
        cc = RED if combo >= 5 else (ORANGE if combo >= 3 else CYAN)
        cs = 2 if combo >= 3 else 1
        ptc('COMBO x' + str(combo), 205, cc, cs)
        if combo >= 5: ptcCN('燃烧！', 240, ORANGE)

# ===== 页面4：结算 =====
def page_result(sim, first):
    if not first: return
    lcd.fill(DARK_BG)
    ptcCN('新纪录！' if sim.get('new_record') else '游戏结束', 10,
          YELLOW if sim.get('new_record') else WHITE)
    ln(30, 40, 210, 40, DIM)

    rows = [
        ('分数', str(sim.get('score', 0)), '分', YELLOW),
        ('最大连击', 'x'+str(sim.get('max_combo', 0)), '', ORANGE),
        ('已答', str(sim.get('q_num', 0)-1), '题', WHITE),
        ('平均速度', '{:.2f}'.format(sim.get('avg_reaction', 0.34)), '秒', GREEN),
    ]
    for i, (label, val, unit, color) in enumerate(rows):
        y = 60 + i * 38
        pCN(label, 15, y, DIM)
        pt(val, 120, y, color, 2)
        if unit: pt(unit, 120 + len(val)*12, y+2, color, 1)

    ln(30, 218, 210, 218, DIM)
    rank = sim.get('rank', 3)
    ptcCN('排名: #'+str(rank), 235, YELLOW)
    pCN('挥手:重试', 5, 295, DIM)
    pCN('返回:菜单', 145, 295, DIM)

# ===== 模拟数据 =====
def simulate(phase, ticks):
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
        return {
            'score': q * 10 + combo * 5,
            'q_num': q,
            'direction': ['UP', 'DOWN', 'LEFT', 'RIGHT'][(q + qc) % 4],
            'trap': q >= 12 and (qc % 3 == 0),
            'deadline': time.ticks_ms() + timeout,
            'timeout': timeout,
            'combo': combo,
            'difficulty': min(5, 1 + q // 5),
        }
    if phase == 'menu':
        return {'selected': (ticks // 20) % 3}
    return None

# ===== 主循环 =====
def run():
    DUR = {'title': 40, 'menu': 55, 'gaming': 100, 'result': 40}
    ORDER = ['title', 'menu', 'gaming', 'result']
    phase = ORDER[0]; idx = 0; t = 0; first = True
    print('=== 反应挑战机 ===')

    while True:
        sim = simulate(phase, t)
        if phase == 'title': page_title(t, first)
        elif phase == 'menu': page_menu(sim['selected'] if sim else 0, first)
        elif phase == 'gaming':
            if sim: page_gaming(sim, first)
        elif phase == 'result': page_result(sim, first)
        first = False
        time.sleep_ms(100)
        t += 1
        if t >= DUR[phase]:
            idx = (idx + 1) % 4
            phase = ORDER[idx]
            t = 0; first = True

if __name__ == '__main__':
    run()
