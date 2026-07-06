"""
幽灵探测器 - LCD 显示
三个页面：雷达扫描 / 数据读数 / 事件日志
"""

from tftlcd import LCD24
import time

# ==================== 颜色定义 ====================
BLACK  = (0, 0, 0)
WHITE  = (255, 255, 255)
RED    = (255, 0, 0)
GREEN  = (0, 255, 0)
YELLOW = (255, 255, 0)
CYAN   = (0, 255, 255)
DIM    = (60, 60, 60)       # 暗灰
ORANGE = (255, 140, 0)


class Display:
    def __init__(self, portrait=1):
        self.lcd = LCD24(portrait=portrait)
        self.lcd.fill(BLACK)

        self.page = 0            # 0=雷达 1=数据 2=日志
        self.last_switch = time.ticks_ms()

        # 雷达动画角度
        self.radar_angle = 0

    # ==================== 页面 1: 雷达扫描 ====================

    def draw_radar(self, detector):
        """雷达扫描动画页"""
        self.lcd.fill(BLACK)

        # 标题
        self.lcd.printStr('GHOST RADAR', 10, 10, CYAN, size=1)

        # 扫描线动画（简单版：用文字模拟）
        angle = self.radar_angle % 4
        scan = ['|', '/', '--', '\\'][angle]
        self.lcd.printStr('[' + scan + '] SCANNING...', 10, 40, GREEN, size=1)

        # EMF 读数（用光敏值伪装）
        emf = detector.light / 4095 * 10  # 映射到 0-10
        self.lcd.printStr('EMF: {:.2f} mG'.format(emf), 10, 70, CYAN, size=1)

        # 探测到目标？
        if detector.pir:
            self.lcd.printStr('TARGET: DETECTED !', 10, 100, RED, size=1)
        else:
            self.lcd.printStr('TARGET: NONE', 10, 100, DIM, size=1)

        # 底部状态
        if detector.level == 0:
            self.lcd.printStr('Status: CLEAR', 10, 150, GREEN, size=1)
        elif detector.level == 1:
            self.lcd.printStr('Status: UNSTABLE', 10, 150, YELLOW, size=1)
        elif detector.level >= 2:
            self.lcd.printStr('Status: WARNING !!', 10, 150, RED, size=1)

        self.radar_angle += 1

    # ==================== 页面 2: 数据读数 ====================

    def draw_data(self, detector):
        """传感器数据面板页"""
        self.lcd.fill(BLACK)

        self.lcd.printStr('=== SENSOR DATA ===', 10, 10, CYAN, size=1)

        # 温度
        color = RED if detector.level >= 2 else GREEN
        self.lcd.printStr('TEMP: {:.1f} C'.format(detector.temp), 10, 45, color, size=2)

        # EMF（光敏）
        emf = detector.light / 4095 * 10
        self.lcd.printStr('EMF : {:.2f} mG'.format(emf), 10, 80, CYAN, size=2)

        # 红外
        if detector.pir:
            self.lcd.printStr('PIR : ACTIVE !', 10, 115, RED, size=2)
        else:
            self.lcd.printStr('PIR : quiet', 10, 115, DIM, size=2)

        # 事件等级
        levels = ['CLEAR', 'SUSPECT', 'WARNING', 'ALERT !!']
        lvl_colors = [GREEN, YELLOW, ORANGE, RED]
        self.lcd.printStr(levels[detector.level], 10, 155,
                          lvl_colors[detector.level], size=2)

    # ==================== 页面 3: 事件日志 ====================

    def draw_log(self, detector):
        """事件日志页"""
        self.lcd.fill(BLACK)

        self.lcd.printStr('=== EVENT LOG ===', 10, 10, CYAN, size=1)

        lvl_mark = ['-', '?', '!!', '!!!']

        if len(detector.log) == 0:
            self.lcd.printStr('(no events yet)', 10, 40, DIM, size=1)
        else:
            for i, (ts, lvl, msg) in enumerate(detector.log[:5]):
                y = 40 + i * 30
                # 时间戳
                self.lcd.printStr(ts, 10, y, DIM, size=1)
                # 等级标记
                mark = lvl_mark[lvl]
                color = [DIM, YELLOW, ORANGE, RED][lvl]
                # 截短消息防止超出
                short_msg = msg[:22] if len(msg) > 22 else msg
                self.lcd.printStr(mark + ' ' + short_msg, 50, y, color, size=1)

    # ==================== 页面切换 ====================

    def update(self, detector):
        """主刷新：每 5 秒自动切换页面"""
        now = time.ticks_ms()
        if time.ticks_diff(now, self.last_switch) > 5000:  # 5 秒切一次
            self.page = (self.page + 1) % 3
            self.last_switch = now

        if self.page == 0:
            self.draw_radar(detector)
        elif self.page == 1:
            self.draw_data(detector)
        elif self.page == 2:
            self.draw_log(detector)
