# -*- coding: utf-8 -*-
"""
bazi.data - 八字数据层重构
中心化的五行/干支/神煞索引，支持高效查询
"""

from collections import defaultdict
from typing import Dict, List, Set, Optional, Tuple
from bidict import bidict

# ============================================================
# 核心数据（从 ganzhi.py 迁移）
# ============================================================

Gan = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
Zhi = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

# 天干五行
gan5 = {"甲": "木", "乙": "木", "丙": "火", "丁": "火", "戊": "土", "己": "土",
        "庚": "金", "辛": "金", "壬": "水", "癸": "水"}

# 地支五行
zhi_wuhangs = {"子": "水", "丑": "土", "寅": "木", "卯": "木", "辰": "土", "巳": "火",
               "午": "火", "未": "土", "申": "金", "酉": "金", "戌": "土", "亥": "水"}

# 地支藏干及其强度
zhi5_list = {
    "子": ["癸"],
    "丑": ["己", "癸", "辛"],
    "寅": ["甲", "丙", "戊"],
    "卯": ["乙"],
    "辰": ["戊", "乙", "癸"],
    "巳": ["丙", "戊", "庚"],
    "午": ["丁", "己"],
    "未": ["己", "丁", "乙"],
    "申": ["庚", "壬", "戊"],
    "酉": ["辛"],
    "戌": ["戊", "辛", "丁"],
    "亥": ["壬", "甲"],
}

# 天干强度值（通根强度）
stem_strength = {"甲": 3, "乙": 1, "丙": 6, "丁": 4, "戊": 5, "己": -4, "庚": -1, "辛": -3, "壬": -5, "癸": -6,
                 "子": -6, "丑": -4, "寅": 3, "卯": 1, "辰": -4, "巳": 5, "午": 6, "未": 3, "申": -2, "酉": -3,
                 "戌": 4, "亥": -5}

# 地支藏干强度
zhi5_strength = {
    "子": {"癸": 8},
    "丑": {"己": 5, "癸": 2, "辛": 1},
    "寅": {"甲": 5, "丙": 2, "戊": 1},
    "卯": {"乙": 8},
    "辰": {"戊": 5, "乙": 2, "癸": 1},
    "巳": {"丙": 5, "戊": 2, "庚": 1},
    "午": {"丁": 5, "己": 3},
    "未": {"己": 5, "丁": 2, "乙": 1},
    "申": {"庚": 5, "壬": 2, "戊": 1},
    "酉": {"辛": 8},
    "戌": {"戊": 5, "辛": 2, "丁": 1},
    "亥": {"壬": 5, "甲": 3},
}


# ============================================================
# 五行索引 - WuxingIndex
# ============================================================

