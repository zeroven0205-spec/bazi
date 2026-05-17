# -*- coding: utf-8 -*-
"""
bazi_calc.calculator - 八字计算引擎
核心计算逻辑：四柱排盘、五行分数、神煞、大运流年
"""

import datetime
from typing import List, Dict, Any, Optional, Tuple
from collections import namedtuple

from .types import (
    BaziInput, BaziCore, WuXingScores, GanScores,
    BaziColumn, Dayun, Liunian, BaziResult
)
from .bazi_data import BD


# ============================================================
# 核心计算类
# ============================================================

class BaziCalculator:
    """
    八字计算引擎
    
    用法:
        calc = BaziCalculator()
        result = calc.calculate(input_params)
        result = calc.calculate(1990, 3, 15, 19)
        result = calc.calculate(1990, 3, 15, 19, female=True)
    """
    
    def __init__(self):
        # 懒加载数据
        self.Gan = BD.Gan()
        self.Zhi = BD.Zhi()
        self.gan5 = BD.gan5()
        self.zhi_wuhangs = BD.zhi_wuhangs()
        self.zhi5 = BD.zhi5()
        self.zhi5_list = BD.zhi5_list()
        self.ten_deities = BD.ten_deities()
        self.zhi_atts = BD.zhi_atts()
        self.temps = BD.temps()
        self.zhengs = BD.zhengs()
        self.kus = BD.kus()
        self.chongs = BD.chongs()
        self.zhi_6hes = BD.zhi_6hes()
        self.zhi_3hes = BD.zhi_3hes()
        self.gong_he = BD.gong_he()
        self.zhi_hes = BD.zhi_hes()
        self.zhi_huis = BD.zhi_huis()
        self.empties = BD.empties()
        self.year_shens = BD.year_shens()
        self.month_shens = BD.month_shens()
        self.day_shens = BD.day_shens()
        self.g_shens = BD.g_shens()
        self.shens_infos = BD.shens_infos()
        self.tiaohous = BD.tiaohous()
        self.jins = BD.jins()
        self.ges = BD.ges()
        self.siling = BD.siling()
        self.nayins = BD.nayins()
        self.days60 = BD.days60()
        self.chens = BD.chens()
        self.months = BD.months()
        self.summarys = BD.summarys()
        self.tianyis = BD.tianyis()
        self.yutangs = BD.yutangs()
    
    def calculate(
        self,
        year: int,
        month: int,
        day: int,
        time: int,
        female: bool = False,
        lunar: bool = False,
        leap: bool = False,
        direct_input: bool = False,
        start_year: int = 1850,
        end_year: int = 2030
    ) -> BaziResult:
        """
        执行八字计算
        
        Args:
            year: 年
            month: 月
            day: 日
            time: 时（0-23）
            female: 是否女命
            lunar: 是否农历输入
            leap: 是否闰月
            direct_input: 直接输入八字
            start_year: 起始年份（用于八字反查）
            end_year: 结束年份
        
        Returns:
            BaziResult: 完整计算结果
        """
        input_params = BaziInput(
            year=year, month=month, day=day, time=time,
            female=female, lunar=lunar, leap=leap,
            direct_input=direct_input
        )
        
        # 1. 获取公历/农历转换
        if direct_input:
            # 直接输入八字模式（需要使用 sxtwl 进行八字反查）
            solar, lunar = self._direct_input_bazi(year, month, day, time, start_year, end_year)
        else:
            solar, lunar = self._get_lunar(year, month, day, time, lunar, leap)
        
        # 2. 获取八字核心四柱
        ba = lunar.getEightChar()
        gans = namedtuple("Gans", "year month day time")(
            year=ba.getYearGan(),
            month=ba.getMonthGan(),
            day=ba.getDayGan(),
            time=ba.getTimeGan()
        )
        zhis = namedtuple("Zhis", "year month day time")(
            year=ba.getYearZhi(),
            month=ba.getMonthZhi(),
            day=ba.getDayZhi(),
            time=ba.getTimeZhi()
        )
        me = gans.day
        month_zhi = zhis.month
        
        # 3. 计算十神
        gan_shens = self._calc_gan_shens(gans, me)
        zhi_shens = self._calc_zhi_shens(zhis, me)
        zhi_shen3 = self._calc_zhi_shen3(zhis, me)
        
        # 4. 计算五行分数
        scores = self._calc_wuxing_scores(gans, zhis)
        gan_scores = self._calc_gan_scores(gans, zhis)
        
        # 5. 计算八字强弱
        strong, weak = self._calc_strength(gans, zhis, me, gan_scores)
        
        # 6. 计算调候
        temps_score, humidity = self._calc_temps(gans, zhis, me)
        
        # 7. 计算拱
        gong = self._calc_gong(zhis)
        
        # 8. 计算关系
        zhi_6he = self._calc_zhi_6he(zhis)
        zhi_6chong = self._calc_zhi_6chong(zhis)
        gan_he = self._calc_gan_he(gans)
        zhi_xing = self._calc_zhi_xing(zhis)
        
        # 9. 计算大运
        direction = self._calc_direction(gans, female)
        yun = ba.getYun(not female)
        dayuns = self._calc_dayuns(yun, gans, zhis, me, direction)
        
        # 10. 计算神煞
        all_shens, column_shens = self._calc_shens(gans, zhis, me)
        
        # 11. 计算格局和局
        all_ges, jus = self._calc_ges_and_ju(gans, zhis, me, month_zhi, zhi_shen3)
        
        # 12. 组装结果
        sex = '女' if female else '男'
        ming_gong = ba.getMingGong()
        tai_yuan = ba.getTaiYuan()
        shen_gong = ba.getShenGong()
        
        zhus = list(zip(gans, zhis))
        
        result = BaziResult(
            sex=sex,
            solar=f"{solar.getYear()}年{solar.getMonth()}月{solar.getDay()}日",
            lunar=f"{lunar.getYear()}年{lunar.getMonth()}月{lunar.getDay()}日",
            ming_gong=ming_gong,
            tai_yuan=tai_yuan,
            shen_gong=shen_gong,
            gans=gans,
            zhis=zhis,
            me=me,
            month_zhi=month_zhi,
            gan_shens=list(gan_shens),
            zhi_shens=list(zhi_shens),
            zhi_shen3=zhi_shen3,
            zhus=zhus,
            scores=scores,
            gan_scores=gan_scores,
            strong=strong,
            weak=weak,
            temps_score=temps_score,
            humidity=humidity,
            gong=gong,
            zhi_6he=zhi_6he,
            zhi_6chong=zhi_6chong,
            gan_he=gan_he,
            zhi_xing=zhi_xing,
            dayuns=dayuns,
            all_shens=all_shens,
            column_shens=column_shens,
            all_ges=all_ges,
            jus=jus
        )
        
        return result
    
    def _get_lunar(self, year: int, month: int, day: int, time: int, 
                   lunar: bool, leap: bool) -> Tuple[Any, Any]:
        """获取公历和农历"""
        from lunar_python import Solar, Lunar
        
        if lunar:
            month_ = -month if leap else month
            lunar_obj = Lunar.fromYmdHms(year, month_, day, time, 0, 0)
            solar = lunar_obj.getSolar()
        else:
            solar = Solar.fromYmdHms(year, month, day, time, 0, 0)
            lunar_obj = solar.getLunar()
        
        return solar, lunar_obj
    
    def _calc_gan_shens(self, gans: namedtuple, me: str) -> List[str]:
        """计算天干十神"""
        result = []
        for i, gan in enumerate(gans):
            if i == 2:
                result.append('--')  # 日干自己
            else:
                result.append(self.ten_deities[me][gan])
        return result
    
    def _calc_zhi_shens(self, zhis: namedtuple, me: str) -> List[str]:
        """计算地支主气十神"""
        result = []
        for zhi in zhis:
            d = self.zhi5[zhi]
            main_gan = max(d, key=d.get)
            result.append(self.ten_deities[me][main_gan])
        return result
    
    def _calc_zhi_shen3(self, zhis: namedtuple, me: str) -> List[List[str]]:
        """计算地支所有十神（含余气）"""
        result = []
        for zhi in zhis:
            shens = []
            for gan in self.zhi5_list[zhi]:
                shens.append(self.ten_deities[me][gan])
            result.append(shens)
        return result
    
    def _calc_wuxing_scores(self, gans: namedtuple, zhis: namedtuple) -> Dict[str, int]:
        """计算五行分数"""
        scores = {"金": 0, "木": 0, "水": 0, "火": 0, "土": 0}
        for gan in gans:
            scores[self.gan5[gan]] += 5
        # zhis.month -> zhis[1] (月支)
        for zhi in list(zhis) + [zhis[1]]:
            for gan in self.zhi5[zhi]:
                scores[self.gan5[gan]] += self.zhi5[zhi][gan]
        return scores
    
    def _calc_gan_scores(self, gans: namedtuple, zhis: namedtuple) -> Dict[str, int]:
        """计算天干分数"""
        gan_scores = {gan: 0 for gan in self.Gan}
        for gan in gans:
            gan_scores[gan] += 5
        # zhis.month -> zhis[1] (月支)
        for zhi in list(zhis) + [zhis[1]]:
            for gan in self.zhi5[zhi]:
                gan_scores[gan] += self.zhi5[zhi][gan]
        return gan_scores
    
    def _calc_strength(self, gans: namedtuple, zhis: namedtuple, me: str,
                      gan_scores: Dict[str, int]) -> Tuple[int, bool]:
        """计算八字强弱"""
        # me 是日干（如 '甲'），me_attrs 是 ten_deities[me]（一个 bidict）
        me_attrs = self.ten_deities[me]
        me_attrs_inv = me_attrs.inverse  # inverse bidict：十神名 -> 天干
        
        # 强根（从 inverse bidict 获取正确的天干）
        strong = gan_scores[me_attrs_inv.get('比', '')] + gan_scores[me_attrs_inv.get('劫', '')] \
            + gan_scores[me_attrs_inv.get('枭', '')] + gan_scores[me_attrs_inv.get('印', '')]
        
        # 弱判断
        me_status = [self.ten_deities[me][zhi] for zhi in zhis]
        weak = True
        for status in me_status:
            if status in ('长', '帝', '建'):
                weak = False
                break
        
        # 比劫多也可能强
        if weak and me_status.count('比') + me_status.count('库') > 2:
            weak = False
        
        return strong, weak
    
    def _calc_temps(self, gans: namedtuple, zhis: namedtuple, me: str) -> Tuple[int, int]:
        """计算调候和湿度"""
        temps_score = (
            self.temps[gans.year] + self.temps[gans.month] +
            self.temps[me] + self.temps[gans.time] +
            self.temps[zhis.year] + self.temps[zhis.month] * 2 +
            self.temps[zhis.day] + self.temps[zhis.time]
        )
        humidity = temps_score
        return temps_score, humidity
    
    def _calc_gong(self, zhis: namedtuple) -> List[str]:
        """计算拱"""
        result = []
        for i in range(3):
            zhi1, zhi2 = zhis[i], zhis[i+1]
            if abs(self.Zhi.index(zhi1) - self.Zhi.index(zhi2)) == 2:
                value = self.Zhi[(self.Zhi.index(zhi1) + self.Zhi.index(zhi2)) // 2]
                result.append(value)
            if (zhi1 + zhi2 in self.gong_he) and (self.gong_he[zhi1 + zhi2] not in list(zhis)):
                result.append(self.gong_he[zhi1 + zhi2])
        return result
    
    def _calc_zhi_6he(self, zhis: namedtuple) -> List[bool]:
        """计算地支六合"""
        result = [False, False, False, False]
        for i in range(3):
            if self.zhi_atts[zhis[i]]['六'] == zhis[i+1]:
                result[i] = result[i+1] = True
        return result
    
    def _calc_zhi_6chong(self, zhis: namedtuple) -> List[bool]:
        """计算地支六冲"""
        result = [False, False, False, False]
        for i in range(3):
            if self.zhi_atts[zhis[i]]['冲'] == zhis[i+1]:
                result[i] = result[i+1] = True
        return result
    
    def _calc_gan_he(self, gans: namedtuple) -> List[bool]:
        """计算干合
        
        gan_hes 是 dict: {('甲', '己'): '中正之合...', ...}
        检查天干对是否在 gan_hes 的 keys 中
        """
        from .bazi_data import BD
        gan_hes = BD.gan_hes()
        
        result = [False, False, False, False]
        for i in range(3):
            key = (gans[i], gans[i+1])
            if key in gan_hes or (gans[i+1], gans[i]) in gan_hes:
                result[i] = result[i+1] = True
        return result
    
    def _calc_zhi_xing(self, zhis: namedtuple) -> List[bool]:
        """计算地支相刑"""
        result = [False, False, False, False]
        for i in range(3):
            if (self.zhi_atts[zhis[i]]['刑'] == zhis[i+1] or 
                self.zhi_atts[zhis[i+1]]['刑'] == zhis[i]):
                result[i] = result[i+1] = True
        return result
    
    def _calc_direction(self, gans: namedtuple, female: bool) -> int:
        """计算大运方向"""
        seq = self.Gan.index(gans.year)
        if female:
            return -1 if seq % 2 == 0 else 1
        else:
            return 1 if seq % 2 == 0 else -1
    
    def _direct_input_bazi(self, year_gz: str, month_gz: str, day_gz: str, time_gz: str,
                          start_year: int, end_year: int) -> Tuple[Any, Any]:
        """直接输入八字模式：根据八字反查出生年份
        
        Args:
            year_gz: 年柱完整干支，如 '庚午'
            month_gz: 月柱完整干支，如 '己卯'
            day_gz: 日柱完整干支，如 '己卯'
            time_gz: 时柱完整干支，如 '甲戌'
        """
        import sxtwl
        from lunar_python import Solar, Lunar
        from ganzhi import getGZ
        
        try:
            # 反查可能的时间
            jds = sxtwl.siZhu2Year(
                getGZ(year_gz),
                getGZ(month_gz),
                getGZ(day_gz),
                getGZ(time_gz),
                start_year,
                end_year
            )
            
            if jds:
                t = sxtwl.JD2DD(jds[0])
                solar = Solar.fromYmdHms(int(t.Y), int(t.M), int(t.D), int(t.h), int(t.m), 0)
                lunar = solar.getLunar()
                return solar, lunar
            else:
                raise ValueError("未找到匹配的出生时间")
        except ValueError:
            raise  # 直接重新抛出 ValueError
        except Exception as e:
            raise ValueError(f"八字反查失败: {type(e).__name__}: {e}") from e
    
    def _calc_dayuns(self, yun, gans: namedtuple, zhis: namedtuple,
                     me: str, direction: int) -> List[Dayun]:
        """计算大运
        
        使用 lunar_python 的 yun.getDaYun() 获取详细信息
        """
        from .bazi_data import BD
        
        gan5 = BD.gan5()
        zhi5 = BD.zhi5()
        empties = BD.empties()
        nayins = BD.nayins()
        
        dayuns = []
        
        # 如果有 yun 对象，使用 lunar_python 的 DaYun
        if yun:
            try:
                for dayun in yun.getDaYun()[1:]:  # 跳过第一个（当前大运）
                    gz = dayun.getGanZhi()
                    if not gz:
                        continue
                    
                    gan_ = gz[0]
                    zhi_ = gz[1]
                    age = dayun.getStartAge()
                    year = dayun.getStartYear()
                    
                    # 计算大运地支关系
                    zhi_relations = set()
                    for item in zhis:
                        for type_ in self.zhi_atts[zhi_]:
                            if item in self.zhi_atts[zhi_][type_]:
                                zhi_relations.add(f"{type_}:{item}")
                    
                    # 检查空亡
                    empty = ''
                    key = (gan5[gans[0]], zhis[2])
                    if key in empties and zhi_ in empties[key]:
                        empty = '空'
                    
                    # 计算夹拱
                    jia = ''
                    for i in range(4):
                        if gan_ == gans[i]:
                            if abs(self.Zhi.index(zhi_) - self.Zhi.index(zhis[i])) == 2:
                                jia = f"  --夹:{self.Zhi[(self.Zhi.index(zhi_) + self.Zhi.index(zhis[i])) // 2]}"
                    
                    # 大运藏干详情
                    zhi5_detail = ''
                    for gan in zhi5[zhi_]:
                        zhi5_detail += f"{gan}{self.ten_deities[me][gan]}　"
                    
                    # 福德
                    fu = '*' if (gan_, zhi_) in list(zip(gans, zhis)) else ''
                    
                    # 纳音
                    nayin = nayins.get((gan_, zhi_), '')
                    
                    dayun_obj = Dayun(
                        age=age,
                        start_year=year,
                        ganzhi=gz,
                        gan_shens=self.ten_deities[me][gan_],
                        zhi_shens=self.ten_deities[me][zhi_],
                        zhi5_detail=zhi5_detail.strip(),
                        relations='  '.join(zhi_relations),
                        empty=empty,
                        fu=fu,
                        nayin=nayin,
                        shens=jia
                    )
                    dayuns.append(dayun_obj)
            except Exception:
                # 回退到简化版
                dayuns = self._calc_dayuns_simple(gans, zhis, me, direction)
        else:
            # 回退到简化版
            dayuns = self._calc_dayuns_simple(gans, zhis, me, direction)
        
        return dayuns
    
    def _calc_dayuns_simple(self, gans: namedtuple, zhis: namedtuple,
                           me: str, direction: int) -> List[Dayun]:
        """简化版大运计算"""
        dayuns = []
        gan_seq = self.Gan.index(gans.month)
        zhi_seq = self.Zhi.index(zhis.month)
        
        for i in range(12):
            gan_seq += direction
            zhi_seq += direction
            dayun_gan = self.Gan[gan_seq % 10]
            dayun_zhi = self.Zhi[zhi_seq % 12]
            
            dayun = Dayun(
                age=i + 1,
                start_year=0,
                ganzhi=f"{dayun_gan}{dayun_zhi}",
                gan_shens=self.ten_deities[me][dayun_gan],
                zhi_shens=self.ten_deities[me][dayun_zhi],
                zhi5_detail="",
                relations="",
                empty="",
                fu="",
                nayin="",
                shens=""
            )
            dayuns.append(dayun)
        
        return dayuns
    
    def _calc_shens(self, gans: namedtuple, zhis: namedtuple, me: str) -> Tuple[List[str], tuple]:
        """计算神煞"""
        all_shens = set()
        strs = ["", "", "", ""]
        
        # 年煞
        for shen, zhi_map in self.year_shens.items():
            for i in (1, 2, 3):
                if zhis[i] in zhi_map.get(zhis[i], []):
                    strs[i] = shen if not strs[i] else strs[i] + "　" + shen
                    all_shens.add(shen)
        
        # 月煞
        for shen, zhi_map in self.month_shens.items():
            for i in range(4):
                if gans[i] in zhi_map.get(zhis[i], []) or zhis[i] in zhi_map.get(zhis[i], []):
                    strs[i] = shen if not strs[i] else strs[i] + "　" + shen
                    if i == 2 and gans[i] in zhi_map.get(zhis[i], []):
                        strs[i] += "●"
                    all_shens.add(shen)
        
        # 日煞
        for shen, zhi_map in self.day_shens.items():
            for i in (0, 1, 3):
                if zhis[i] in zhi_map.get(zhis[i], []):
                    strs[i] = shen if not strs[i] else strs[i] + "　" + shen
                    all_shens.add(shen)
        
        # 时煞
        for shen, zhi_map in self.g_shens.items():
            for i in range(4):
                if zhis[i] in zhi_map.get(me, []):
                    strs[i] = shen if not strs[i] else strs[i] + "　" + shen
                    all_shens.add(shen)
        
        return sorted(all_shens), tuple(strs)
    
    def _calc_ges_and_ju(self, gans: namedtuple, zhis: namedtuple, me: str,
                        month_zhi: str, zhi_shen3: List[List[str]]) -> Tuple[List[str], List[str]]:
        """计算格局和局"""
        all_ges = []
        jus = []
        
        # 三合局
        zhis_g = set(list(zhis))
        for item in self.zhi_hes:
            if set(item).issubset(zhis_g):
                jus.append(item)
        
        # 三会局
        for item in self.zhi_huis:
            if set(item).issubset(zhis_g):
                jus.append(item)
        
        # 格局判定（简化版）
        zhi_main_shens = [self.ten_deities[me][max(self.zhi5[z], key=self.zhi5[z].get)] for z in zhis]
        
        # 成格的十神
        for i, shen in enumerate(zhi_shen3):
            if i in (1, 2, 3) and shen:
                if shen[0] not in ('比', '劫'):
                    all_ges.append(shen[0])
        
        return all_ges, jus


# ============================================================
# 全局实例
# ============================================================

_calculator = None

def get_calculator() -> BaziCalculator:
    """获取计算器实例"""
    global _calculator
    if _calculator is None:
        _calculator = BaziCalculator()
    return _calculator