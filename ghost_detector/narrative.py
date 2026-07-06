"""
幽灵探测器 - 事件文案库
根据传感器组合，生成对应的"灵异叙事"文案
"""

# ==================== 单传感器触发文案 ====================

NARRATIVE_TEMP = [
    "冷点正在形成...温差 {delta:.1f}°C",
    "温度异常下降！当前变化 {delta:.1f}°C",
    "区域温度骤降，疑似灵体吸热",
    "检测到局部低温区，请保持警惕",
]

NARRATIVE_LIGHT = [
    "EMF 电磁场波动 {delta} μT",
    "2.4GHz 频段异常脉冲信号",
    "电离辐射读数不稳定",
    "检测到微弱光子异常",
]

NARRATIVE_PIR = [
    "侦测到高速移动实体",
    "红外热源信号一闪而过",
    "有东西在移动...速度太快无法锁定",
    "生物信号出现，非人类热源特征",
]

# ==================== 多传感器联动文案 ====================

NARRATIVE_COMBO = [
    "⚠ 多个传感器同时异常！A类完整显灵事件！",
    "⚠ 灵压持续上升，建议立即离开！",
    "⚠ 三级警报：冷点 + EMF + 实体位移同时发生",
    "⚠ 灵魂正在尝试显形，请保持安静",
    "⚠ 超自然现象确认，数据已记录",
]

# ==================== 平静文案 ====================

NARRATIVE_CALM = [
    "环境稳定，未检测到异常",
    "区域安全，继续扫描中...",
    "当前一切正常，灵压为零",
    "平静。继续保持监视",
    "扫描完成，无事件报告",
]


# ==================== 文案选取函数 ====================

import random

_last_temp_text = -1
_last_light_text = -1
_last_pir_text = -1
_last_calm_text = -1
_last_combo_text = -1


def _pick(arr, last_index):
    """从数组中随机选一条，避免跟上一次重复"""
    idx = random.randint(0, len(arr) - 1)
    if idx == last_index and len(arr) > 1:
        idx = (idx + 1) % len(arr)
    return arr[idx], idx


def calm_text():
    """返回一条平静状态文案"""
    global _last_calm_text
    text, _last_calm_text = _pick(NARRATIVE_CALM, _last_calm_text)
    return text


def detect_text(anomalies):
    """
    根据异常类型返回文案
    anomalies: dict, 如 {'temp': True, 'light': False, 'pir': True}
    """
    global _last_temp_text, _last_light_text, _last_pir_text, _last_combo_text

    count = sum(anomalies.values())  # 几个传感器异常

    # 3 个全触发 = 显灵
    if count >= 3:
        text, _last_combo_text = _pick(NARRATIVE_COMBO, _last_combo_text)
        return text

    # 2 个触发 = 联动
    if count >= 2:
        text, _last_combo_text = _pick(NARRATIVE_COMBO, _last_combo_text)
        return text

    # 1 个触发 = 分别处理
    if anomalies.get('temp'):
        text, _last_temp_text = _pick(NARRATIVE_TEMP, _last_temp_text)
        return text
    if anomalies.get('light'):
        text, _last_light_text = _pick(NARRATIVE_LIGHT, _last_light_text)
        return text
    if anomalies.get('pir'):
        text, _last_pir_text = _pick(NARRATIVE_PIR, _last_pir_text)
        return text

    return calm_text()