class WuxingIndex:
    """五行索引 - 从任意角度快速查询干支与五行的关系"""

    def __init__(self):
        # 天干 → 五行
        self.stem_wuhang = dict(gan5)

        # 地支 → 五行
        self.branch_wuhang = dict(zhi_wuhangs)

        # 五行 → 天干集合
        self.wuhang_stems = defaultdict(set)
        for gan, wh in gan5.items():
            self.wuhang_stems[wh].add(gan)

        # 五行 → 地支集合
        self.wuhang_branches = defaultdict(set)
        for zhi, wh in zhi_wuhangs.items():
            self.wuhang_branches[wh].add(zhi)

        # 天干/地支 → 强度值
        self.stem_strength = {k: v for k, v in stem_strength.items() if k in Gan}
        self.branch_strength = {k: v for k, v in stem_strength.items() if k in Zhi}

        # 地支藏干列表（快速查找）
        self.branch_stems = dict(zhi5_list)

        # 地支藏干强度
        self.branch_stem_strength = dict(zhi5_strength)

        # 天干相合关系
        self.gan_he = {
            "甲": "己", "己": "甲",
            "乙": "庚", "庚": "乙",
            "丙": "辛", "辛": "丙",
            "丁": "壬", "壬": "丁",
            "戊": "癸", "癸": "戊",
        }

        # 天干相冲关系
        self.gan_chong = {
            "甲": "庚", "庚": "甲",
            "乙": "辛", "辛": "乙",
            "丙": "壬", "壬": "丙",
            "丁": "癸", "癸": "丁",
        }

        # 地支相冲关系
        self.zhi_chong = {
            "子": "午", "午": "子",
            "丑": "未", "未": "丑",
            "寅": "申", "申": "寅",
            "卯": "酉", "酉": "卯",
            "辰": "戌", "戌": "辰",
            "巳": "亥", "亥": "巳",
        }

        # 地支相合关系 (地支两两相合，key 排序)
        self.zhi_he = {
            ("子", "丑"): "土",
            ("丑", "子"): "土",
            ("寅", "亥"): "木",
            ("亥", "寅"): "木",
            ("卯", "戌"): "火",
            ("戌", "卯"): "火",
            ("辰", "酉"): "金",
            ("酉", "辰"): "金",
            ("巳", "申"): "水",
            ("申", "巳"): "水",
            ("午", "未"): "土",
            ("未", "午"): "土",
        }

        # 地支三合局
        self.zhi_3he = {
            ("申", "子", "辰"): "水",
            ("子", "申", "辰"): "水",
            ("辰", "子", "申"): "水",
            ("巳", "酉", "丑"): "金",
            ("酉", "巳", "丑"): "金",
            ("丑", "巳", "酉"): "金",
            ("寅", "午", "戌"): "火",
            ("午", "寅", "戌"): "火",
            ("戌", "寅", "午"): "火",
            ("亥", "卯", "未"): "木",
            ("卯", "亥", "未"): "木",
            ("未", "亥", "卯"): "木",
        }

        # 地支三会局
        self.zhi_hui = {
            ("亥", "子", "丑"): "水",
            ("寅", "卯", "辰"): "木",
            ("巳", "午", "未"): "火",
            ("申", "酉", "戌"): "金",
        }

        # 地支相刑
        self.zhi_xing = {
            ("寅", "巳"): "寅刑巳 无恩之刑",
            ("巳", "申"): "巳刑申 无恩之刑",
            ("申", "寅"): "申刑寅 无恩之刑",
            ("未", "丑"): "未刑丑 持势之刑",
            ("丑", "戌"): "丑刑戌 持势之刑",
            ("戌", "未"): "戌刑未 持势之刑",
            ("子", "卯"): "子刑卯 无礼之刑",
            ("卯", "子"): "卯刑子 无礼之刑",
        }

        # 地支相害
        self.zhi_hai = {
            ("子", "未"): "未害子 势家相害",
            ("丑", "午"): "午害丑 官鬼相害",
            ("寅", "巳"): "寅巳互相相害",
            ("卯", "辰"): "卯害辰 以少凌长",
            ("申", "亥"): "申亥互相相害",
            ("酉", "戌"): "戌害酉 嫉妒相害",
        }

        # 地支相破
        self.zhi_po = {
            ("子", "酉"): "子酉相破",
            ("午", "卯"): "午卯相破",
            ("辰", "丑"): "辰丑相破",
            ("戌", "未"): "戌未相破",
        }

        # 地支六合的拱（两支相隔，中神）
        self.gong_he = {
            ("申", "辰"): "子",
            ("巳", "丑"): "酉",
            ("寅", "戌"): "午",
            ("亥", "未"): "卯",
        }

    def get_stems_by_wuhang(self, wuhang: str) -> Set[str]:
        """查某五行对应的所有天干"""
        return self.wuhang_stems.get(wuhang, set())

    def get_branches_by_wuhang(self, wuhang: str) -> Set[str]:
        """查某五行对应的所有地支"""
        return self.wuhang_branches.get(wuhang, set())

    def get_all_by_wuhang(self, wuhang: str) -> Dict[str, Set[str]]:
        """查某五行对应的所有干支"""
        return {
            "天干": self.get_stems_by_wuhang(wuhang),
            "地支": self.get_branches_by_wuhang(wuhang),
        }

    def query_gan_relations(self, gan: str) -> Dict[str, str]:
        """查某天干的相合/相冲"""
        return {
            "合": self.gan_he.get(gan, ""),
            "冲": self.gan_chong.get(gan, ""),
        }

    def query_zhi_all_relations(self, zhi: str) -> Dict[str, any]:
        """查某地支的所有关系（合/冲/刑/害/破/三合/三会）"""
        relations = {}

        # 相冲
        chong = self.zhi_chong.get(zhi)
        if chong:
            relations["冲"] = chong

        # 相合（六合）
        he_results = []
        for (z1, z2), result in self.zhi_he.items():
            if z1 == zhi or z2 == zhi:
                he_results.append({"partner": z1 if z2 == zhi else z2, "result": result})
        if he_results:
            relations["合"] = he_results

        # 三合局
        he3_results = []
        for (z1, z2, z3), result in self.zhi_3he.items():
            if zhi in (z1, z2, z3):
                he3_results.append({"partners": [z for z in (z1, z2, z3) if z != zhi], "result": result})
        if he3_results:
            relations["三合"] = he3_results

        # 三会局
        hui_results = []
        for (z1, z2, z3), result in self.zhi_hui.items():
            if zhi in (z1, z2, z3):
                hui_results.append({"partners": [z for z in (z1, z2, z3) if z != zhi], "result": result})
        if hui_results:
            relations["三会"] = hui_results

        # 相刑
        xing_results = []
        for (z1, z2), desc in self.zhi_xing.items():
            if zhi in (z1, z2):
                xing_results.append({"partner": z1 if z2 == zhi else z2, "desc": desc})
        if xing_results:
            relations["刑"] = xing_results

        # 相害
        hai_results = []
        for (z1, z2), desc in self.zhi_hai.items():
            if zhi in (z1, z2):
                hai_results.append({"partner": z1 if z2 == zhi else z2, "desc": desc})
        if hai_results:
            relations["害"] = hai_results

        # 相破
        po_results = []
        for (z1, z2), desc in self.zhi_po.items():
            if zhi in (z1, z2):
                po_results.append({"partner": z1 if z2 == zhi else z2, "desc": desc})
        if po_results:
            relations["破"] = po_results

        return relations

    def check_gan_he(self, gan1: str, gan2: str) -> bool:
        """检查两天干是否相合"""
        return self.gan_he.get(gan1) == gan2

    def check_gan_chong(self, gan1: str, gan2: str) -> bool:
        """检查两天干是否相冲"""
        return self.gan_chong.get(gan1) == gan2

    def check_zhi_he(self, zhi1: str, zhi2: str) -> Optional[str]:
        """检查两地支是否相合，返回合化结果"""
        key = tuple(sorted((zhi1, zhi2)))
        return self.zhi_he.get(key)

    def check_zhi_chong(self, zhi1: str, zhi2: str) -> bool:
        """检查两地支是否相冲"""
        return self.zhi_chong.get(zhi1) == zhi2

    def check_zhi_xing(self, zhi1: str, zhi2: str) -> Optional[str]:
        """检查两地支是否相刑"""
        key = (zhi1, zhi2)
        reverse = (zhi2, zhi1)
        return self.zhi_xing.get(key) or self.zhi_xing.get(reverse)

    def check_zhi_hai(self, zhi1: str, zhi2: str) -> Optional[str]:
        """检查两地支是否相害"""
        key = (zhi1, zhi2)
        reverse = (zhi2, zhi1)
        return self.zhi_hai.get(key) or self.zhi_hai.get(reverse)

    def check_zhi_po(self, zhi1: str, zhi2: str) -> bool:
        """检查两地支是否相破"""
        key = (zhi1, zhi2)
        reverse = (zhi2, zhi1)
        return key in self.zhi_po or reverse in self.zhi_po

    def calc_root_strength(self, gan: str, zhi_list: List[str]) -> Dict[str, List[str]]:
        """
        计算某天干在某四柱地支中的通根强弱

        Args:
            gan: 天干（如"甲"）
            zhi_list: 四柱地支列表 ["年支", "月支", "日支", "时支"]

        Returns:
            {强:[...], 中:[...], 弱:[...]}}
        """
        target_wuhang = self.stem_wuhang.get(gan)
        if not target_wuhang:
            return {"强": [], "中": [], "弱": []}

        result = {"强": [], "中": [], "弱": []}

        for zhi in zhi_list:
            if zhi not in self.branch_stems:
                continue
            stems_in_zhi = self.branch_stems[zhi]

            if len(stems_in_zhi) == 1:
                # 单藏天干（如子藏癸）
                if stems_in_zhi[0] == gan:
                    result["强"].append(zhi)
            else:
                # 多藏天干
                if gan in stems_in_zhi:
                    strength = self.branch_stem_strength.get(zhi, {}).get(gan, 0)
                    if strength >= 5:
                        result["强"].append(zhi)
                    elif strength >= 2:
                        result["中"].append(zhi)
                    else:
                        result["弱"].append(zhi)

        return {k: v for k, v in result.items() if v}


