'''
实验名称：温度传感器 + MQTT发布 + LCD显示（手机可查看）
版本：v1.0
平台：pyWiFi ESP32-S3 + 2.4寸LCD
说明：DS18B20采集温度 → LCD显示 → MQTT发布 → 手机订阅查看
'''

import network, time
from machine import Pin, Timer
from tftlcd import LCD24
from simple import MQTTClient
import onewire, ds18x20

# ==================== 配置区域 ====================
WIFI_SSID = 'iPhone'       # WiFi账号
WIFI_PASS = '7878789191'          # WiFi密码
MQTT_SERVER = 'broker.emqx.io'
MQTT_PORT = 1883
CLIENT_ID = 'MyESP32-Temp'       # 客户端ID（随便改）
TOPIC = '/public/01Studio/Temp1'  # 发布主题（改成你自己独有的，避免和别人冲突）
# =================================================

# 定义颜色
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
CYAN = (0, 255, 255)
YELLOW = (255, 255, 0)

# 初始化2.4寸LCD
d = LCD24(portrait=1)
d.fill(BLACK)
d.printStr('Starting...', 10, 50, WHITE, size=2)

# 初始化DS18B20
ow = onewire.OneWire(Pin(2))
ds = ds18x20.DS18X20(ow)
rom = ds.scan()

# WiFi连接函数
def WIFI_Connect():
    WIFI_LED = Pin(46, Pin.OUT)
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    start_time = time.time()

    if not wlan.isconnected():
        print('Connecting to WiFi...')
        d.fill(BLACK)
        d.printStr('Connecting WiFi...', 10, 30, YELLOW, size=1)
        wlan.connect(WIFI_SSID, WIFI_PASS)

        while not wlan.isconnected():
            WIFI_LED.value(1)
            time.sleep_ms(300)
            WIFI_LED.value(0)
            time.sleep_ms(300)

            if time.time() - start_time > 15:
                print('WiFi Timeout!')
                d.fill(BLACK)
                d.printStr('WiFi Timeout!', 10, 80, RED, size=2)
                return False

    if wlan.isconnected():
        WIFI_LED.value(1)
        print('WiFi Connected:', wlan.ifconfig())
        d.fill(BLACK)
        d.printStr('WiFi Connected!', 10, 10, GREEN, size=1)
        d.printStr('IP:', 10, 40, WHITE, size=1)
        d.printStr(wlan.ifconfig()[0], 10, 65, CYAN, size=1)
        time.sleep(2)
        return True
    return False


# 主程序
if WIFI_Connect():

    # 连接MQTT服务器
    client = MQTTClient(CLIENT_ID, MQTT_SERVER, MQTT_PORT)
    client.connect()
    print('MQTT Connected!')
    d.printStr('MQTT Connected!', 10, 100, GREEN, size=1)
    time.sleep(1)

    # 定时发布温度
    def publish_temp(tim):
        ds.convert_temp()
        temp = ds.read_temp(rom[0])

        msg = str('%.2f' % temp)  # 温度数据作为消息
        client.publish(TOPIC, msg)  # 发布到MQTT

        # LCD显示
        d.fill(BLACK)
        d.printStr('01Studio', 10, 10, WHITE, size=2)
        d.printStr('MQTT Temp Sender', 10, 50, CYAN, size=1)
        d.printStr(str('%.2f' % temp) + ' C', 10, 90, GREEN, size=3)
        d.printStr('Topic:', 10, 160, WHITE, size=1)
        d.printStr(TOPIC, 10, 185, CYAN, size=1)

        print('Published:', msg)  # 串口打印

    # 定时器，每3秒发布一次
    tim = Timer(1)
    tim.init(period=3000, mode=Timer.PERIODIC, callback=publish_temp)

else:
    d.fill(BLACK)
    d.printStr('WiFi Failed!', 10, 80, RED, size=2)
