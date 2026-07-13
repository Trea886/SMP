"""
Reaction Challenge - LCD Auto Demo
No sensors needed - auto cycles 4 pages
"""

from tftlcd import LCD24
from machine import Pin
import time

# Ultrasonic
from sonic_sensor import HCSR04
sonic = HCSR04(Pin(8, Pin.OUT), Pin(9, Pin.IN))

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


# ===== Page 1: Title =====
def page_title(ticks, first):
    if first:
        lcd.fill(DARK_BG)
        ptc('REACTION', 80, WHITE, 3)
        ptc('CHALLENGE', 120, CYAN, 2)
        ln(40, 155, 200, 155, DIM)
        ptc('Ultrasonic Mode', 200, WHITE, 1)
        ptc('Auto Start...', 225, DIM, 1)
        mq = 'MQTT OK' if _has_mqtt else 'MQTT ---'
        pt(mq, 10, 295, GREEN if _has_mqtt else DIM, 1)
    # 闪电只在非第一帧画（避免卡顿）
    if not first:
        c = YELLOW if ticks % 6 < 3 else DARK_BG
        ln(100,20,140,20,c)
        ln(140,20,120,40,c)
        ln(120,40,160,40,c)
        ln(160,40,110,70,c)


# ===== Page 2: Menu =====
def page_menu(first):
    if first:
        lcd.fill(DARK_BG)
        ptc('SELECT MODE', 15, CYAN, 2)
        ln(20, 45, 220, 45, DIM)
        # 只显示超声波
        fl(15, 68, 210, 52, (0,80,180))
        pt('> ULTRASONIC', 25, 78, GREEN, 2)
        pt('Move hand near or far', 25, 105, WHITE, 1)
        pt('Auto starting...', 60, 200, DIM, 1)


# ===== Page 3: Gaming =====
def page_gaming(sim, first):
    lcd.fill(DARK_BG)
    ln(5, 25, 235, 25, DIM)
    ln(20, 190, 220, 190, DIM)
    q = sim['q_num']
    action = sim.get('action', 'CLOSE')
    combo = sim['combo']
    # Top
    fl(5,2,235,22,DARK_BG)
    pt('SCORE: '+str(sim['score']), 8, 5, WHITE, 1)
    pt('Q '+str(q)+'/20', 155, 5, CYAN, 1)
    # Action
    fl(20,38,200,82,DARK_BG)
    if action == 'CLOSE':
        ptc('CLOSE!', 55, GREEN, 3)
        ptc('Hand < 20cm', 95, GREEN, 1)
    else:
        ptc('BACK!', 55, CYAN, 3)
        ptc('Hand > 70cm', 95, CYAN, 1)
    # Progress bar
    remain = sim['deadline'] - time.ticks_ms()
    total = sim['timeout']
    pct = max(0, min(1, remain / total))
    bc = GREEN if pct>.5 else (YELLOW if pct>.25 else RED)
    fl(20,140,200,12,DIM)
    fw = int(200 * pct)
    if fw > 0: fl(20,140,fw,12,bc)
    fr(20,140,200,12,WHITE)
    fl(20,157,200,22,DARK_BG)
    ptc('{:.1f}s'.format(max(0,remain/1000)), 160, bc, 1)
    # COMBO
    fl(20,195,200,58,DARK_BG)
    if combo > 0:
        cs = 3 if combo>=5 else (2 if combo>=3 else 1)
        cc = RED if combo>=5 else (ORANGE if combo>=3 else CYAN)
        ptc('COMBO x'+str(combo), 210, cc, cs)
    # Bottom
    fl(5,278,120,18,DARK_BG)
    pt('DIFF:'+'*'*sim.get('difficulty',1), 8, 280, DIM, 1)


# ===== Page 4: Result =====
def page_result(sim, first):
    if not first: return
    lcd.fill(DARK_BG)
    ptc('** NEW RECORD **' if sim.get('new_record') else 'GAME OVER', 10,
        YELLOW if sim.get('new_record') else WHITE, 2)
    ln(30, 40, 210, 40, DIM)
    rows = [
        ('Score',     str(sim['score'])+' pts',  YELLOW),
        ('Max COMBO', 'x'+str(sim['max_combo']), ORANGE),
        ('Answered',  str(sim['q_num']-1)+' Q',  WHITE),
        ('Avg Speed', '{:.2f}s'.format(sim.get('avg_reaction',0.34)), GREEN),
    ]
    for i,(label,value,color) in enumerate(rows):
        y = 60 + i * 38
        pt(label, 15, y, DIM, 1)
        pt(value, 120, y, color, 2)
    ln(30, 218, 210, 218, DIM)
    rank = sim.get('rank', 3)
    ptc('RANK: #'+str(rank), 235, YELLOW, 2)
    ptc('Score Uploaded!' if sim.get('uploaded') else 'Offline', 270,
        GREEN if sim.get('uploaded') else DIM, 1)
    pt('Wave: Retry', 5, 298, DIM, 1)
    pt('Back: Menu', 145, 298, DIM, 1)


