# core/palaces.py
"""命宫、身宫、事项宫、三方四正"""
from ..constants import ZHI, ZHI_INDEX, SHI_XIANG_GONG, SHEN_SPECIAL_DAYS


def an_ming_gong(zhang_pos: str, hour_zhi: str) -> str:
    """
    命宫：天杖宫起生时，顺数至卯。
    公式：命 = (T + 3 − H) mod 12。
    """
    t = ZHI_INDEX[zhang_pos]
    h = ZHI_INDEX[hour_zhi]
    return ZHI[(t + 3 - h) % 12]


def an_shen_gong(zhang_pos: str, birth_day: int, hour_zhi: str) -> str:
    """
    身宫：天杖宫逆数，每宫 2.5 日。
    基础偏移 = floor((日−1) / 2.5)。
    特殊日 {3,8,13,18,23,28}：
      午时（含）之前不加，未时（含）之后偏移 +1。
    """
    t = ZHI_INDEX[zhang_pos]
    h = ZHI_INDEX[hour_zhi]
    offset = int((birth_day - 1) // 2.5)

    if birth_day in SHEN_SPECIAL_DAYS and h >= ZHI_INDEX["未"]:
        offset += 1

    return ZHI[(t - offset) % 12]


def an_shi_xiang_gong(ming_gong: str) -> dict:
    """
    十二事项宫：命宫起，地支逆行。
    返回 {地支: 宫名}。
    """
    start = ZHI_INDEX[ming_gong]
    return {ZHI[(start - i) % 12]: name
            for i, name in enumerate(SHI_XIANG_GONG)}


def calc_san_fang_si_zheng(ming_gong: str) -> dict:
    """
    三方四正：
    三方 = 命宫 + 三合两位（+4、+8）
    四正 = 三方 + 对宫（+6）
    """
    m = ZHI_INDEX[ming_gong]
    san_fang = [ZHI[(m + 4) % 12], ZHI[(m + 8) % 12]]
    dui_gong = ZHI[(m + 6) % 12]
    return {
        "命宫": ming_gong,
        "三合": san_fang,
        "对宫": dui_gong,
        "四正": [ming_gong] + san_fang + [dui_gong],
    }