# ============================================================
# 神煞索引 - ShenShaIndex
# ============================================================

class ShenShaIndex:
    """神煞索引 - O(1) 查询神煞（替代 datas.py 中的线性扫描）"""

    def __init__(self):
        # 预建索引：{zhi: [shen1, shen2, ...]}
        self._year_shens_index = defaultdict(list)
        self._month_shens_index = defaultdict(list)
        self._day_shens_index = defaultdict(list)

        # 季煞（岁煞）
        self._ji_shens = {}

        # 日煞（时杀师）
        self._shi_shens = {}

    def build_year_index(self, year_shens: dict):
        """从 year_shens 数据构建索引"""
        self._year_shens_index.clear()
        for shen, zhi_map in year_shens.items():
            for zhi in zhi_map:
                if zhi not in self._year_shens_index:
                    self._year_shens_index[zhi] = []
                self._year_shens_index[zhi].append(shen)

    def build_month_index(self, month_shens: dict):
        """从 month_shens 数据构建索引"""
        self._month_shens_index.clear()
        for shen, zhi_map in month_shens.items():
            for zhi in zhi_map:
                if zhi not in self._month_shens_index:
                    self._month_shens_index[zhi] = []
                self._month_shens_index[zhi].append(shen)

    def build_day_index(self, day_shens: dict):
        """从 day_shens 数据构建索引"""
        self._day_shens_index.clear()
        for shen, zhi_map in day_shens.items():
            for zhi in zhi_map:
                if zhi not in self._day_shens_index:
                    self._day_shens_index[zhi] = []
                self._day_shens_index[zhi].append(shen)

    def query_year_shens(self, zhi: str) -> List[str]:
        """查某地支的年煞"""
        return self._year_shens_index.get(zhi, [])

    def query_month_shens(self, gan: str, zhi: str) -> List[str]:
        """查某干支的月煞（需同时满足天干和地支条件）"""
        shens = []
        for shen, zhi_map in self._month_shens_index.items():
            if zhi in zhi_map:
                shens.append(shen)
        return shens

    def query_day_shens(self, zhi: str) -> List[str]:
        """查某地支的日煞"""
        return self._day_shens_index.get(zhi, [])

    def query_all_shens(self, gan: str, zhi: str, me: str) -> List[str]:
        """查某柱的所有神煞（年/月/日）"""
        results = []
        results.extend(self.query_year_shens(zhi))
        results.extend(self.query_day_shens(zhi))
        # 月煞需要额外处理
        return results


