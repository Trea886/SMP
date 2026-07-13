"""
PAJ7620 手势传感器驱动 for MicroPython
I2C 地址 0x73, SCL=8 SDA=9
返回手势: UP / DOWN / LEFT / RIGHT / FORWARD / BACKWARD / NONE
"""

from machine import Pin, I2C
import time

# I2C 初始化 — SCL=8, SDA=9
from machine import SoftI2C
i2c = SoftI2C(scl=Pin(8), sda=Pin(9), freq=50000)

PAJ7620_ADDR = 0x73

# ==================== 寄存器 ====================

# Bank select: 0 = bank0 (配置), 1 = bank1 (数据)
REG_BANK_SEL = 0xEF

# Bank0 — 配置寄存器
REG_SUSPEND = 0x03
REG_GES_ENTRY = 0x41   # 手势检测使能
REG_GES_ENTRY2 = 0x42  # 近距离手势使能

# Bank1 — 手势结果
REG_GES_RESULT = 0x43  # 手势原始值

# 手势值映射
GESTURE_MAP = {
    0x01: 'UP',
    0x02: 'DOWN',
    0x04: 'LEFT',
    0x08: 'RIGHT',
    0x10: 'FORWARD',
    0x20: 'BACKWARD',
    0x40: 'CLOCKWISE',
    0x80: 'COUNTERCLOCKWISE',
}

# ==================== 内部函数 ====================

def _write_reg(reg, val):
    """写一个寄存器"""
    i2c.writeto_mem(PAJ7620_ADDR, reg, bytes([val]))

def _read_reg(reg, n=1):
    """读 n 字节"""
    return i2c.readfrom_mem(PAJ7620_ADDR, reg, n)

def _select_bank(bank):
    """切换寄存器 Bank（0 或 1）"""
    _write_reg(REG_BANK_SEL, bank)

# ==================== 初始化 ====================

def init():
    """初始化 PAJ7620，开启手势检测"""
    print('[GES] Initializing PAJ7620...')

    # 1. 唤醒传感器
    _select_bank(0)
    _write_reg(REG_SUSPEND, 0x00)  # 写 0 唤醒

    # 2. 软件复位（写 0x01 → 唤醒）
    time.sleep_ms(10)

    # 3. 使能手势检测（bank0）
    _select_bank(0)
    _write_reg(REG_GES_ENTRY, 0x01)   # 使能基础手势
    _write_reg(REG_GES_ENTRY2, 0x01)  # 使能近距手势

    time.sleep_ms(100)
    print('[GES] PAJ7620 ready')
    return True

# ==================== 读取手势 ====================

def read_gesture():
    """
    非阻塞读取当前手势
    返回: 'UP' / 'DOWN' / 'LEFT' / 'RIGHT' / 'FORWARD' / 'BACKWARD' / 'NONE'
    """
    _select_bank(1)
    data = _read_reg(REG_GES_RESULT, 1)
    val = data[0]

    gesture = GESTURE_MAP.get(val, 'NONE')

    # 读完后清掉寄存器（写 0）
    if val != 0:
        _select_bank(1)
        _write_reg(REG_GES_RESULT, 0x00)

    return gesture


# ==================== 测试（直接运行此文件） ====================

if __name__ == '__main__':
    print('PAJ7620 Gesture Sensor Test')
    print('I2C devices:', [hex(x) for x in i2c.scan()])

    if init():
        print('Wave your hand over the sensor...')
        while True:
            g = read_gesture()
            if g != 'NONE':
                print('Gesture:', g)
            time.sleep_ms(50)
    else:
        print('Sensor not found! Check wiring.')
