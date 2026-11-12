# calendar_utils.py
"""历法转换：公历 ↔ 农历、四柱"""
from datetime import date
from lunar_python import Solar
from .constants import ZHI_TO_HOUR


def solar_to_lunar(solar_date: date, hour_zhi: str) -> dict:
    """公历 → 农历年支、月、日、时支。闰月取绝对值。"""
    h = ZHI_TO_HOUR[hour_zhi]
    solar = Solar.fromYmdHms(solar_date.year, solar_date.month,
                             solar_date.day, h, 0, 0)
    lunar = solar.getLunar()
    return {
        "year_zhi": lunar.getYearZhi(),
        "month": abs(lunar.getMonth()),
        "day": lunar.getDay(),
        "hour_zhi": hour_zhi,
        "lunar_text": (
            f"{lunar.getYearInChinese()}年"
            f"{lunar.getMonthInChinese()}月"
            f"{lunar.getDayInChinese()}"
        ),
        "is_leap": lunar.getMonth() < 0,
    }


def get_bazi(solar_date: date, hour_zhi: str) -> dict:
    """四柱八字"""
    h = ZHI_TO_HOUR[hour_zhi]
    solar = Solar.fromYmdHms(solar_date.year, solar_date.month,
                             solar_date.day, h, 0, 0)
    lunar = solar.getLunar()
    return {
        "年柱": lunar.getYearInGanZhi(),
        "月柱": lunar.getMonthInGanZhi(),
        "日柱": lunar.getDayInGanZhi(),
        "时柱": lunar.getTimeInGanZhi(),
        "年干": lunar.getYearGan(),
        "年支": lunar.getYearZhi(),
        "农历": (
            f"{lunar.getYearInChinese()}年"
            f"{lunar.getMonthInChinese()}月"
            f"{lunar.getDayInChinese()}"
        ),
        "时辰": lunar.getTimeZhi(),
    }
