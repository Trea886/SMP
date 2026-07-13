"""
反应挑战机 - 中文 LCD 演示
需要 fonts.py 已上传到 ESP32
"""
from tftlcd import LCD24
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

# ===== 中文显示函数 =====
def pCN(text, x, y, color=WHITE, bg=DARK_BG, size=1):
    """显示中文 (size=1 用16x16字库)"""
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

def ptcCN(text, y, color=WHITE, bg=DARK_BG, size=1):
    """居中中文"""
    w = len(text) * 16
    x = max(0, (240 - w) // 2)
    pCN(text, x, y, color, bg, size)

def pt(t, x, y, c, s=1): lcd.printStr(t, x, y, c, size=s)
def ptc(t, y, c, s=1):
    w = len(t) * 6 * s
    x = max(0, (240 - w) // 2)
    lcd.printStr(t, x, y, c, size=s)

def ln(x1,y1,x2,y2,c):
    try: lcd.drawLine(x1,y1,x2,y2,c)
    except: pass

def fl(x,y,w,h,c):
    try: lcd.drawRect(x,y,w,h,c,True)
    except: pass

def fr(x,y,w,h,c):
    try: lcd.drawRect(x,y,w,h,c,False)
    except: pass

# ===== 四页 =====

def page_title(ticks, first):
    if first:
        lcd.fill(DARK_BG)
        ptcCN('反应', 60, WHITE, size=1)
        ptcCN('挑战', 105, CYAN, size=1)
        ln(40, 155, 200, 155, DIM)
        ptcCN('按下按钮或挥手', 200, WHITE, size=1)
        ptcCN('开始游戏', 225, DIM, size=1)
        mq = 'MQTT OK' if _has_mqtt else 'MQTT ---'
        pt(mq, 10, 295, GREEN if _has_mqtt else DIM, 1)

def page_menu(selected, first):
    MODES = [
        ('手势', '箭头提示-挥手回答', YELLOW),
        ('超声波', '手靠近或远离传感器', GREEN),
        ('组合', '混合提示-连击奖励', ORANGE),
    ]
    if first:
        lcd.fill(DARK_BG)
        ptcCN('选择模式', 15, CYAN, size=1)
        ln(20, 45, 220, 45, DIM)
        pt('UP/DN:Select', 10, 270, DIM, 1)
        pt('FWD:Confirm', 10, 290, DIM, 1)
    for i, (name, desc, color) in enumerate(MODES):
        y = 72 + i * 62
        sel = (i == selected)
        fl(15, y-3, 210, 52, DIM if sel else DARK_BG)
        cursor = '>' if sel else ' '
        pt(cursor, 25, y+4, color, 2)
        ptcCN(name, y+4, color, size=1)
        ptcCN(desc, y+28, WHITE if sel else DIM, size=1)

def page_gaming(sim, first):
    if first:
        lcd.fill(DARK_BG)
        ln(5, 25, 235, 25, DIM)
        ln(20, 190, 220, 190, DIM)
    q = sim.get('q_num', 0); score = sim.get('score', 0)
    trap = sim.get('trap', False); combo = sim.get('combo', 0)
    direction = sim.get('direction', 'UP')
    ARROWS = {'UP':'^','DOWN':'v','LEFT':'<','RIGHT':'>'}

    fl(5,2,235,22,DARK_BG)
    pCN('分数', 8, 5, WHITE, DARK_BG, 1)
    pt(str(score), 44, 5, YELLOW, 1)
    pCN('题', 155, 5, DIM, DARK_BG, 1)
    pt(str(q)+'/20', 175, 5, CYAN, 1)

    arrow = ARROWS.get(direction, '?')
    ac = RED if trap else CYAN
    fl(20,38,200,82,DARK_BG)
    ptc(arrow, 50, ac, 4)
    ptcCN('反转' if trap else '立即挥手', 105, RED if trap else GREEN, size=1)

    # 进度条
    remain = sim.get('deadline', 0) - time.ticks_ms()
    total = sim.get('timeout', 2000)
    pct = max(0, min(1, remain/total))
    bc = GREEN if pct>0.5 else (YELLOW if pct>0.25 else RED)
    fl(20,140,200,12,DIM)
    if pct>0: fl(20,140,int(200*pct),12,bc)
    fr(20,140,200,12,WHITE)
    ptc('{:.1f}s'.format(max(0,remain/1000)), 160, bc, 1)

    if combo>0:
        cc = RED if combo>=5 else (ORANGE if combo>=3 else CYAN)
        ptcCN('连击x'+str(combo), 205, cc, size=1)

def page_result(sim, first):
    if not first: return
    lcd.fill(DARK_BG)
    ptcCN('新纪录' if sim.get('new_record') else '游戏结束', 10,
          YELLOW if sim.get('new_record') else WHITE, size=1)
    ln(30, 40, 210, 40, DIM)
    rows = [
        ('分数', str(sim.get('score',0)), '分', YELLOW),
        ('最大连击', 'x'+str(sim.get('max_combo',0)), '', ORANGE),
        ('已答', str(sim.get('q_num',0)-1), '题', WHITE),
        ('平均速度', '{:.2f}'.format(sim.get('avg_reaction',0.34)), '秒', GREEN),
    ]
    for i,(label,val,unit,color) in enumerate(rows):
        y = 60 + i*38
        ptcCN(label, y, DIM, size=1)
        pt(val, 120, y, color, 2)
        if unit: ptcCN(unit, y+2, color, size=1)
    ln(30, 218, 210, 218, DIM)
    rank = sim.get('rank', 3)
    ptcCN('排名:#'+str(rank), 235, YELLOW, size=1)
    ptcCN('挥手:重试', 295, WHITE, size=1)
    ptcCN('返回:菜单', 295, DIM, size=1)

# ===== 模拟数据 =====
def simulate(phase, ticks):
    if phase=='result':
        return {'score':147+(ticks//30)*5,'max_combo':8+(ticks//30)%5,
                'q_num':18,'avg_reaction':0.28+(ticks%3)*0.05,
                'rank':max(1,3-(ticks//30)%3),'new_record':(ticks//30)%3==0}
    if phase=='gaming':
        qc=ticks//10; q=(qc%15)+1; combo=min(12,q%8)
        timeout=max(700,2000-(q//5)*200)
        return {'score':q*10+combo*5,'q_num':q,
                'direction':['UP','DOWN','LEFT','RIGHT'][(q+qc)%4],
                'trap':q>=12 and(qc%3==0),'deadline':time.ticks_ms()+timeout,
                'timeout':timeout,'combo':combo,'difficulty':min(5,1+q//5)}
    if phase=='menu': return {'selected':(ticks//20)%3}
    return None

# ===== 主循环 =====
def run():
    ORDER=['title','menu','gaming','result']
    DUR={'title':40,'menu':55,'gaming':100,'result':40}
    phase=ORDER[0]; idx=0; t=0; first=True
    print('=== 反应挑战机 ===')
    print('MQTT:'+('OK' if _has_mqtt else 'offline'))

    while True:
        sim=simulate(phase,t)
        if phase=='title': page_title(t,first)
        elif phase=='menu': page_menu(sim['selected'] if sim else 0,first)
        elif phase=='gaming':
            if sim: page_gaming(sim,first)
        elif phase=='result': page_result(sim,first)
        first=False
        time.sleep_ms(100)
        t+=1
        if t>=DUR[phase]:
            idx=(idx+1)%4; phase=ORDER[idx]; t=0; first=True

if __name__=='__main__':
    run()
