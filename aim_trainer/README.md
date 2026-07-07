# 🎯 桌面体感射击靶 Motion Aim Trainer

> MPU6050 体感握把 + 舵机靶子 + LCD 准星 = 一台放在桌上就能练枪法的迷你射击场。
> 三种模式，宿舍 PK，FPS 手感搬到现实世界。

---

## 一、项目概述

### 这是什么

桌子上一台小型靶场装置。手持 MPU6050 陀螺仪握把当"枪"，倾斜握把控制 LCD 屏幕上的准星移动。舵机驱动的靶子随机弹起(1~3秒间隔)，瞄准扣扳机 → 红外击中 → 靶子应声倒下 + 蜂鸣器音效。三种游戏模式，比拼谁的反应最快、枪法最准。

### 实物效果预览

```
        ┌─────────────────────────┐
        │      LCD 显示屏          │
        │                         │
        │    ┌───靶子───┐         │
        │    │   🎯    │ ← 舵机   │
        │    │  (立起)  │   控制   │
        │    └─────────┘         │
        │      +  (准星)          │
        │                         │
        └─────────────────────────┘
                  ↑
         红外接收管在靶心

      ┌──────────────────┐
      │    握把 (枪)      │
      │   ┌──────────┐   │
      │   │ MPU6050  │   │  ← 检测倾斜角度
      │   │ 陀螺仪   │   │
      │   ├──────────┤   │
      │   │ 扳机按钮  │   │  ← 扣下 = 射击
      │   ├──────────┤   │
      │   │ 红外发射管 │   │  ← 枪口发出红外线
      │   └──────────┘   │
      └──────────────────┘
```

### 为什么做这个

| | |
|:--|:--|
| 🎯 **好玩上瘾** | 靶子随机弹起、击中倒下的反馈极爽，打了一局还想再来 |
| 🔫 **沉浸体验** | 体感握把瞄准 + 扣扳机 + 靶子物理倒下，不是按键游戏 |
| 🤖 **传感器融合** | MPU6050 (姿态) + 红外 (命中检测) + 舵机 + 蜂鸣器 + LCD |
| 🔧 **难度适中** | I2C 读陀螺仪 + 简单几何映射 + 状态机，大一完全能搞定 |
| 🏆 **宿舍 PK** | 三种模式 + 排行榜，朋友轮流刷分 |

---

## 二、游戏模式

### 模式 1 · 计时赛 ⏱️（主打）

```
限时 60 秒，靶子随机弹起，打中得分，统计命中数。

难度递进：
  0~20 秒  │  靶子停留 2.0 秒  │  热身
  20~40 秒 │  靶子停留 1.2 秒  │  加速
  40~60 秒 │  靶子停留 0.7 秒  │  极限冲刺

靶子倒下后随机 0.5~2.0 秒再次弹起
每次命中: +10 分
连续命中 COMBO: ×2, ×3, ×5...
```

### 模式 2 · 精度赛 🎯

```
靶子中心有"十环"区域，LCD 准星越接近靶心，分数越高。

评分规则:
  准星距靶心 < 5px   →  💥 十环!  +100 分
  准星距靶心 < 15px  →  🎯 九环   +50 分
  准星距靶心 < 30px  →  ✅ 命中   +20 分
  准星距靶心 > 30px  →  ❌ 脱靶   0 分

每轮 20 个靶子，统计总分 + 平均环数 + 爆头率
```

### 模式 3 · 移动靶 🏃

```
靶子在舵机驱动下来回摆动（不是固定位置），必须追踪瞄准。

难度设置:
  低速模式:  舵机 30°/s 摆动 (新手)
  中速模式:  舵机 60°/s 摆动 (熟练)
  高速模式:  舵机 90°/s 摆动 (地狱)

靶子持续移动 10 秒，期间可多次射击
每轮 5 个移动靶，统计命中数 + 命中率
```

---

## 三、硬件清单