# ===== Simulator =====
_q_start = 0  # 每道题开始的真实时间
_q_idx = -1   # 当前题目序号

def simulate(phase, ticks):
    global _q_start, _q_idx
    if phase == 'menu':
        return {'selected': (ticks // 20) % 3}
    if phase == 'result':
        return {
            'score': 147 + (ticks//30)*5,
            'max_combo': 8 + (ticks//30)%5,
            'q_num': 18,
            'avg_reaction': 0.28 + (ticks%3)*.05,
            'rank': max(1, 3 - (ticks//30)%3),
            'new_record': (ticks//30)%3==0,
            'uploaded': ticks > 15,
        }
    if phase == 'gaming':
        qc = ticks // 10
        q = (qc % 15) + 1
        if qc != _q_idx:
            _q_start = time.ticks_ms()
            _q_idx = qc
        combo = min(12, q % 8)
        timeout = max(700, 2000 - (q//5)*200)
        return {
            'score': q*10 + combo*5,
            'q_num': q,
            'action': 'CLOSE' if q%2==1 else 'BACK',
            'deadline': _q_start + timeout,
            'timeout': timeout,
            'combo': combo,
            'difficulty': min(5, 1+q//5),
        }
    return None


# ===== Main =====
def run():
    state = 'title'
    t = 0; first = True; last_read = 0

    # Game vars
    score = 0; combo = 0; max_combo = 0; q_num = 1
    target = 'CLOSE'
    deadline = 0; grace_end = 0
    uploaded = False

    print('==============================')
    print('  Reaction Challenge - Sonic')
    print('==============================')

    def new_game():
        nonlocal score,combo,max_combo,q_num,target,deadline,grace_end,uploaded
        score=0;combo=0;max_combo=0;q_num=1
        target='CLOSE'  # 第一题固定靠近
        deadline=time.ticks_ms()+5000
        grace_end=time.ticks_ms()+2500
        uploaded=False

    def next_q():
        nonlocal q_num,target,deadline,grace_end
        q_num+=1
        target='BACK' if target=='CLOSE' else 'CLOSE'  # 交替
        deadline=time.ticks_ms()+max(3500,5000-q_num*150)
        grace_end=time.ticks_ms()+2000

    new_game()

    while True:
        # Only read sensor in game state
        d = -1
        if state == 'game' and time.ticks_diff(time.ticks_ms(), last_read) > 500:
            d = sonic.getDistance()
            last_read = time.ticks_ms()

        if state == 'title':
            page_title(t, first)
            first = False
            if t > 30:
                state = 'game'
                new_game()
                t = 0; first = True
        elif state == 'game':
            sim = {
                'score': score, 'q_num': q_num,
                'action': target,
                'deadline': deadline, 'timeout': 3000,
                'combo': combo, 'difficulty': min(5,1+q_num//5),
            }
            page_gaming(sim, first)
            first = False

            if d > 0:
                if time.ticks_diff(time.ticks_ms(), grace_end) < 0:
                    pass  # grace period
                else:
                    a = 'HOLD'
                    if d < 20: a = 'CLOSE'
                    elif d > 70: a = 'BACK'
                    if a == target:
                        combo += 1
                        if combo > max_combo: max_combo = combo
                        m = [1,1,2,3,5,10]
                        score += 10 * m[min(combo,5)]
                        next_q()
                        first = True
                    elif a != 'HOLD':
                        state = 'result'
                        if _has_mqtt:
                            try: upload_score(score,'sonic',max_combo,340,q_num-1); uploaded=True
                            except: pass
                        t = 0; first = True

            if time.ticks_diff(time.ticks_ms(), deadline) > 0:
                state = 'result'
                if _has_mqtt:
                    try: upload_score(score,'sonic',max_combo,340,q_num-1); uploaded=True
                    except: pass
                t = 0; first = True

        elif state == 'result':
            if first:
                lcd.fill(DARK_BG)
                ptc('GAME OVER', 20, WHITE, 3)
                ptc('游戏失败', 70, RED, 2)
                ptc('Score: '+str(score), 120, YELLOW, 2)
                ptc('Max COMBO: x'+str(max_combo), 160, ORANGE, 1)
                if uploaded:
                    ptc('Data Uploaded!', 210, GREEN, 1)
                else:
                    ptc('Offline Mode', 210, DIM, 1)
                ptc('Restart in 6s...', 260, DIM, 1)

        if state == 'result':
            if t > 40:
                state = 'title'; t = 0; first = True

        time.sleep_ms(150)
        t += 1


run()