# ============================================================
# 全局单例
# ============================================================

wuxing = WuxingIndex()
shensha = ShenShaIndex()

# ============================================================
# 兼容层 - 从 datas.py 导入原始数据并构建索引
# ============================================================

_year_shens = None
_month_shens = None
_day_shens = None
_g_shens = None


def _build_shensha_index():
    """延迟构建神煞索引（从 datas.py 导入数据后）"""
    global _year_shens, _month_shens, _day_shens, _g_shens

    if _year_shens is None:
        try:
            from datas import year_shens, month_shens, day_shens, g_shens
            _year_shens = year_shens
            _month_shens = month_shens
            _day_shens = day_shens
            _g_shens = g_shens

            if year_shens:
                shensha.build_year_index(year_shens)
            if month_shens:
                shensha.build_month_index(month_shens)
            if day_shens:
                shensha.build_day_index(day_shens)
        except ImportError:
            pass


def query_all_shens(gans: tuple, zhis: tuple, me_gan: str) -> list:
    """
    兼容层：查询八字所有神煞（使用索引加速）

    Args:
        gans: (年干, 月干, 日干, 时干)
        zhis: (年支, 月支, 日支, 时支)
        me_gan: 日干（如"甲"）

    Returns:
        所有神煞名称列表
    """
    _build_shensha_index()

    all_shens = set()

    if not _year_shens:
        return []

    # 年煞
    for shen, zhi_map in _year_shens.items():
        if zhis[0] in zhi_map.get(zhis[0], []):
            all_shens.add(shen)

    # 月煞
    for shen, zhi_map in _month_shens.items():
        for i in range(4):
            if gans[i] in zhi_map.get(zhis[i], []) or zhis[i] in zhi_map.get(zhis[i], []):
                all_shens.add(shen)

    # 日煞
    for shen, zhi_map in _day_shens.items():
        for i in (0, 1, 3):
            if zhis[i] in zhi_map.get(zhis[i], []):
                all_shens.add(shen)

    # 时煞
    for shen, zhi_map in _g_shens.items():
        for i in range(4):
            if zhis[i] in zhi_map.get(me_gan, []):
                all_shens.add(shen)

    return sorted(all_shens)


