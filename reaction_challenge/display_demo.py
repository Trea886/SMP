"""
RCT Final - Gesture Only (Direction + Forward/Back)
"""

from tftlcd import LCD24
import time, random

# Gesture sensor
from gesture_sensor import init as ges_init, read_gesture

# MQTT
try:
    from mqtt_handler import connect_wifi, connect_mqtt, upload_score
    _mqtt = True
except:
    _mqtt = False

lcd = LCD24(portrait=1)
BLACK=(0,0,0); WHITE=(255,255,255); RED=(255,0,0); GREEN=(0,255,0)
CYAN=(0,255,255); YELLOW=(255,255,0); ORANGE=(255,140,0)
DIM=(80,80,80); DARK=(10,10,20)

def pt(t,x,y,c,s=2): lcd.printStr(t,x,y,c,size=s)
def ptc(t,y,c,s=2):
    w=len(t)*6*s; x=max(0,(240-w)//2); lcd.printStr(t,x,y,c,size=s)
def ln(x1,y1,x2,y2,c):
    try: lcd.drawLine(x1,y1,x2,y2,c)
    except: pass
def fl(x,y,w,h,c):
    try: lcd.drawRect(x,y,w,h,c,True)
    except: pass

# ==================== Pages ====================

def page_title(t, first):
    if first:
        lcd.fill(DARK)
        ptc('REACTION', 70, WHITE, 3)
        ptc('CHALLENGE', 110, CYAN, 2)
        ln(40, 150, 200, 150, DIM)
    c = YELLOW if t%6<3 else DARK
    ln(100,15,140,15,c); ln(140,15,120,35,c); ln(120,35,160,35,c); ln(160,35,110,65,c)

def page_game(sim, first):
    if first: lcd.fill(DARK)
    # Top bar
    fl(5,2,235,22,DARK); pt('SCORE:'+str(sim['s']),8,5,WHITE,1)
    pt('Q '+str(sim['q']),155,5,CYAN,1)
    # Question area
    qtype = sim['type']  # 'arrow' or 'dist'
    fl(20,40,200,90,DARK)
    if qtype == 'arrow':
        arrows = {'UP':'^','DOWN':'v','LEFT':'<','RIGHT':'>'}
        d = sim['dir']
        ac = RED if sim.get('trap') else CYAN
        ptc(arrows.get(d,'?'), 50, ac, 4)
        ptc('!! REVERSE !!' if sim.get('trap') else 'WAVE DIRECTION', 108,
            RED if sim.get('trap') else GREEN, 1)
    else:
        act = sim['act']
        if act == 'FORWARD':
            ptc('FORWARD!', 50, GREEN, 3)
            ptc('Move hand closer', 90, GREEN, 1)
        else:
            ptc('BACK!', 50, CYAN, 3)
            ptc('Move hand away', 90, CYAN, 1)
    # Timer bar
    rem = max(0, sim['dl']-time.ticks_ms())
    tot = sim['tot']
    pct = rem/tot if tot>0 else 0
    bc = GREEN if pct>.5 else (YELLOW if pct>.25 else RED)
    fl(20,145,200,10,DIM)
    fw=int(200*pct)
    if fw>0: fl(20,145,fw,10,bc)
    fl(20,160,200,20,DARK); ptc('{:.1f}s'.format(rem/1000),163,bc,1)
    # COMBO
    fl(20,195,200,50,DARK)
    cbo=sim['combo']
    if cbo>=5: cc,cs=RED,3
    elif cbo>=3: cc,cs=ORANGE,2
    elif cbo>0: cc,cs=CYAN,1
    else: cc,cs=DIM,1
    if cbo>0: ptc('COMBO x'+str(cbo),215,cc,cs)
    # Difficulty
    fl(5,278,130,18,DARK); pt('DIFF:'+'*'*sim['df'],8,280,DIM,1)

def page_result(score, max_combo, q_num, uploaded):
    lcd.fill(DARK)
    ptc('GAME OVER', 15, WHITE, 3)
    pt('Score: '+str(score)+' pts', 30, 65, YELLOW, 2)
    pt('Max COMBO: x'+str(max_combo), 30, 100, ORANGE, 2)
    pt('Questions: '+str(q_num-1), 30, 135, WHITE, 1)
    ptc('Uploaded!' if uploaded else 'Offline', 185, GREEN if uploaded else DIM, 1)
    ptc('STOPPED', 260, DIM, 1)

# ==================== Main ====================

def run():
    if _mqtt:
        try: connect_wifi(); connect_mqtt()
        except: pass

    ges_init()

    state = 'title'
    t = 0; first = True; last_g = ''

    score=0; combo=0; max_combo=0; q_num=1
    q_type='arrow'; cur_dir='UP'; cur_trap=False; cur_act='FORWARD'
    deadline=0; timeout=4000; grace_end=0; uploaded=False

    def new_game():
        nonlocal score,combo,max_combo,q_num,deadline,grace_end,timeout,uploaded
        nonlocal q_type,cur_dir,cur_trap,cur_act
        score=0;combo=0;max_combo=0;q_num=1;uploaded=False
        next_q()

    def next_q():
        nonlocal q_num,deadline,grace_end,timeout
        nonlocal q_type,cur_dir,cur_trap,cur_act
        q_num+=1
        # Random: 60% arrow, 40% distance
        q_type = 'arrow' if random.random()<0.6 else 'dist'
        if q_type == 'arrow':
            cur_dir=random.choice(['UP','DOWN','LEFT','RIGHT'])
            cur_trap=(q_num>=12 and random.random()<.3)
        else:
            cur_act=random.choice(['FORWARD','BACK'])
        timeout=max(2000,4000-(q_num//6)*200)
        deadline=time.ticks_ms()+timeout
        grace_end=time.ticks_ms()+1000

    new_game()

    print('========================')
    print('  RCT - Gesture Final')
    print('========================')

    while True:
        g = read_gesture()
        if g == last_g or g == 'NONE':
            g = 'NONE'
        else:
            print('[GES]', g)
            last_g = g

        # ===== Title =====
        if state == 'title':
            page_title(t, first)
            first = False
            if t > 50:
                state='game'; t=0; first=True; new_game()

        # ===== Game =====
        elif state == 'game':
            sim = {'s':score,'q':q_num,'combo':combo,'df':min(5,1+q_num//6)}
            sim['type']=q_type; sim['tot']=timeout; sim['dl']=deadline

            if q_type == 'arrow':
                sim['dir']=cur_dir; sim['trap']=cur_trap
            else:
                sim['act']=cur_act

            page_game(sim, first)
            first = False

            rem = deadline - time.ticks_ms()
            in_grace = time.ticks_diff(time.ticks_ms(), grace_end) < 0

            if not in_grace and rem > 0:
                if q_type == 'arrow':
                    if g in ('UP','DOWN','LEFT','RIGHT'):
                        correct = (g!=cur_dir) if cur_trap else (g==cur_dir)
                        if correct:
                            combo+=1
                            if combo>max_combo: max_combo=combo
                            m=[1,1,2,3,5,10]; score+=10*m[min(combo,5)]
                            next_q(); first=True
                        else:
                            state='result'; t=0; first=True
                            if _mqtt:
                                try: upload_score(score,'gesture',max_combo,340,q_num-1); uploaded=True
                                except: pass
                else:  # dist
                    if g in ('FORWARD','BACKWARD'):
                        correct = (g==cur_act)
                        if correct:
                            combo+=1
                            if combo>max_combo: max_combo=combo
                            m=[1,1,2,3,5,10]; score+=10*m[min(combo,5)]
                            next_q(); first=True
                        else:
                            state='result'; t=0; first=True
                            if _mqtt:
                                try: upload_score(score,'gesture',max_combo,340,q_num-1); uploaded=True
                                except: pass

            if rem <= 0:
                state='result'; t=0; first=True
                if _mqtt:
                    try: upload_score(score,'gesture',max_combo,340,q_num-1); uploaded=True
                    except: pass

        # ===== Result =====
        elif state == 'result':
            if first:
                page_result(score, max_combo, q_num, uploaded)
            first = False
            if t > 60:
                print('=== GAME ENDED ===')
                break  # Stop the loop, game over

        time.sleep_ms(100)
        t += 1


run()
print('Program stopped.')
