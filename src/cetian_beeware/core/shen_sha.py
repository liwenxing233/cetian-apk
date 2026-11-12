# core/shen_sha.py
"""流年十二神煞"""
from ..constants import ZHI, ZHI_INDEX, LIU_NIAN_SHEN_SHA


def an_liu_nian_shen_sha(year_zhi: str) -> dict:
    """
    从生年支起太岁，顺行十二宫。
    返回 {地支: {"name", "ji_xiong", "alias"}}
    """
    start = ZHI_INDEX[year_zhi]
    return {
        ZHI[(start + i) % 12]: {
            "name": name,
            "ji_xiong": jx,
            "alias": alias,
        }
        for i, (name, jx, alias) in enumerate(LIU_NIAN_SHEN_SHA)
    }
