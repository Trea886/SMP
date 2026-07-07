# ⚡ 桌面反应挑战机 Reaction Challenge

> 手势 + 超声波 + 舵机 = 一台能让你和朋友 PK 反应速度的桌面装置。
> Web 全球排行榜，谁的神经反射最快？

---

## 一、项目概述

### 这是什么

桌子上一台小装置，LCD 随机出题——箭头指哪你往哪挥手。答对 COMBO 越叠越高，答错舵机倒旗 + 蜂鸣器惨叫。每次分数自动上传云端，Web 排行榜实时更新，朋友之间互相 PK。

### 为什么做这个

| | |
|:--|:--|
| 🎮 **好玩** | 三种游戏模式，COMBO 机制上头，打了一局还想再来 |
| 🌐 **联网 PK** | MQTT 上传分数 → Web 排行榜，不是单机玩具 |
| 🤖 **多传感器融合** | 手势识别 + 超声波 + 舵机 + 蜂鸣器 + LCD，全部用上 |
| 🔧 **技术适中** | 基于 ESP32 MicroPython，有挑战但不至于做不出来 |
| 📦 **便携无线** | 锂电池供电，不用插线，放哪都能玩 |

---

## 二、游戏模式

### 模式 1 · 手势闪电 ⚡（主打）

```
LCD 显示箭头方向（⬆️⬇️⬅️➡️）
你必须在倒计时内挥出正确手势

难度递进：
  第 1-5 题  │  2.0 秒  │  基础方向
  第 6-10 题 │  1.5 秒  │  加速
  第 11-15 题│  1.0 秒  │  更快
  第 16 题+  │  0.7 秒  │  红色"反方向"陷阱 30% 概率出现

错误或超时 → 游戏结束，结算分数
```

### 模式 2 · 超声波快拍 🖐️

```
LCD 变色，手脚要快：

  绿灯 🟢 → 手快速靠近（< 10cm）
  红灯 🔴 → 手快速缩回（> 30cm）
  蓝灯 🔵 → 保持不动

每轮 20 题，统计正确率 + 平均反应时间（ms）
```

### 模式 3 · 连击挑战 🔥

```
手势 + 超声波混合出题
连续答对 → COMBO 倍率飙升：

  ×1 → ×2 → ×3 → ×5 → ×10 🔥🔥🔥

答错 → COMBO 归零，分数重新累积
60 秒限时，追求最高 COMBO + 最高总分
```

---

## 三、硬件清单

| 模块 | 型号 | 数量 | 大约单价 | 用途 |
|:--|:--|:--|:--|:--|
| 主控 | ESP32-S3 (pyWiFi) | 1 | 已有 | 主控 + WiFi |
| 显示屏 | 2.4" LCD (ILI9341) | 1 | 已有 | 游戏界面 |
| 手势识别 | APDS-9960 / PAJ7620 | 1 | 已有 | 核心输入：上下左右挥手 |
| 超声波 | HC-SR04 | 1 | 已有 | 测距输入 + 第二游戏模式 |
| 舵机 | SG90 | 1 | 已有 | 物理反馈：升旗/倒旗/摆动 |
| 蜂鸣器 | 无源蜂鸣器 | 1 | 已有 | 倒计时音效 + 成功/失败提示 |
| 按钮 | 微动开关 | 2 | 已有 | 开始游戏 / 切换模式 |
| 供电 | 锂电池 | 1 | 已有 | 无线便携 |

### 接线表

| 模块 | ESP32 引脚 | 协议 |
|:--|:--|:--|
| 手势传感器 SDA | GPIO 17 | I2C |
| 手势传感器 SCL | GPIO 18 | I2C |
| 超声波 Trig | GPIO 5 | 数字输出 |
| 超声波 Echo | GPIO 6 | 数字输入 |
| 舵机信号线 | GPIO 7 | PWM |
| 蜂鸣器 | GPIO 8 | PWM |
| 按钮 1 | GPIO 9 | 数字输入 (上拉) |
| 按钮 2 | GPIO 11 | 数字输入 (上拉) |
| LCD | 板载 SPI | SPI |

---

## 四、程序架构