| 模块 | 型号 | 数量 | 用途 |
|:--|:--|:--|:--|
| 主控 | ESP32 | 1 | 主控芯片 |
| 显示屏 | 2.4" LCD (ILI9341 / ST7789) | 1 | 显示准星 + 靶子 + 分数 |
| 陀螺仪 | MPU6050 | 1 | 检测握把倾斜角度 → 控制准星 |
| 红外发射管 | 5mm IR LED (940nm) | 1 | 装在握把枪口，扣扳机时发射 |
| 红外接收管 | VS1838B 或 5mm IR Receiver | 1 | 装在靶心，接收命中信号 |
| 舵机 | SG90 | 1 | 靶子立起/倒下/摆动 |
| 蜂鸣器 | 无源蜂鸣器 | 1 | 命中音效 + 倒计时提示 |
| 按钮 | 微动开关 | 3 | 扳机(射击) + 模式切换 + 开始 |
| 供电 | USB 5V 或锂电池 | 1 | 供电 |

### 接线表

| 模块 | ESP32 引脚 | 协议 |
|:--|:--|:--|
| MPU6050 SDA | GPIO 21 | I2C |
| MPU6050 SCL | GPIO 22 | I2C |
| 红外接收管 OUT | GPIO 34 | 数字输入 (中断) |
| 红外发射管 | GPIO 13 | 数字输出 |
| 舵机信号线 | GPIO 5 | PWM (50Hz) |
| 蜂鸣器 | GPIO 18 | PWM |
| 扳机按钮 | GPIO 25 | 数字输入 (上拉) |
| 模式按钮 | GPIO 26 | 数字输入 (上拉) |
| 开始按钮 | GPIO 27 | 数字输入 (上拉) |
| LCD | 板载 SPI | SPI |

---

## 四、程序架构

```
aim_trainer/
├── README.md            # 本文档
├── main.py              # 主循环 + 状态机
├── config.py            # 引脚、参数、阈值配置
├── mpu6050.py           # MPU6050 陀螺仪驱动 (I2C)
├── sensors.py           # 红外接收 + 按钮读取
├── games.py             # 三个游戏模式核心逻辑
├── actuator.py          # 舵机 + 蜂鸣器控制
├── display.py           # LCD 渲染 (菜单 / 准星 / 结算 / 靶子)
└── aiming.py            # 角度 → 准星坐标映射
```

---

## 五、核心原理

### 5.1 体感瞄准原理

```
MPU6050 加速度计 → 倾角 → 屏幕坐标

握把水平放置 (校准零点):
  前倾 (Pitch +)  → 准星上移  ┌────────────┐
  后仰 (Pitch -)  → 准星下移  │  LCD 屏幕   │
  左倾 (Roll  -)  → 准星左移  │            │
  右倾 (Roll  +)  → 准星右移  │    + ←准星 │
                              │            │
  倾角公式:                   └────────────┘
    pitch = atan2(ax, sqrt(ay² + az²))
    roll  = atan2(ay, sqrt(ax² + az²))

  坐标映射:
    x = screen_w/2 + roll  * K   (K = 像素/度)
    y = screen_h/2 + pitch * K

  示例: K=8 → 倾斜 10° → 准星移动 80px
```

### 5.2 红外命中检测

```
扳机按下 → 红外发射管发出 38kHz 调制信号 (100ms 脉冲)
         → 靶心红外接收管收到信号 → 输出低电平
         → ESP32 中断捕获 → 判定 HIT

时序:
  扳机  ──────┐         ┌──────
               └─────────┘
  IR发射         ┌──┐
            ─────┘  └───────  (100ms 脉冲)
  接收端          ┌──┐
            ──────┘  └──────  (延迟 < 1ms)

防作弊:
  - 两次射击间隔 ≥ 300ms (防止连发刷分)
  - 只有靶子"立起"状态才接收命中信号
```

### 5.3 舵机靶子机构

```
SG90 舵机 (0°~180°):

  靶子"立起"  →  舵机角度 = 90°
  靶子"倒下"  →  舵机角度 = 0°
  靶子"摆动"  →  舵机在 60°~120° 之间来回

  实物结构:
      ┌──────────┐
      │ 纸板靶子  │ ← 红外接收管在中心
      │   🎯     │
      └────┬─────┘
           │ 热熔胶固定
      ┌────┴────┐
      │ 舵机摇臂  │ ← SG90 塑料摇臂
      └────┬────┘
           │
      ┌────┴────┐
      │  SG90   │ ← 底座固定
      └─────────┘
```

