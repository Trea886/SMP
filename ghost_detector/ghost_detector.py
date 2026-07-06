"""
幽灵探测器 - 核心逻辑
变化率检测 → 事件分级 → 叙事匹配
"""

from sensors import read_all
from narrative import detect_text, calm_text
import config


class GhostDetector:
    def __init__(self):
        # 上一次的读数，用于计算变化率
        self.last_temp = None
        self.last_light = None

        # 当前状态
        self.level = 0           # 0=平静 1=疑似 2=警告 3=显灵
        self.message = ""        # 当前事件描述
        self.temp = 0            # 当前温度
        self.light = 0           # 当前光照
        self.pir = False         # 当前红外

        # 事件日志（最多存 20 条）
        self.log = []

    def scan(self):
        """扫描一次：读传感器 → 计算变化 → 分级 → 生成文案"""
        data = read_all()
        self.temp = data['temp']
        self.light = data['light']
        self.pir = data['pir']

        # 第一次运行，先存基准值，不判断
        if self.last_temp is None:
            self.last_temp = self.temp
            self.last_light = self.light
            self.level = 0
            self.message = calm_text()
            return

        # 计算变化量
        temp_delta = self.temp - self.last_temp        # 温度变化（可正可负）
        light_delta = abs(self.light - self.last_light) # 光照波动（取绝对值）

        # 判断每个传感器是否异常
        weird = {
            'temp': abs(temp_delta) > config.TEMP_DELTA_THRESHOLD,  # 温度波动 > 阈值
            'light': light_delta > config.LIGHT_DELTA_THRESHOLD,    # 光照波动 > 阈值
            'pir': self.pir                                         # 红外检测到人
        }

        # 统计异常数量 → 定级
        count = sum(weird.values())

        if count == 0:
            self.level = 0          # 平静
        elif count == 1:
            self.level = 1          # 疑似
        elif count == 2:
            self.level = 2          # 警告
        else:
            self.level = 3          # 显灵

        # 生成叙事文案
        if self.level == 0:
            self.message = calm_text()
        else:
            self.message = detect_text(weird)

        # 如果是警告及以上，记录到日志
        if self.level >= 2:
            import time
            t = time.localtime()
            timestamp = "{:02d}:{:02d}:{:02d}".format(t[3], t[4], t[5])
            self.log.insert(0, (timestamp, self.level, self.message))
            if len(self.log) > 20:
                self.log = self.log[:20]  # 只保留最近 20 条

        # 更新上一次读数
        self.last_temp = self.temp
        self.last_light = self.light
