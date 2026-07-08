# ⚡ 反应挑战机 Reaction Challenge

> ESP32 桌面反应力测试装置 + 赛博朋克 Web 全球排行榜
> 手势答题、COMBO 连击、MQTT 实时排名

---

## 当前状态

| 模块 | 状态 |
|:--|:--|
| LCD UI 演示（4 页面自动轮播） | ✅ 完成 |
| MQTT 通信（分数上传 + 远程控制 + 玩家名） | ✅ 完成 |
| Web 排行榜（赛博朋克风 + Canvas 粒子） | ✅ 完成 |
| 网页远程控制 ESP32 | ✅ 完成 |
| 网页设置玩家名 | ✅ 完成 |
| 传感器输入（手势/超声波） | ⏳ 传感器未到 |

---

## 文件结构

```
reaction_challenge/
├── README.md              # 本文档
├── display_demo.py        # ESP32 主程序 — LCD UI + MQTT 集成
├── mqtt_handler.py        # WiFi / MQTT 连接 / 分数上传 / 远程指令 / 玩家名
├── simple.py              # MQTT 客户端库（从 Study_test 复制）
└── web/
    └── index.html         # 赛博朋克排行榜（单文件，零后端）
```

---

## 硬件需求

| 模块 | 用途 |
|:--|:--|
| ESP32-S3 + 2.4" LCD | 主控 + 显示 |
| 手势识别传感器（APDS-9960 / PAJ7620） | 核心输入 |
| 超声波 HC-SR04 | 第二输入模式 |
| 舵机 SG90 | 物理反馈 |
| 蜂鸣器 | 音效 |
| 按钮 ×2 | 辅助输入 |

---

## 快速开始

### 1. ESP32 端

将以下文件烧录到 ESP32：

```
simple.py
mqtt_handler.py
display_demo.py
```

REPL 中运行：

```python
import display_demo
display_demo.run()
```

LCD 自动轮播标题 → 菜单 → 游戏 → 结算四个页面。

### 2. Web 排行榜

```bash
cd reaction_challenge/web
python -m http.server 8080
```

浏览器打开 `http://localhost:8080`。

或 VS Code 装 Live Server 插件 → 右键 `index.html` → Open with Live Server。

---

## Web 排行榜功能

| 功能 | 说明 |
|:--|:--|
| 🏆 领奖台 | TOP 3 金银铜 + 👑🥈🥉 奖牌动画 |
| 📊 实时排名 | MQTT 订阅 `/reaction/score`，自动更新 |
| 🎮 远程控制 | 点击按钮切换 ESP32 游戏模式 |
| 👤 玩家名 | 输入名字 → MQTT 同步到 ESP32 |
| 🌌 粒子背景 | Canvas 引擎：160 节点网络 + 350 星系尘埃 + 10 星云 |
| 🔦 手电筒 | 鼠标区域增亮 + 跟随网格线 |
| 🎨 标题渐变 | 鼠标在标题上滑动，区域变色 |
| 💥 点击特效 | 粒子炸裂 + 光环扩散 |
| 🌐 双语界面 | Orbitron 字体，中英对照 |

---

## MQTT 通信协议

| 主题 | 方向 | 用途 |
|:--|:--|:--|
| `/reaction/score` | ESP32 → Web | 分数 JSON 上报 |
| `/reaction/control` | Web → ESP32 | 远程指令（gesture/sonic/combo/back） |
| `/reaction/player` | Web → ESP32 | 玩家名同步 |

**分数 JSON：**
```json
{"device":"张三","score":147,"mode":"gesture","combo":8,"avg_ms":340,"questions":18}
```

---

## ESP32 端用法

### 无需传感器模式（当前）

程序自动模拟游戏数据，四页面轮播。通过网页可以：
- 设置玩家名
- 远程切换游戏模式
- 查看上传的模拟分数

### 传感器到齐后

连接手势传感器 + 超声波 + 舵机，即可进入真实游戏模式。LCD 显示中文界面（`fonts.py` 字库支持）。

---

## 开发日志

```
fix: 游戏倒计时改用真实硬件时钟
feat: 反应挑战机 + MQTT 排行榜
feat(web): 赛博朋克风排行榜 — Canvas 粒子引擎、中英双语、远程控制、奖牌系统
feat: 网页端玩家名注册 + MQTT 同步到 ESP32
```
