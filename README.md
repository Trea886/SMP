# ⚡ 反应挑战机 Reaction Challenge

> ESP32 桌面反应力测试装置 + 赛博朋克 Web 全球排行榜
> 超声波答题 · COMBO 连击 · MQTT 实时排名

---

## 一、项目概述

桌面上一台 ESP32 小装置，LCD 屏幕出题（靠近/远离），你用手掌距离作答。答对 COMBO 越叠越高，超时或答错游戏结束。每次分数自动上传 MQTT，Web 排行榜实时刷新，朋友之间互相 PK。

当前为 **超声波自动演示版**，程序上电自动循环运行，无需额外传感器即可体验完整游戏流程。

| | |
|:--|:--|
| 🎮 **当前模式** | 超声波模式（靠近/远离） |
| 🌐 **联网 PK** | MQTT 上传分数 → Web 全球排行榜 |
| 🤖 **传感器** | HC-SR04 超声波测距 |
| 📦 **无线便携** | WiFi 联网，锂电池供电 |
| 🎨 **赛博朋克** | Web 端 Canvas 粒子引擎 + 中英双语界面 |

---

## 二、硬件清单

| 模块 | 型号 | 用途 |
|:--|:--|:--|
| 主控 | ESP32-S3 (pyWiFi) + 2.4" LCD | 主控 + 显示 |
| 超声波 | HC-SR04 | 核心输入：靠近/远离 |
| 供电 | 锂电池 | 无线便携 |

### 接线表（当前使用）

| 模块 | 引脚 | ESP32 |
|:--|:--|:--|
| 超声波 Trig | → | GPIO 8 |
| 超声波 Echo | → | GPIO 9 |
| 超声波 VCC | → | 5V |
| 超声波 GND | → | GND |

---

## 三、游戏玩法（超声波模式）

LCD 交替显示 **CLOSE!**（手靠近 < 20cm）和 **BACK!**（手远离 > 70cm），在倒计时结束前做出正确距离动作即得分。

| 题号 | 时限 | 难度 |
|:--|:--|:--|
| 第 1-5 题 | ~5 秒 | 基础 |
| 第 6-10 题 | ~4 秒 | 加速 |
| 第 11-15 题 | ~3 秒 | 更快 |
| 第 16 题起 | ~2 秒 | 极速 |

**COMBO 连击：** 连续答对叠加 COMBO，倍率递增：
- COMBO ×1~2：+10 分
- COMBO ×3~4：+20 分
- COMBO ×5~9：+30 分
- COMBO ×10+：+50 分（COMBO ×10 封顶）

---

## 四、LCD 界面

四页面自动轮播：

| 页面 | 内容 |
|:--|:--|
| 🏠 **标题页** | "REACTION CHALLENGE" + 闪电闪烁动画 + MQTT 状态 |
| 📋 **菜单页** | "ULTRASONIC" 模式介绍 |
| 🎮 **游戏中** | SCORE + 题号 + 动作指令 + 倒计时进度条 + COMBO |
| 🏆 **结算页** | 游戏结束 / 分数 / COMBO / MQTT 上传状态 |

支持中文字库（`fonts.py`），16px 点阵渲染。

---

## 五、文件结构

```
reaction_challenge/
├── README.md                    # 本文档
├── display_demo.py              # ESP32 主程序 — LCD UI + 游戏逻辑 + MQTT
├── mqtt_handler.py              # WiFi / MQTT / 分数上传 / 远程指令 / 玩家名
├── sonic_sensor.py              # HC-SR04 超声波传感器驱动
├── gesture_sensor.py            # PAJ7620 手势传感器驱动（预留，未接入主程序）
├── fonts.py                     # 中文字库（16px 点阵）
├── 项目文档_原型概述与选题简介.md  # 项目设计文档
└── web/
    └── index.html               # 赛博朋克排行榜（单文件）
```

---

## 六、快速开始

### ESP32 端

将以下文件烧录到 ESP32 并运行：

```
mqtt_handler.py
sonic_sensor.py
display_demo.py
```

```python
import display_demo
display_demo.run()
```

程序会自动连接 WiFi，循环运行标题 → 菜单 → 游戏 → 结算四个页面。

---

**MQTT 依赖：** `mqtt_handler.py` 依赖 `simple` 模块（MicroPython MQTT 客户端库 `umqtt.simple`），请确保 ESP32 固件中已包含该库，或将 `simple.py` 一同烧录。

### Web 排行榜

```bash
cd reaction_challenge/web
python -m http.server 8080
# 浏览器打开 http://localhost:8080
```

或 VS Code 装 Live Server → 右键 `index.html` → Open with Live Server。

---

## 七、Web 排行榜功能

| 功能 | 说明 |
|:--|:--|
| 🏆 领奖台 | TOP 3 金银铜 + 奖牌动画 |
| 📊 实时排名 | MQTT 订阅，新分数自动上榜 |
| 🎮 远程控制 | 网页按钮切换 ESP32 游戏模式 |
| 👤 玩家名 | 网页输入 → MQTT 同步到 ESP32 |
| 🌌 Canvas 粒子 | 160 节点网络 + 350 星系尘埃 + 10 星云 + 6 星团 + 100 数据雨 |
| 🔦 手电筒 | 鼠标处增亮，周围渐暗 |
| 💥 点击特效 | 粒子炸裂 + 光环扩散 |
| 🌐 双语界面 | Orbitron 字体，中英对照 |

---

## 八、MQTT 协议

| 主题 | 方向 | 用途 |
|:--|:--|:--|
| `/reaction/score` | ESP32 → Web | 分数上报 |
| `/reaction/control` | Web → ESP32 | 远程指令 |
| `/reaction/player` | Web → ESP32 | 玩家名同步 |

**分数 JSON：**
```json
{"device":"ESP32_Reaction","score":147,"mode":"sonic","combo":8,"avg_ms":340,"questions":18}
```

---

## 九、后续扩展

以下模块驱动已就绪或规划中，可按需接入主程序：

| 模块 | 文件 | 状态 |
|:--|:--|:--|
| 手势传感器 (PAJ7620) | `gesture_sensor.py` | 驱动完成，待接入 |
| 舵机 (SG90) | — | 规划中 |
| 蜂鸣器 | — | 规划中 |
| 物理按钮 | — | 规划中 |
| 多模式切换 | — | 规划中（手势/超声波/连击三模式） |