```
reaction_challenge/
├── README.md               # 本文档
├── main.py                 # 主循环 + 状态机
├── config.py               # 引脚、阈值、WiFi/MQTT 配置
├── sensors.py              # 手势识别 + 超声波 + 按钮驱动
├── games.py                # 三个游戏模式核心逻辑
├── actuator.py             # 舵机 + 蜂鸣器控制
├── display.py              # LCD 界面渲染 (菜单 / 游戏中 / 结算)
├── leaderboard.py          # MQTT 排行榜上传 / 拉取
└── web/
    └── index.html          # Web 排行榜页面（单文件，放 GitHub Pages）
```

---

## 五、主状态机

```
                     ┌─────────────┐
                     │   TITLE     │  LCD 显示 Logo + "挥手开始"
                     │   SCREEN    │
                     └──────┬──────┘
                            │ 手势触发 / 按钮按下
                            ▼
                     ┌─────────────┐
                     │   MENU      │  上下挥手选模式，前推确认
                     │   SELECT    │
                     └──────┬──────┘
                            │
              ┌─────────────┼─────────────┐
              ▼             ▼             ▼
       ┌──────────┐  ┌──────────┐  ┌──────────┐
       │ GESTURE  │  │ULTRASONIC│  │  COMBO   │
       │  MODE    │  │  MODE    │  │  MODE    │
       └────┬─────┘  └────┬─────┘  └────┬─────┘
            │             │             │
            └─────────────┼─────────────┘
                          ▼
                   ┌─────────────┐
                   │   RESULT    │  分数 + 排名变化 + 舵机表演
                   │   SCREEN    │
                   └──────┬──────┘
                          │
            ┌─────────────┼─────────────┐
            ▼             ▼             ▼
       再来一局      回到菜单      MQTT 上传分数
```

---

## 六、舵机 & 蜂鸣器反馈设计

| 事件 | 舵机动作 | 蜂鸣器音效 |
|:--|:--|:--|
| 答对 | 0° → 90° 升绿旗 → 回 0° | 短促 "滴" |
| 答错 | 0° → -90° 倒旗 → 回 0° | 低沉 "嘟——" |
| 超时 | 舵机快速抖两下 | "滴滴滴" |
| COMBO ×5 | 舵机来回摆动 3 次 | 上升音阶 🎵 |
| 破纪录 | 舵机 360° 绕一圈 | 胜利旋律 |
| 游戏结束 | 舵机慢速抖三下 | sad 音效下降 |

---

## 七、通信协议

### MQTT 主题设计

| 主题 | 方向 | 频率 | 内容 |
|:--|:--|:--|:--|
| `/reaction/score` | ESP32 → Broker | 每局结束 | 见下方 JSON |
| `/reaction/leaderboard` | Web 订阅 | 实时 | 由 Web 端本地聚合 |

### 分数上报 JSON

```json
{
  "device": "ESP32_01",
  "player": "Player_A",
  "score": 147,
  "mode": "gesture",
  "combo": 12,
  "avg_reaction_ms": 340,
  "questions_answered": 18,
  "timestamp": 1690000000
}
```

---

## 八、Web 排行榜页面

### 技术方案

- **单文件 HTML**，零依赖，纯 HTML + CSS + JS
- 通过 **MQTT.js** (CDN) 直连 `broker.emqx.io` 的 WebSocket 端口 (8084)
- 部署在 **GitHub Pages**，完全免费，有链接就能访问

### 页面布局

```
┌────────────────────────────────────────────┐
│          ⚡ 反应挑战 · 全球排行榜           │
│                                            │
│  [手势模式] [超声波模式] [连击模式] [全部]  │  ← Tab 切换
│                                            │
│  🥇  Player_ABC    147 分  COMBO ×12      │
│  🥈  Player_XYZ    132 分  COMBO ×8       │
│  🥉  ESP32_Desk     98 分  COMBO ×5       │
│   4  Guest_001      76 分  COMBO ×3       │
│   5  Test_Device    54 分  COMBO ×2       │
│  ...                                       │
│                                            │
│  ───────────────────────────────────────── │
│  📊 今日统计                               │
│  总对局: 47  |  最高 COMBO: ×12            │
│  最快反应: 0.18s  |  在线设备: 3           │
└────────────────────────────────────────────┘
```

---

## 九、LCD 界面设计

### 标题页
```
╔══════════════════════╗
║                      ║
║       ⚡ ⚡ ⚡        ║
║    REACTION TEST     ║
║    ═════════════     ║
║    挥手开始游戏       ║
║                      ║
║    v0.1 · MQTT OK    ║
╚══════════════════════╝
```

