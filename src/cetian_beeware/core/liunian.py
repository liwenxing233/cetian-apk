# core/liunian.py
"""流年排盘：流年星曜、神煞、命宫"""
from ..constants import ZHI, ZHI_INDEX, LIU_NIAN_SHEN_SHA, LIU_HE


def calc_liu_nian(year_zhi: str, year_gan: str) -> dict:
    """
    计算流年数据。
    year_zhi: 流年地支
    year_gan: 流年天干
    """
    # 1. 流年命宫：即流年地支所在的宫位
    liu_ming = year_zhi

    # 2. 流年十二神煞：流年地支起太岁，顺行
    liu_shen_sha = {}
    start_idx = ZHI_INDEX[year_zhi]
    for i, (name, jx, _) in enumerate(LIU_NIAN_SHEN_SHA):
        pos = ZHI[(start_idx + i) % 12]
        liu_shen_sha[pos] = name

    # 3. 流年十九星起法
    liu_stars = {z: [] for z in ZHI}

    # 3.1 十二正星：流年位起天虚，逆排
    zheng_order = ["天虚", "天贵", "天印", "天寿", "天空",
                   "红鸾", "天库", "天贯", "文昌", "天福", "天禄", "紫微"]
    for i, star in enumerate(zheng_order):
        pos = ZHI[(start_idx - i) % 12]
        liu_stars[pos].append(star)

    # 3.2 七附星：固定点加午(6)逆至流年太岁
    # 天杖(寅:2), 天异(申:8), 毛头(巳:5), 天刃(亥:11), 天姚(丑:1), 天刑(酉:9), 天哭(子:0)
    fu_stars = {
        "天杖": 2, "天异": 8, "毛头": 5, "天刃": 11,
        "天姚": 1, "天刑": 9, "天哭": 0
    }
    for star, base_idx in fu_stars.items():
        pos_idx = (base_idx + 6 - start_idx) % 12
        liu_stars[ZHI[pos_idx]].append(star)

    return {
        "year_zhi": year_zhi,
        "year_gan": year_gan,
        "liu_ming": liu_ming,
        "shen_sha": liu_shen_sha,
        "stars": liu_stars,
    }