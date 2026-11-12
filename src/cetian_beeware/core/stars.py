# core/stars.py
"""安星：十二正曜、天杖四星、天刑、天姚、天哭、三台八座、龙池凤阁"""
from ..constants import (
    ZHI, ZHI_INDEX, ZHENG_YAO_ORDER, LIU_HE,
)


def an_zheng_yao(year_zhi: str) -> dict:
    """
    十二正曜：未宫起子年，顺数至生年支安紫微；
    从紫微宫逆行，依次安虚、贵、印……
    """
    ziwei_idx = (ZHI_INDEX["未"] + ZHI_INDEX[year_zhi]) % 12
    return {
        star: ZHI[(ziwei_idx - i) % 12]
        for i, star in enumerate(ZHENG_YAO_ORDER)
    }


def an_tian_zhang(month: int) -> dict:
    """天杖四星：子起正月，逆数至生月安天杖；逆布异、毛、刃。"""
    zhang_idx = (ZHI_INDEX["子"] - (month - 1)) % 12
    names = ["天杖", "天异", "毛头", "天刃"]
    return {n: ZHI[(zhang_idx - i) % 12] for i, n in enumerate(names)}


def an_tian_xing(month: int) -> str:
    """天刑：酉起正月，顺数至生月。"""
    return ZHI[(ZHI_INDEX["酉"] + month - 1) % 12]


def an_tian_yao(month: int) -> str:
    """天姚：丑起正月，顺数至生月。"""
    return ZHI[(ZHI_INDEX["丑"] + month - 1) % 12]


def an_tian_ku(year_zhi: str) -> str:
    """天哭：生年支六合位。"""
    return LIU_HE[year_zhi]


def an_san_tai(month: int, day: int) -> str:
    """
    三台：辰起正月，顺数至生月；该月宫起初一，顺数至生日。
    """
    yue_idx = (ZHI_INDEX["辰"] + month - 1) % 12
    return ZHI[(yue_idx + day - 1) % 12]


def an_ba_zuo(month: int, day: int) -> str:
    """
    八座：戌起正月，逆数至生月；该月宫起初一，逆数至生日。
    """
    yue_idx = (ZHI_INDEX["戌"] - (month - 1)) % 12
    return ZHI[(yue_idx - (day - 1)) % 12]


def an_long_chi(year_zhi: str) -> str:
    """龙池：辰起子年，顺数至生年（通行本）。"""
    return ZHI[(ZHI_INDEX["辰"] + ZHI_INDEX[year_zhi]) % 12]


def an_feng_ge(year_zhi: str) -> str:
    """凤阁：戌起子年，逆数至生年（通行本）。"""
    return ZHI[(ZHI_INDEX["戌"] - ZHI_INDEX[year_zhi]) % 12]