---

## 六、主状态机

```
                         ┌─────────────┐
                         │   TITLE     │  LCD 显示 Logo + "扣扳机开始"
                         │   SCREEN    │
                         └──────┬──────┘
                                │ 扳机按下
                                ▼
                         ┌─────────────┐
                         │   MENU      │  模式按钮切换，扳机确认
                         │   SELECT    │
                         └──────┬──────┘
                                │
                  ┌─────────────┼─────────────┐
                  ▼             ▼             ▼
           ┌──────────┐  ┌──────────┐  ┌──────────┐
           │  TIMED   │  │PRECISION │  │  MOVING  │
           │  MODE    │  │  MODE    │  │  MODE    │
           └────┬─────┘  └────┬─────┘  └────┬─────┘
                │             │             │
                └─────────────┼─────────────┘
                              ▼
                       ┌─────────────┐
                       │   RESULT    │  总分 + 命中率 + 排名
                       │   SCREEN    │  扳机 → 再来一局
                       └─────────────┘  模式 → 返回菜单
```

---

## 七、反馈设计

| 事件 | 舵机动作 | 蜂鸣器音效 | LCD 特效 |
|:--|:--|:--|:--|
| 靶子弹起 | 0° → 90° (快速) | 短"嘟" | 靶子出现动画 |
| 命中靶心 | 90° → 0° (倒下) | "滴！"(800Hz) | 爆炸粒子动画 |
| 脱靶 | 不动 | — | 红色闪烁 MISS |
| 时间到 | 舵机慢速回 0° | "嘟——嘟——嘟" | GAME OVER 大字 |
| COMBO×5 | 靶子快速弹起再倒 3 次 | 上升音阶 🎵 | COMBO 火焰特效 |
| 十环命中 | 靶子倒下 + 舵机抖动 | 胜利音效 | 满屏金色 💥 |
| 新纪录 | 舵机绕圈庆祝 | 完整 victory jingle | "新纪录!!" 闪烁 |

---

## 八、LCD 界面设计

### 标题页
```
╔══════════════════════════╗
║                          ║
║        🎯  AIM LAB       ║
║    ═════════════════     ║
║     桌面体感射击靶        ║
║                          ║
║    扣扳机开始游戏         ║
║                          ║
║    ver 1.0 · ESP32       ║
╚══════════════════════════╝
```

### 菜单页
```
╔══════════════════════════╗
║   选择游戏模式             ║
║                          ║
║  ▶ 计时赛  ⏱️ 60s        ║
║    精度赛  🎯 精准       ║
║    移动靶  🏃 追踪       ║
║                          ║
║  模式键=切换  扳机=确认   ║
╚══════════════════════════╝
```

### 游戏中（计时赛）
```
╔══════════════════════════╗
║  命中: 15  剩余: 32s     ║
║                          ║
║         ┌─────┐          ║
║         │ 🎯  │ ← 靶子   ║
║         └──┬──┘          ║
║            │             ║
║         +  │  ← 准星     ║
║            │             ║
║  🔥 COMBO ×3             ║
║  ████████░░░░  66%       ║
╚══════════════════════════╝
```

### 结算页
```
╔══════════════════════════╗
║     🏆 游戏结束           ║
║                          ║
║  命中数:    18 / 25      ║
║  命中率:    72%          ║
║  最高 COMBO: ×8 🔥       ║
║  总分:      1260 分      ║
║                          ║
║  🆕 新纪录!!              ║
║                          ║
║  扳机 → 再来一局          ║
║  模式 → 返回菜单          ║
╚══════════════════════════╝
```

---

## 九、实物制作指南

### 9.1 握把 (枪)

```
材料:
  - 3D 打印外壳 或 硬纸板折叠 + 热熔胶
  - 或者直接用 PVC 管 (直径 25mm)

制作步骤:
  1. 切割/打印握把外壳 (手枪形状)
  2. MPU6050 固定在握把内部 (尽量水平)
  3. 枪口前端钻孔嵌入红外发射管
  4. 扳机位置安装微动开关
  5. 四芯排线从握把底部引出 (VCC/GND/SDA/SCL + 红外/按钮线)
```

