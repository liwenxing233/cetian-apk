# core/chart.py
"""综合排盘"""
from ..constants import (
    ZHI, ZHI_INDEX, JIU_YANG_XING, JIU_YIN_XING, YANG_ZHI, XING_WU_XING, WU_XING_YI_WEN,
    MIAO, WANG, LE, SHI_XIANG_GONG
)
from .stars import (
    an_zheng_yao, an_tian_zhang, an_tian_xing, an_tian_yao, an_tian_ku,
    an_san_tai, an_ba_zuo, an_long_chi, an_feng_ge,
)
from .palaces import (
    an_ming_gong, an_shen_gong, an_shi_xiang_gong, calc_san_fang_si_zheng,
)
from .limits import calc_qiyun_age, calc_da_xian, calc_xiao_yun
from .shen_sha import an_liu_nian_shen_sha
from .liunian import calc_liu_nian
from .extras import calc_chang_sheng, calc_di_xing, calc_ge_ju


def get_miao_wang(star, zhi):
    if star in MIAO and zhi in MIAO[star]: return "庙"
    if star in WANG and zhi in WANG[star]: return "旺"
    if star in LE and zhi in LE[star]: return "乐"
    return ""


def build_chart(year_zhi: str, year_gan: str, month: int, day: int,
                hour_zhi: str, gender: str,
                liunian_zhi: str = "", liunian_gan: str = "") -> dict:
    zheng = an_zheng_yao(year_zhi)
    zhang_group = an_tian_zhang(month)
    tian_xing = an_tian_xing(month)
    tian_yao = an_tian_yao(month)
    tian_ku = an_tian_ku(year_zhi)
    san_tai = an_san_tai(month, day)
    ba_zuo = an_ba_zuo(month, day)
    long_chi = an_long_chi(year_zhi)
    feng_ge = an_feng_ge(year_zhi)

    zhang_pos = zhang_group["天杖"]
    ming_gong = an_ming_gong(zhang_pos, hour_zhi)
    shen_gong = an_shen_gong(zhang_pos, day, hour_zhi)
    shi_xiang = an_shi_xiang_gong(ming_gong)

    qiyun = calc_qiyun_age(year_gan)
    da_xian = calc_da_xian(ming_gong, shen_gong, year_gan, gender, qiyun["age"])
    xiao_yun = calc_xiao_yun(ming_gong, shen_gong, year_gan, gender)
    shen_sha = an_liu_nian_shen_sha(year_zhi)
    san_fang = calc_san_fang_si_zheng(ming_gong)

    # 扩展功能
    chang_sheng = calc_chang_sheng(ming_gong, shen_gong, year_gan, gender)
    di_xing = calc_di_xing(month, day, year_zhi, hour_zhi)

    chart = {z: {
        "zheng_yao": [], "fu_jia": [], "extra": [], "di_xing": [],
        "shi_xiang": shi_xiang.get(z, ""),
        "shen_sha": shen_sha.get(z),
        "yin_yang": "阳" if z in YANG_ZHI else "阴",
        "chang_sheng": chang_sheng.get(z, ""),
    } for z in ZHI}

    for star, pos in zheng.items():
        chart[pos]["zheng_yao"].append({"name": star, "mw": get_miao_wang(star, pos)})
    for star, pos in zhang_group.items():
        chart[pos]["fu_jia"].append({"name": star, "mw": get_miao_wang(star, pos)})
    chart[tian_xing]["fu_jia"].append({"name": "天刑", "mw": get_miao_wang("天刑", tian_xing)})
    chart[tian_yao]["fu_jia"].append({"name": "天姚", "mw": get_miao_wang("天姚", tian_yao)})
    chart[tian_ku]["fu_jia"].append({"name": "天哭", "mw": get_miao_wang("天哭", tian_ku)})

    for star, pos in [("三台", san_tai), ("八座", ba_zuo), ("龙池", long_chi), ("凤阁", feng_ge)]:
        chart[pos]["extra"].append({"name": star, "mw": ""})

    for pos, stars in di_xing.items():
        for s in stars:
            chart[pos]["di_xing"].append({"name": s, "mw": ""})

    huofu = _calc_huofu(chart)
    ge_ju = calc_ge_ju(chart, ming_gong, shen_gong, hour_zhi)

    liu_data = None
    if liunian_zhi and liunian_gan:
        liu_data = calc_liu_nian(liunian_zhi, liunian_gan)

        # 计算流年转宫（流年命宫起，逆排财帛兄弟等）
        if liu_data:
            liuming = liu_data["liu_ming"]
            liuming_idx = ZHI_INDEX[liuming]
            liu_zhuan_gong = {}
            for i, gname in enumerate(SHI_XIANG_GONG):
                pos = ZHI[(liuming_idx - i) % 12]
                liu_zhuan_gong[pos] = gname
            liu_data["zhuan_gong"] = liu_zhuan_gong

    return {
        "chart": chart,
        "ming_gong": ming_gong,
        "shen_gong": shen_gong,
        "zhang_pos": zhang_pos,
        "ziwei_pos": zheng["紫微"],
        "san_fang_si_zheng": san_fang,
        "qiyun": qiyun,
        "da_xian": da_xian,
        "xiao_yun": xiao_yun,
        "huofu": huofu,
        "shen_sha": shen_sha,
        "liunian": liu_data,
        "ge_ju": ge_ju,
    }


def _calc_huofu(chart: dict) -> list:
    result = []
    for zhi in ZHI:
        is_yang_gong = zhi in YANG_ZHI
        palace_label = "阳宫" if is_yang_gong else "阴宫"
        zheng_names = [s["name"] for s in chart[zhi]["zheng_yao"]]
        fu_names = [s["name"] for s in chart[zhi]["fu_jia"]]
        for star in zheng_names + fu_names:
            if star == "天空":
                result.append(
                    {"star": star, "palace": zhi, "palace_label": palace_label, "wuxing": "—", "category": "特殊星",
                     "judge": "主虚花"})
                continue
            if star in JIU_YANG_XING:
                judge = "福重灾轻" if is_yang_gong else "福轻灾重"
                category = "九阳星"
            elif star in JIU_YIN_XING:
                judge = "灾重福轻" if is_yang_gong else "福重灾轻"
                category = "九阴星"
            else:
                continue
            result.append(
                {"star": star, "palace": zhi, "palace_label": palace_label, "wuxing": XING_WU_XING.get(star, "—"),
                 "category": category, "judge": judge})
    return result