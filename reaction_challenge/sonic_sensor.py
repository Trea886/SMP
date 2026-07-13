"""
HC-SR04 超声波 — 安全版（自带超时）
"""

from machine import Pin
from time import sleep_us, ticks_us, ticks_diff

TRIG = Pin(8, Pin.OUT)
ECHO = Pin(9, Pin.IN)

def read():
    TRIG.value(0)
    sleep_us(5)
    TRIG.value(1)
    sleep_us(10)
    TRIG.value(0)

    t0 = ticks_us()
    while ECHO.value() == 0:
        if ticks_diff(ticks_us(), t0) > 30000:
            return -1

    t1 = ticks_us()
    while ECHO.value() == 1:
        if ticks_diff(ticks_us(), t1) > 30000:
            return -1

    return round(ticks_diff(ticks_us(), t1) * 0.017, 1)


# 兼容旧版
class HCSR04:
    def __init__(self, trig, echo):
        self.trig = trig
        self.echo = echo
    def getDistance(self):
        return read()