```
     握把侧面示意图:
     
     ┌────────────────────┐
     │ 红外发射管 →  ●     │ ← 枪口
     │                    │
     │   ┌────────┐      │
     │   │MPU6050 │      │ ← 陀螺仪平放
     │   │ 芯片   │      │
     │   └────────┘      │
     │        ┌─┐        │
     │   扳机 │_│←按钮   │
     │        └─┘        │
     └──────┬┬───────────┘
            └┘← 排线引出
```

### 9.2 靶子机构

```
材料:
  - 硬纸板 / 泡沫板 (做靶面)
  - SG90 舵机 + 塑料摇臂
  - 红外接收管 (嵌在靶心)

制作步骤:
  1. 剪圆形纸板 (直径 8cm)
  2. 画同心圆 (模拟靶环，中心标红)
  3. 中心开小孔嵌入红外接收管
  4. 纸板底部用热熔胶固定在舵机摇臂上
  5. 舵机用螺丝/热熔胶固定在底座(木板/厚纸板)
```

```
     靶子正面:          靶子侧面:
    ┌──────────┐       ┌──────────┐
    │  ◉ 10 环  │       │  靶面     │
    │  ◉  9 环  │       │   │       │
    │  ◉  8 环  │       │   │ 舵机   │
    │  ◉  7 环  │       │  ┌┴┐      │
    │  ◉  6 环  │       │  │ │←摇臂 │
    └──────────┘       └──┴─┴──────┘
                           底座
```

### 9.3 整体布局

```
     俯视图 (摆在桌上):

    ┌──────────────────────────────┐
    │         LCD 显示屏           │
    │    ┌──────────────────┐      │
    │    │                  │      │
    │    │    靶子在LCD前方  │      │
    │    │   (立起时遮挡屏幕) │      │
    │    │                  │      │
    │    └──────────────────┘      │
    └──────────────────────────────┘
              ↑
        ESP32 + 面包板 (放在 LCD 背后)

    握把放在桌面上，玩家坐在 LCD 前方 30~50cm
```

---

## 十、核心代码骨架

### MPU6050 驱动关键部分

```python
from machine import Pin, I2C
import math, time

class MPU6050:
    def __init__(self, i2c, addr=0x68):
        self.i2c = i2c
        self.addr = addr
        # 唤醒 MPU6050
        self.i2c.writeto_mem(self.addr, 0x6B, b'\x00')
        self.calibrate()

    def read_raw(self):
        """读取 6 轴原始数据"""
        data = self.i2c.readfrom_mem(self.addr, 0x3B, 14)
        accel_x = (data[0] << 8 | data[1])
        accel_y = (data[2] << 8 | data[3])
        accel_z = (data[4] << 8 | data[5])
        gyro_x  = (data[8] << 8 | data[9])
        gyro_y  = (data[10] << 8 | data[11])
        return accel_x, accel_y, accel_z, gyro_x, gyro_y

    def get_angles(self):
        """互补滤波计算俯仰角和翻滚角"""
        ax, ay, az, gx, gy = self.read_raw()
        # 加速度计角度
        acc_pitch = math.atan2(ax, math.sqrt(ay**2 + az**2))
        acc_roll  = math.atan2(ay, math.sqrt(ax**2 + az**2))
        # 互补滤波 (0.98 陀螺仪 + 0.02 加速度计)
        dt = 0.01  # 10ms 循环
        self.pitch = 0.98 * (self.pitch + gx * dt) + 0.02 * acc_pitch
        self.roll  = 0.98 * (self.roll  + gy * dt) + 0.02 * acc_roll
        return math.degrees(self.pitch), math.degrees(self.roll)

    def calibrate(self):
        """零点校准: 取 100 次平均"""
        self.pitch, self.roll = 0.0, 0.0
        print("校准中...保持握把水平不动")
        for _ in range(100):
            self.get_angles()
            time.sleep_ms(10)
```

### 瞄准映射

