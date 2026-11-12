# core/extras.py
"""扩展功能：十二长生、地星会源、格局判定"""
from ..constants import ZHI, ZHI_INDEX, LIU_HE, YANG_GAN

CHANG_SHENG = ["长生", "沐浴", "冠带", "临官", "帝旺", "衰", "病", "死", "墓", "绝", "胎", "养"]


def calc_chang_sheng(ming_gong: str, shen_gong: str, year_gan: str, gender: str) -> dict:
    """计算十二长生"""
    is_yang = year_gan in YANG_GAN
    is_male = gender == "男"
    yang_nan_yin_nv = (is_yang and is_male) or ((not is_yang) and (not is_male))

    if yang_nan_yin_nv:
        start_idx = ZHI_INDEX[ming_gong]
        direction = 1  # 顺
    else:
        start_idx = ZHI_INDEX[shen_gong]
        direction = -1  # 逆

    result = {}
    for i, name in enumerate(CHANG_SHENG):
        pos = ZHI[(start_idx + direction * i) % 12]
        result[pos] = name
    return result


def calc_di_xing(month: int, day: int, year_zhi: str, hour_zhi: str) -> dict:
    """计算地星会源（提取明确起法的星曜）"""
    result = {z: [] for z in ZHI}

    # 人专：巳起子时，顺数至生时
    rz_idx = (ZHI_INDEX["巳"] + ZHI_INDEX[hour_zhi]) % 12
    result[ZHI[rz_idx]].append("人专")

    # 煞贡：酉起子时，顺数至生时
    sg_idx = (ZHI_INDEX["酉"] + ZHI_INDEX[hour_zhi]) % 12
    result[ZHI[sg_idx]].append("煞贡")

    # 左辅：辰起子年，顺行至生年
    zf_idx = (ZHI_INDEX["辰"] + ZHI_INDEX[year_zhi]) % 12
    result[ZHI[zf_idx]].append("左辅")

    # 右弼：戌起子年，逆行至生年
    yb_idx = (ZHI_INDEX["戌"] - ZHI_INDEX[year_zhi]) % 12
    result[ZHI[yb_idx]].append("右弼")

    # 三台八座（同十八飞星起法，这里简化复用）
    st_idx = (ZHI_INDEX["辰"] + month - 1 + day - 1) % 12
    result[ZHI[st_idx]].append("台(地)")
    bz_idx = (ZHI_INDEX["戌"] - (month - 1) - (day - 1)) % 12
    result[ZHI[bz_idx]].append("座(地)")

    # 八凶星
    # 丧门：子起正月，逆行至生月
    sm_idx = (ZHI_INDEX["子"] - (month - 1)) % 12
    result[ZHI[sm_idx]].append("丧门")
    # 白虎(异虎)：丧门后一位(逆)
    bh_idx = (sm_idx - 1) % 12
    result[ZHI[bh_idx]].append("白虎")
    # 血光：丧门后二位(逆)
    xg_idx = (sm_idx - 2) % 12
    result[ZHI[xg_idx]].append("血光")
    # 吊客：生年六合
    dk_idx = ZHI_INDEX[LIU_HE[year_zhi]]
    result[ZHI[dk_idx]].append("吊客")
    # 破败：丑起正月，顺行至生月
    pb_idx = (ZHI_INDEX["丑"] + month - 1) % 12
    result[ZHI[pb_idx]].append("破败")
    # 大耗：根据原文，可能在太乙后，这里默认放午
    dh_idx = ZHI_INDEX["午"]
    result[ZHI[dh_idx]].append("大耗")

    return result


def calc_ge_ju(chart_data: dict, ming_gong: str, shen_gong: str, hour_zhi: str) -> list:
    """格局判定"""
    results = []
    mp = ZHI_INDEX[ming_gong]
    sp = ZHI_INDEX[shen_gong]

    # 1. 身溺江湖格
    if ming_gong in ["亥", "子"] and shen_gong in ["亥", "子"]:
        # 检查该宫主星是否入庙
        zheng = chart_data[ming_gong]["zheng_yao"]
        is_ru_miao = any(s["mw"] == "庙" for s in zheng)
        if not is_ru_miao:
            results.append("身溺江湖格")

    # 2. 子投罗网格
    if ming_gong in ["戌", "亥", "辰", "巳"] and shen_gong in ["戌", "亥", "辰", "巳"]:
        results.append("子投罗网格")

    # 3. 磨烛为命格
    ming_fu = [s["name"] for s in chart_data[ming_gong]["fu_jia"]]
    if "天刃" in ming_fu:
        results.append("磨烛为命格")

    # 4. 命坐富门格 (天刃天虚居卯)
    ma_idx = ZHI_INDEX["卯"]
    if "天刃" in [s["name"] for s in chart_data["卯"]["fu_jia"]] and "天虚" in [s["name"] for s in
                                                                                chart_data["卯"]["zheng_yao"]]:
        results.append("命坐富门格")

    # 5. 蛇入龙宫
    if hour_zhi == "卯" and ming_gong == "卯":
        results.append("蛇入龙宫")

    return results