"""
幽灵探测器 - 传感器驱动
封装三个传感器：温度(板载)、光敏(ADC)、红外(数字)
提供统一的 read_all() 接口
"""

from machine import Pin, ADC
import esp32

# ==================== 传感器初始化 ====================

# 1. 板载温度传感器（ESP32 内部）
# 注意：板载温度不准绝对温度，但变化率是可靠的，正好拿来用

# 2. 光敏传感器（ADC）
light_adc = ADC(Pin(10))
light_adc.atten(ADC.ATTN_11DB)      # 0-3.3V 范围

# 3. 红外人体感应（数字输入）
pir = Pin(6, Pin.IN)


# ==================== 读取函数 ====================

def read_temperature():
    """
    读取板载温度（华氏度转摄氏度）
    返回: 温度值 °C
    """
    f = esp32.raw_temperature()  # 华氏度
    c = (f - 32) / 1.8            # 转摄氏度
    return c


def read_light():
    """
    读取光敏传感器
    返回: ADC 值 (0-4095)，越小越暗，越大越亮
    """
    return light_adc.read()


def read_pir():
    """
    读取红外人体感应
    返回: True=检测到人, False=没人
    """
    return pir.value() == 1


def read_all():
    """
    一次性读取全部传感器
    返回: {'temp': 温度, 'light': 光照, 'pir': 红外}
    """
    return {
        'temp': read_temperature(),
        'light': read_light(),
        'pir': read_pir()
    }