```python
class Aiming:
    def __init__(self, screen_w=240, screen_h=320):
        self.w = screen_w
        self.h = screen_h
        self.cx = screen_w // 2   # 屏幕中心 X
        self.cy = screen_h // 2   # 屏幕中心 Y
        self.K = 8                # 像素/度 灵敏度

    def angle_to_screen(self, pitch, roll):
        """倾角 → 屏幕坐标, 加边界限制"""
        x = self.cx + roll  * self.K
        y = self.cy + pitch * self.K
        # 限制在屏幕范围内
        x = max(5, min(self.w - 5, int(x)))
        y = max(20, min(self.h - 20, int(y)))
        return x, y

    def check_hit(self, cross_x, cross_y, target_x, target_y, radius=15):
        """判断准星是否在靶子范围内"""
        dist = math.sqrt((cross_x - target_x)**2 + (cross_y - target_y)**2)
        return dist <= radius, dist  # (是否命中, 距靶心距离)
```

### 计时赛核心逻辑

```python
import random, time

class TimedGame:
    def __init__(self, duration=60):
        self.duration = duration
        self.hits = 0
        self.shots = 0
        self.combo = 0
        self.max_combo = 0
        self.score = 0
        self.target_up = False
        self.target_x = 0
        self.target_y = 0
        self.phase = 0       # 0=热身 1=加速 2=冲刺
        self.target_linger = 2000  # 靶子停留时间 (ms)

    def update_phase(self, elapsed_sec):
        """根据已过时间调整难度"""
        if elapsed_sec < 20:
            self.phase, self.target_linger = 0, 2000
        elif elapsed_sec < 40:
            self.phase, self.target_linger = 1, 1200
        else:
            self.phase, self.target_linger = 2, 700

    def pop_target(self):
        """随机位置弹出靶子"""
        margin = 40
        self.target_x = random.randint(margin, 240 - margin)
        self.target_y = random.randint(60, 280)
        self.target_up = True
        self.pop_time = time.ticks_ms()

    def on_shot(self):
        """扣扳机 → 检测命中 → 返回结果"""
        self.shots += 1
        if not self.target_up:
            return None  # 没有靶子, 空放

        if time.ticks_ms() - self.pop_time > self.target_linger:
            self.target_up = False
            return None  # 太慢, 靶子已经缩回

        return True  # 具体的命中判定在 aiming.check_hit() 中

    def on_hit(self, distance_from_center):
        """命中处理"""
        self.hits += 1
        self.combo += 1
        self.max_combo = max(self.max_combo, self.combo)
        # COMBO 倍率
        mult = min(self.combo, 5)  # 最高 ×5
        self.score += 10 * mult
        self.target_up = False

    def on_miss(self):
        """脱靶处理"""
        self.combo = 0
```

### 主状态机

```python
TITLE, MENU, GAMING, RESULT = 0, 1, 2, 3

state = TITLE
mode = 0       # 0=计时赛 1=精度赛 2=移动靶
game = None

while True:
    # 读取传感器
    pitch, roll = mpu.get_angles()
    cross_x, cross_y = aiming.angle_to_screen(pitch, roll)
    trigger = button_trigger.value() == 0    # 上拉, 按下=低电平
    mode_btn = button_mode.value() == 0

    if state == TITLE:
        display.show_title()
        if trigger:
            state = MENU
            time.sleep_ms(300)  # 防抖

    elif state == MENU:
        display.show_menu(mode)
        if mode_btn:
            mode = (mode + 1) % 3
            time.sleep_ms(200)
        if trigger:
            game = create_game(mode)
            state = GAMING
            time.sleep_ms(300)

    elif state == GAMING:
        game.tick(time.ticks_ms())
        display.show_game(game, cross_x, cross_y)
        if trigger:
            result = game.on_shot()
            if result is True:
                hit, dist = aiming.check_hit(cross_x, cross_y,
                                              game.target_x, game.target_y)
                if hit:
                    game.on_hit(dist)
                    actuator.hit_feedback(dist)  # 舵机+蜂鸣器
                else:
                    game.on_miss()
                    actuator.miss_feedback()
        if game.is_over():
            state = RESULT
            actuator.game_over_feedback()

    elif state == RESULT:
        display.show_result(game)
        if trigger:
            game = create_game(mode)  # 再来一局
            state = GAMING
        if mode_btn:
            state = MENU

    time.sleep_ms(10)  # ~100Hz 主循环
```

