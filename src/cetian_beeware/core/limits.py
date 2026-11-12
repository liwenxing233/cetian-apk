# core/limits.py
"""起运岁数、大限、小运"""
from ..constants import ZHI, ZHI_INDEX, TIAN_GAN, YANG_GAN


def is_yang_gan(gan: str) -> bool:
    return gan in YANG_GAN


def calc_qiyun_age(year_gan: str) -> dict:
    """
    起运岁数（顺类至甲距离法）。
    从生年天干顺数至下一个『甲』的天干距离，1–10。
    """
    gan_idx = TIAN_GAN.index(year_gan)
    distance = (10 - gan_idx) % 10
    if distance == 0:
        distance = 10
    return {
        "age": distance,
        "method": "顺类至甲距离法",
        "note": "传本『二十甲子』之说与本法存在出入，此数为参考",
    }


def calc_da_xian(ming_gong: str, shen_gong: str,
                 year_gan: str, gender: str,
                 qiyun_age: int) -> list:
    """
    大限：
    阳男阴女从命宫顺行，十年一宫；
    阴男阳女从身宫逆行，十年一宫。
    返回 [(起始虚岁, 结束虚岁, 宫位), ...]，共 12 限。
    """
    is_yang = is_yang_gan(year_gan)
    is_male = gender == "男"
    yang_forward = (is_yang and is_male) or ((not is_yang) and (not is_male))

    if yang_forward:
        start_pos = ming_gong
        direction = +1
    else:
        start_pos = shen_gong
        direction = -1

    start_idx = ZHI_INDEX[start_pos]
    result = []
    age = qiyun_age
    for i in range(12):
        pos = ZHI[(start_idx + direction * i) % 12]
        result.append((age, age + 9, pos))
        age += 10
    return result


def calc_xiao_yun(ming_gong: str, shen_gong: str,
                  year_gan: str, gender: str) -> list:
    """
    小运：
    阳男阴女从身宫逆行，一年一宫；
    阴男阳女从命宫顺行，一年一宫。
    返回 [(虚岁, 宫位), ...]，共 12 条。
    """
    is_yang = is_yang_gan(year_gan)
    is_male = gender == "男"
    yang_nv_forward = (is_yang and is_male) or ((not is_yang) and (not is_male))

    if yang_nv_forward:
        start_pos = shen_gong
        direction = -1
    else:
        start_pos = ming_gong
        direction = +1

    start_idx = ZHI_INDEX[start_pos]
    return [(i + 1, ZHI[(start_idx + direction * i) % 12])
            for i in range(12)]
