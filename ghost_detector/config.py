"""
幽灵探测器 - 配置文件
所有引脚、阈值、WiFi/MQTT 设置都在这里，改起来方便
"""

# ==================== 引脚定义 ====================
# 传感器
PIN_LIGHT = 10          # 光敏传感器 (ADC)
PIN_PIR = 6             # 红外人体感应 (数字输入)
PIN_BUZZER = None       # 蜂鸣器引脚（先留空，后面再加）

# LCD 引脚（板子自带，一般不用改）
LCD_PORTRAIT = 1        # 竖屏模式

# ==================== 阈值设置 ====================
# 传感器变化率阈值（超过这个值就算"异常"）
TEMP_DELTA_THRESHOLD = 0.3      # 温度变化率阈值 (°C/s)
LIGHT_DELTA_THRESHOLD = 60      # 光照波动阈值 (ADC 值)，降到60，稍微遮光就能触发
LIGHT_BASELINE = 3400           # 环境光基准值（有光状态下的读数）

# ==================== WiFi / MQTT（暂时不用）====================
WIFI_SSID = 'iPhone'
WIFI_PASS = '7878789191'
MQTT_SERVER = 'broker.emqx.io'
MQTT_PORT = 1883
CLIENT_ID = 'GhostDetector'
TOPIC = '/ghost/events'