### 菜单页
```
╔══════════════════════╗
║  选择游戏模式         ║
║                      ║
║  ▶ 手势闪电 ⚡       ║  ← 上下挥手移动
║    超声波快拍 🖐️     ║     光标，前推确认
║    连击挑战 🔥       ║
║                      ║
║  ↘ 前推 = 确认       ║
╚══════════════════════╝
```

### 游戏中（手势模式）
```
╔══════════════════════╗
║  得分: 85   第 12 题 ║
║                      ║
║        ⬆️            ║  ← 大号箭头，明确指方向
║                      ║     红色 = 反方向陷阱
║                      ║
║  ████████░░  0.8s    ║  ← 倒计时进度条
║                      ║
║  🔥 COMBO ×3         ║
╚══════════════════════╝
```

### 结算页
```
╔══════════════════════╗
║     🎮 游戏结束       ║
║                      ║
║  得分:      147 分   ║
║  最高 COMBO: ×12 🔥  ║
║  答题数:    18 题    ║
║  平均反应:  0.34 s   ║
║                      ║
║  📡 分数已上传        ║
║                      ║
║  👋 挥手 → 再来一局   ║
║  ↩ 后退 → 返回菜单   ║
╚══════════════════════╝
```

---

## 十、核心代码骨架（关键逻辑预览）

### 手势闪电模式 - 核心循环

```python
class GestureGame:
    def __init__(self):
        self.score = 0
        self.combo = 0
        self.max_combo = 0
        self.question_num = 0
        self.timeout = 2000        # 起始 2 秒
        self.directions = ['UP', 'DOWN', 'LEFT', 'RIGHT']
        self.state = 'waiting'     # waiting | showing | judging | over

    def next_question(self):
        """生成下一题"""
        self.question_num += 1
        # 每 5 题加速 200ms，最快 700ms
        self.timeout = max(700, 2000 - (self.question_num // 5) * 200)
        # 16 题后有 30% 概率出反方向陷阱
        trap = self.question_num >= 16 and random.random() < 0.3
        self.current_dir = random.choice(self.directions)
        self.is_trap = trap
        self.deadline = time.ticks_ms() + self.timeout
        self.state = 'showing'
        return self.current_dir, trap

    def answer(self, gesture):
        """判断正误，返回 (correct, bonus, combo)"""
        now = time.ticks_ms()
        if now > self.deadline:
            self.state = 'over'
            return False, 0, self.combo

        correct = (gesture != self.current_dir) if self.is_trap \
                  else (gesture == self.current_dir)

        if correct:
            self.combo += 1
            self.max_combo = max(self.max_combo, self.combo)
            # COMBO 倍率表
            multipliers = [1, 1, 2, 3, 5, 10]
            mult = multipliers[min(self.combo, 5)]
            bonus = 10 * mult
            self.score += bonus
            return True, bonus, self.combo
        else:
            self.combo = 0
            self.state = 'over'
            return False, 0, 0
```

### 主状态机

```python
# 状态枚举
TITLE, MENU, GAMING, RESULT = 0, 1, 2, 3
state = TITLE

def tick(timer):
    global state, game

    gesture = read_gesture()        # None / 'UP' / 'DOWN' / 'LEFT' / 'RIGHT' / 'FORWARD'
    distance = read_ultrasonic()    # cm
    btn1, btn2 = read_buttons()

    if state == TITLE:
        display.show_title()
        if gesture or distance < 15 or btn1:
            state = MENU

    elif state == MENU:
        display.show_menu(cursor_pos)
        if gesture in ('UP', 'DOWN'):
            cursor_pos = (cursor_pos + dir) % 3
        elif gesture == 'FORWARD' or btn1:
            game = create_game(cursor_pos)
            state = GAMING

    elif state == GAMING:
        game.update(gesture, distance)
        display.show_gaming(game)
        if game.is_over():
            state = RESULT
            upload_score(game)       # MQTT 上传

    elif state == RESULT:
        display.show_result(game)
        if gesture == 'FORWARD':
            game = create_game(game.mode)  # 再来一局
            state = GAMING
        elif gesture == 'BACKWARD' or btn2:
            state = MENU
```

---

## 十一、舵机 & 蜂鸣器驱动预览