---

## 十一、舵机 & 蜂鸣器驱动

```python
from machine import Pin, PWM
import time

class Actuator:
    def __init__(self, servo_pin=5, buzzer_pin=18, ir_led_pin=13):
        self.servo = PWM(Pin(servo_pin), freq=50)
        self.buzzer = PWM(Pin(buzzer_pin), freq=440, duty=0)
        self.ir_led = Pin(ir_led_pin, Pin.OUT)
        self.ir_led.value(0)

    def angle(self, deg):
        """0°~180° → PWM duty"""
        duty = int(25 + deg * 115 / 180)
        self.servo.duty(duty)

    def target_up(self):
        self.angle(90)

    def target_down(self):
        self.angle(0)

    def target_swing(self, pos):
        """60°~120° 正弦摆动"""
        angle = 90 + int(30 * pos)  # pos: -1.0 ~ 1.0
        self.angle(angle)

    def fire_ir(self, duration_ms=100):
        """发射红外脉冲"""
        self.ir_led.value(1)
        time.sleep_ms(duration_ms)
        self.ir_led.value(0)

    def beep(self, freq, dur_ms):
        self.buzzer.freq(freq)
        self.buzzer.duty(512)
        time.sleep_ms(dur_ms)
        self.buzzer.duty(0)

    def hit_feedback(self, distance):
        """命中反馈: 靶子倒下 + 音效"""
        self.beep(800, 80)
        time.sleep_ms(50)
        self.target_down()
        time.sleep_ms(300)
        self.target_up()

    def miss_feedback(self):
        """脱靶: 短促低音"""
        self.beep(200, 150)

    def combo_fire_feedback(self):
        """COMBO×5: 靶子快速弹+倒 3 次 + 上升音阶"""
        for i in range(3):
            self.target_down()
            self.beep(523 + i * 200, 80)
            time.sleep_ms(100)
            self.target_up()
            time.sleep_ms(100)

    def new_record_feedback(self):
        """破纪录: 胜利旋律"""
        melody = [523, 659, 784, 1047, 784, 1047]
        for f in melody:
            self.beep(f, 120)
            time.sleep_ms(80)
        # 舵机绕圈
        for a in range(0, 180, 10):
            self.angle(a)
            time.sleep_ms(30)
```

---

## 十二、红外命中系统

```python
from machine import Pin
import time

class IRShot:
    """红外射击检测系统"""
    def __init__(self, emitter_pin=13, receiver_pin=34):
        self.emitter = Pin(emitter_pin, Pin.OUT)
        self.receiver = Pin(receiver_pin, Pin.IN, Pin.PULL_UP)

    def shoot(self):
        """发射红外信号 + 等待接收"""
        # 发射 38kHz 调制脉冲 (模拟红外遥控协议)
        self._send_pulse()
        # 检测接收端
        time.sleep_us(500)  # 等待信号到达
        return self.receiver.value() == 0  # 低电平 = 收到

    def _send_pulse(self):
        """发送 100ms 的 38kHz 载波"""
        period_us = 26  # 1/38000 ≈ 26us
        pulses = 3800   # 100ms / 26us
        for _ in range(pulses):
            self.emitter.value(1)
            time.sleep_us(13)   # 50% duty
            self.emitter.value(0)
            time.sleep_us(13)
```

> **注意**: MPU6050 的 I2C 地址 (0x68) 可能与某些 LCD 冲突，接线前先 `i2c.scan()` 确认。红外接收管如果用的是 VS1838B（一体化接收头），它自带 38kHz 解调，直接输出高低电平，连 GPIO 中断就行，代码可以简化很多。

---

## 十三、开发路线图

