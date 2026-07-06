"""
幽灵探测器 - 主程序
烧录到板子，上电就跑
"""

import time
from machine import Timer
from ghost_detector import GhostDetector
from display import Display


# 初始化
detector = GhostDetector()
display = Display(portrait=1)

# 启动时显示标题
display.lcd.fill((0, 0, 0))
display.lcd.printStr('Ghost Detector', 10, 60, (0, 255, 255), size=2)
display.lcd.printStr('v0.1', 10, 100, (255, 255, 255), size=1)
display.lcd.printStr('Calibrating...', 10, 130, (255, 255, 0), size=1)
time.sleep(2)

# 预热：采集一次基准，避免开机就报警
detector.scan()
time.sleep(1)

print('Ghost Detector ready!')

# ==================== 主循环（定时器版）====================

def tick(timer):
    """每秒触发一次：扫描 + 刷新 LCD"""
    detector.scan()
    display.update(detector)

    # 串口打印（调试用）
    print("[{}] Temp:{:.1f}C Light:{} PIR:{} -> Lv{} | {}".format(
        detector.level * "*",
        detector.temp,
        detector.light,
        detector.pir,
        detector.level,
        detector.message
    ))


# 启动定时器，每秒跑一次
tim = Timer(1)
tim.init(period=1000, mode=Timer.PERIODIC, callback=tick)

print('Scanning... (Timer started)')