```python
from machine import Pin, PWM
import time

class Actuator:
    def __init__(self, servo_pin=7, buzzer_pin=8):
        self.servo = PWM(Pin(servo_pin), freq=50)  # 50Hz 标准舵机
        self.buzzer = PWM(Pin(buzzer_pin), freq=440, duty=0)

    def servo_angle(self, angle):
        """0° ~ 180° (对应 0.5ms ~ 2.5ms)"""
        duty = int(25 + angle * 115 / 180)
        self.servo.duty(duty)

    def flag_raise(self):    # 答对：升绿旗
        self.servo_angle(90)
        time.sleep_ms(300)
        self.servo_angle(0)

    def flag_fall(self):     # 答错：倒旗
        self.servo_angle(0)
        time.sleep_ms(200)
        self.servo_angle(0)

    def beep(self, freq, duration_ms):
        self.buzzer.freq(freq)
        self.buzzer.duty(512)
        time.sleep_ms(duration_ms)
        self.buzzer.duty(0)

    def victory_jingle(self):
        for f in [523, 659, 784, 1047]:
            self.beep(f, 100)

    def fail_sound(self):
        self.beep(200, 500)

    def combo_fire(self):
        for _ in range(3):
            self.servo_angle(45)
            self.beep(880, 50)
            time.sleep_ms(50)
            self.servo_angle(0)
            time.sleep_ms(50)
```

---

## 十二、开发路线图

| 阶段 | 内容 | 负责 | 预计工时 |
|:--|:--|:--|:--|
| **Phase 1** | 手势传感器驱动调试 → LCD 显示识别方向 | | 2h |
| **Phase 2** | 「手势闪电」核心逻辑 + LCD 界面 | | 3h |
| **Phase 3** | 舵机 + 蜂鸣器反馈接入 | | 2h |
| **Phase 4** | 「超声波快拍」模式 | | 2h |
| **Phase 5** | 「连击挑战」模式 | | 2h |
| **Phase 6** | MQTT 通信 + 分数上传 | | 2h |
| **Phase 7** | Web 排行榜页面 | | 3h |
| **Phase 8** | 联调 + LCD 动画打磨 | | 3h |

---

## 十三、分工建议

| 角色 | 负责模块 | 技能要求 |
|:--|:--|:--|
| **硬件 & 驱动** | `sensors.py` / `actuator.py` 接线调试 | 熟悉 MicroPython、读数据手册 |
| **游戏逻辑** | `games.py` / `main.py` 状态机 | 逻辑思维好，写核心算法 |
| **LCD 界面** | `display.py` 三个页面渲染 | 有 UI 审美，喜欢做动画 |
| **Web 前端** | `web/index.html` 排行榜 | HTML/CSS/JS，MQTT.js |
| **项目管理** | README 维护、测试、演示视频 | 啥都会一点 |

---

## 十四、风险 & 注意事项

| 风险点 | 应对方案 |
|:--|:--|
| 手势传感器不同型号 API 不一致 | 先确认型号（APDS-9960 / PAJ7620），分别写驱动适配 |
| HC-SR04 在 MicroPython 下精度不够 | 用 `time.ticks_us()` 计时，多次测量取中位数 |
| 舵机和蜂鸣器同时用 PWM 可能有冲突 | ESP32 有多个 PWM 通道，用不同通道即可 |
| MQTT 公共 Broker 可能有延迟 | 排行榜不需要实时性，秒级延迟可以接受 |
| 锂电池续航 | 不加游戏时 LCD 背光调暗，加休眠模式 |

---

## 十五、扩展想法（如果还有时间）

- 🔐 **玩家注册**：EEPROM 存玩家名，LCD 选字母输入
- 🎨 **自定义皮肤**：LCD 主题色切换（暗黑/赛博/像素风）
- 📱 **手机 App**：蓝牙 BLE 连 ESP32，手机当副屏显示分数
- 🔊 **语音播报**：加个 DFPlayer Mini 模块 → "恭喜！新纪录！"
- 🏆 **每周重置排行榜**：每周一自动归档上周数据

---

> **一句话总结：一台用"挥手"来玩的反应力测试机，连上网，全世界的 ESP32 都能 PK。**
>
> 难度：⭐⭐⭐ | 趣味：⭐⭐⭐⭐⭐ | 工期：约 5 天
