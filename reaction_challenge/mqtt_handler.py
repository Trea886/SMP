"""
Reaction Challenge - MQTT Score Upload + Remote Control
WiFi + MQTT connection, publish scores, receive web commands
"""

import network
import time
from simple import MQTTClient

# ==================== Config ====================
WIFI_SSID  = 'iPhone'
WIFI_PASS  = '7878789191'
MQTT_HOST  = 'broker.emqx.io'
MQTT_PORT  = 1883
CLIENT_ID  = 'ESP32_Reaction'
TOPIC_SCORE   = '/reaction/score'
TOPIC_CONTROL = '/reaction/control'

# ==================== State ====================
wlan = None
client = None
connected = False

# Command queue from web
_commands = []

# ==================== WiFi ====================

def connect_wifi():
    global wlan
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    if wlan.isconnected():
        print('[WiFi] Already connected:', wlan.ifconfig()[0])
        return True

    print('[WiFi] Connecting to', WIFI_SSID, '...')
    wlan.connect(WIFI_SSID, WIFI_PASS)

    timeout = 15
    while not wlan.isconnected() and timeout > 0:
        time.sleep(1)
        timeout -= 1
        print('  .', end='')

    if wlan.isconnected():
        print('\n[WiFi] Connected! IP:', wlan.ifconfig()[0])
        return True
    else:
        print('\n[WiFi] Failed!')
        return False


# ==================== MQTT ====================

def _on_control_msg(topic, msg):
    """Callback: web sent a command"""
    try:
        cmd = msg.decode('utf-8')
        _commands.append(cmd)
        print('[MQTT] Received command:', cmd)
    except:
        pass

def connect_mqtt():
    global client, connected

    if not wlan or not wlan.isconnected():
        if not connect_wifi():
            connected = False
            return False

    try:
        client = MQTTClient(CLIENT_ID, MQTT_HOST, MQTT_PORT)
        client.set_callback(_on_control_msg)
        client.connect()
        client.subscribe(TOPIC_CONTROL)
        connected = True
        print('[MQTT] Connected to', MQTT_HOST)
        return True
    except Exception as e:
        print('[MQTT] Connect failed:', e)
        connected = False
        return False


# ==================== Publish ====================

def upload_score(score, mode='gesture', combo=0, avg_ms=0, questions=0):
    global client, connected

    if not connected:
        if not connect_mqtt():
            return False

    try:
        payload = '{{"device":"{}","score":{},"mode":"{}","combo":{},"avg_ms":{},"questions":{}}}'.format(
            CLIENT_ID, score, mode, combo, avg_ms, questions
        )
        client.publish(TOPIC_SCORE, payload)
        print('[MQTT] Published:', payload)
        return True
    except Exception as e:
        print('[MQTT] Publish failed:', e)
        connected = False
        return False


# ==================== Incoming commands ====================

def check_command():
    """
    Non-blocking check: returns the oldest pending command, or None.
    Call this once per main loop tick.
    """
    global client
    # Check for incoming MQTT messages
    if client and connected:
        try:
            client.check_msg()
        except:
            pass

    if _commands:
        return _commands.pop(0)
    return None


# ==================== Init ====================

def start():
    try:
        connect_wifi()
        connect_mqtt()
    except Exception as e:
        print('[MQTT] Init failed:', e)
