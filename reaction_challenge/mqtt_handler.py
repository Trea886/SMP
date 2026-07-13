"""
Reaction Challenge - MQTT Score Upload + Remote Control
WiFi + MQTT connection, publish scores, receive web commands
"""

import network
import time
from simple import MQTTClient

# ==================== Config ====================
WIFI_SSID  = 'iPhone'
WIFI_PASS  = '1029384756'
MQTT_HOST  = 'broker.emqx.io'
MQTT_PORT  = 1883
CLIENT_ID  = 'ESP32_Reaction'
TOPIC_SCORE   = '/reaction/score'
TOPIC_CONTROL = '/reaction/control'
TOPIC_PLAYER  = '/reaction/player'

# ==================== State ====================
wlan = None
client = None
connected = False
current_player = ''

# Command queue from web
_commands = []

# Player name queue
_player_name = None

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

def _on_mqtt_msg(topic, msg):
    """Callback: handles both control commands and player name"""
    global current_player, _player_name
    try:
        t = topic.decode('utf-8')
        data = msg.decode('utf-8')

        if t == TOPIC_PLAYER:
            # Player name from web
            if '"name"' in data:
                # Extract name from '{"name":"xxx"}'
                start = data.find('"name":"') + 8
                end = data.find('"', start)
                if end > start:
                    current_player = data[start:end]
                    _player_name = current_player
                    print('[MQTT] Player name set:', current_player)
            else:
                current_player = data.strip().strip('"')
                _player_name = current_player
                print('[MQTT] Player name set:', current_player)
        elif t == TOPIC_CONTROL:
            _commands.append(data)
            print('[MQTT] Received command:', data)
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
        client.set_callback(_on_mqtt_msg)
        client.connect()
        client.subscribe(TOPIC_CONTROL)
        client.subscribe(TOPIC_PLAYER)
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
        name = current_player if current_player else CLIENT_ID
        payload = '{{"device":"{}","score":{},"mode":"{}","combo":{},"avg_ms":{},"questions":{}}}'.format(
            name, score, mode, combo, avg_ms, questions
        )
        client.publish(TOPIC_SCORE, payload)
        print('[MQTT] Published:', payload)
        return True
    except Exception as e:
        print('[MQTT] Publish failed:', e)
        connected = False
        return False


# ==================== Player Name ====================

def get_player():
    """Return current player name, or empty string if not set"""
    global _player_name
    if _player_name:
        name = _player_name
        _player_name = None  # consume it
        return name
    return current_player if current_player else ''


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