| 阶段 | 内容 | 预计工时 |
|:--|:--|:--|
| **Phase 1** | MPU6050 驱动 + 串口打印角度数据 | 1.5h |
| **Phase 2** | 角度 → LCD 准星映射 + 可视化调试 | 1.5h |
| **Phase 3** | 舵机靶子机构组装 + 立起/倒下控制 | 1h |
| **Phase 4** | 红外发射/接收调试 + 命中检测 | 1.5h |
| **Phase 5** | 「计时赛」核心逻辑 + LCD 界面 | 2h |
| **Phase 6** | 「精度赛」+「移动靶」模式 | 2h |
| **Phase 7** | 蜂鸣器音效 + 舵机反馈动画 | 1.5h |
| **Phase 8** | 握把外壳制作 + 整体联调 | 2h |
| **总计** | | **约 13h** |

---

## 十四、实物制作清单

| 物品 | 来源 | 用途 |
|:--|:--|:--|
| ESP32 开发板 | 已有 | 主控 |
| 2.4" LCD | 已有 | 显示 |
| MPU6050 模块 | ~8 元 | 体感瞄准 |
| SG90 舵机 | 已有 | 靶子驱动 |
| 红外发射管 (5mm) | ~1 元 | 发射命中信号 |
| 红外接收头 (VS1838B) | ~2 元 | 接收命中信号 |
| 蜂鸣器 | 已有 | 音效 |
| 微动开关 ×3 | ~3 元 | 扳机+模式+开始 |
| 硬纸板 / 瓦楞纸 | 快递盒 | 靶面 + 握把外壳 |
| 热熔胶 | 已有 | 固定结构 |
| PVC 管 (20cm) | ~3 元 | 握把枪管 |
| 杜邦线若干 | 已有 | 接线 |
| 面包板 | 已有 | 原型搭建 |

总新增成本: **约 17 元**

---

## 十五、风险 & 注意事项

| 风险点 | 应对方案 |
|:--|:--|
| MPU6050 漂移导致准星偏移 | 每次开机自动校准，游戏中定期微调零点 |
| 红外接收管受环境光干扰 | 用 38kHz 调制解调（VS1838B），滤除直流光 |
| 舵机抖动影响红外接收 | 命中检测窗口设在舵机静止时（靶子完全立起后 50ms） |
| 握把倾斜角度太灵敏/太迟钝 | `K` 值做成可调参数，在菜单加灵敏度设置 |
| 连续射击导致红外发热 | 软件限制两次射击间隔 ≥ 300ms |
| LCD 刷新导致准星拖影 | 准星用异或绘制（先擦再画），每帧只刷新变动区域 |

---

## 十六、效果视频拍摄建议

```
视频结构 (60~90秒):

0~10s   : 实物外观展示 + 握把特写 + 靶子机构
10~25s  : 计时赛一局 (展示核心玩法)
25~35s  : 精度赛演示十环命中 (展示精度判定)
35~45s  : 移动靶追踪 (展示最难模式)
45~55s  : COMBO ×10 火焰特效 + 破纪录庆祝
55~60s  : 朋友 PK 画面 + 分数对比

推荐 BGM: 轻快电子 / 8bit 游戏风
视频标题: "大一做的体感射击靶，宿舍里也能练枪法！"
```

---

> **一句话总结：握把倾斜瞄准 + 扣扳机射击 + 舵机靶子物理倒下 = 把 CS:GO 的训练场搬到了桌面上。**
>
> 难度: ⭐⭐⭐ | 趣味: ⭐⭐⭐⭐⭐ | 工期: 约 2~3 天 | 成本: ~17 元

---

## 附录: 可扩展方向

- 🏆 **WiFi 排行榜**: 加入 MQTT 上传分数，多台 ESP32 共享全球排行榜
- 🎨 **外观升级**: 3D 打印枪形外壳 + 喷漆上色
- 📱 **手机联机**: BLE 连手机 App，手机显示第三人称视角
- 💡 **激光替代红外**: 用红色激光笔（可见光）替代红外，视觉效果更好（但注意安全，功率 <5mW）
- 🔊 **语音播报**: DFPlayer Mini + 小喇叭 → "Double Kill!" "Head Shot!"
- 🔫 **双枪模式**: 两个握把 + 两个靶子 = 左右开弓