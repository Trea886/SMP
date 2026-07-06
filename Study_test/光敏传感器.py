'''
实验名称：光敏传感器（2.4寸LCD版本）
版本：v1.0
平台：pyWiFi ESP32-S3
作者：01Studio
说明：通过光敏传感器对外界环境光照强度测量并在LCD上显示。
'''

#导入相关模块
from tftlcd import LCD24
from machine import Pin, ADC, Timer

#定义常用颜色
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)

#初始化2.4寸LCD
d = LCD24(portrait=1)  # 默认竖屏
d.fill(BLACK)  # 填充黑色背景

#初始化ADC，Pin=10，11DB衰减，测量电压0-3.3V
Light = ADC(Pin(10))
Light.atten(ADC.ATTN_11DB)

#中断回调函数
def fun(tim):
    d.fill(BLACK)  # 清屏显示黑色背景

    d.printStr('01Studio', 10, 10, WHITE, size=2)        # 首行显示01Studio
    d.printStr('Light test:', 10, 50, WHITE, size=1)     # 次行显示实验名称

    value = Light.read()  # 获取ADC数值

    # 显示ADC数值
    d.printStr('ADC: ' + str(value) + ' (0-4095)', 10, 90, CYAN, size=1)
    # 计算电压值，获得的数据0-4095相当于0-3.3V，保留2位小数
    d.printStr('Volt: ' + str('%.2f' % (value / 4095 * 3.3)) + ' V', 10, 120, CYAN, size=1)

    # 判断光照强度，分3档显示
    if 0 < value <= 1365:
        d.printStr('Bright', 10, 160, GREEN, size=2)      # 明亮
    elif 1365 < value <= 2730:
        d.printStr('Normal', 10, 160, YELLOW, size=2)     # 正常
    elif 2730 < value <= 4095:
        d.printStr('Weak', 10, 160, RED, size=2)          # 暗

#开启RTOS定时器
tim = Timer(1)
tim.init(period=1000, mode=Timer.PERIODIC, callback=fun)  # 周期1s