def query_column_shens(gans: tuple, zhis: tuple, me_gan: str) -> tuple:
    """
    兼容层：查询每柱的神煞字符串（元组格式）

    Args:
        gans: (年干, 月干, 日干, 时干)
        zhis: (年支, 月支, 日支, 时支)
        me_gan: 日干

    Returns:
        (年柱神煞串, 月柱神煞串, 日柱神煞串, 时柱神煞串)
    """
    _build_shensha_index()

    if not _year_shens:
        return ("", "", "", "")

    strs = ["", "", "", ""]
    all_shens = set()

    # 年煞
    for shen, zhi_map in _year_shens.items():
        for i in (1, 2, 3):
            if zhis[i] in zhi_map.get(zhis[i], []):
                strs[i] = shen if not strs[i] else strs[i] + chr(12288) + shen
                all_shens.add(shen)

    # 月煞
    for shen, zhi_map in _month_shens.items():
        for i in range(4):
            if gans[i] in zhi_map.get(zhis[i], []) or zhis[i] in zhi_map.get(zhis[i], []):
                strs[i] = shen if not strs[i] else strs[i] + chr(12288) + shen
                if i == 2 and gans[i] in zhi_map.get(zhis[i], []):
                    strs[i] += "●"
                all_shens.add(shen)

    # 日煞
    for shen, zhi_map in _day_shens.items():
        for i in (0, 1, 3):
            if zhis[i] in zhi_map.get(zhis[i], []):
                strs[i] = shen if not strs[i] else strs[i] + chr(12288) + shen
                all_shens.add(shen)

    # 时煞
    for shen, zhi_map in _g_shens.items():
        for i in range(4):
            if zhis[i] in zhi_map.get(me_gan, []):
                strs[i] = shen if not strs[i] else strs[i] + chr(12288) + shen
                all_shens.add(shen)

    return tuple(strs)
