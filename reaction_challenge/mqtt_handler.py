"""
Reaction Challenge - MQTT Score Upload
WiFi + MQTT connection, publish scores to broker
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
TOPIC      = '/reaction/score'

# ==================== State ====================
wlan = None
client = None
connected = False

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

def connect_mqtt():
    global client, connected

    if not wlan or not wlan.isconnected():
        if not connect_wifi():
            connected = False
            return False

    try:
        client = MQTTClient(CLIENT_ID, MQTT_HOST, MQTT_PORT)
        client.connect()
        connected = True
        print('[MQTT] Connected to', MQTT_HOST)
        return True
    except Exception as e:
        print('[MQTT] Connect failed:', e)
        connected = False
        return False


# ==================== Publish ====================

def upload_score(score, mode='gesture', combo=0, avg_ms=0, questions=0):
    """
    Upload game result to MQTT broker.
    Returns True on success, False on failure.
    Game never crashes from network errors.
    """
    global client, connected

    # Auto-connect if needed
    if not connected:
        if not connect_mqtt():
            return False

    try:
        # Build JSON payload
        payload = '{{"device":"{}","score":{},"mode":"{}","combo":{},"avg_ms":{},"questions":{}}}'.format(
            CLIENT_ID, score, mode, combo, avg_ms, questions
        )

        client.publish(TOPIC, payload)
        print('[MQTT] Published:', payload)
        return True

    except Exception as e:
        print('[MQTT] Publish failed:', e)
        connected = False
        return False


# ==================== Init ====================

def start():
    """Call at boot to set up connections in background"""
    try:
        connect_wifi()
        connect_mqtt()
    except Exception as e:
        print('[MQTT] Init failed:', e)
