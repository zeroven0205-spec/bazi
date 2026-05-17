# -*- coding: utf-8 -*-
"""
bazi_calc.liunian - 流年详细计算
计算每个流年的详细运势信息

用法:
    from bazi_calc import BaziCalculator
    from bazi_calc.liunian import calculate_liunians
    
    result = BaziCalculator().calculate(1990, 3, 15, 19)
    liunians = calculate_liunians(result)
    for ln in liunians:
        print(f"{ln.year}年: {ln.ganzhi}")
"""

from typing import List, Dict, Any, Tuple

from .types import Liunian, BaziResult
from .bazi_data import BD


# ============================================================
# 流年计算器
# ============================================================

class LiunianCalculator:
    """
    流年计算器
    
    用法:
        from bazi_calc import BaziCalculator
        from bazi_calc.liunian import LiunianCalculator
        
        result = BaziCalculator().calculate(1990, 3, 15, 19)
        calc = LiunianCalculator(result)
        liunians = calc.calculate(start_year=2020, end_year=2030)
    """
    
    def __init__(self, result: BaziResult):
        self.result = result
        self.Gan = BD.Gan()
        self.Zhi = BD.Zhi()
        self.gan5 = BD.gan5()
        self.zhi5 = BD.zhi5()
        self.ten_deities = BD.ten_deities()
        self.zhi_atts = BD.zhi_atts()
        self.empties = BD.empties()
        self.nayins = BD.nayins()
        
        # 提取基本变量
        self.gans = list(result.gans)
        self.zhis = list(result.zhis)
        self.zhus = list(zip(self.gans, self.zhis))
        self.me = result.me
    
    def calculate(self, start_year: int = 2020, end_year: int = 2030,
                 direction: int = 1) -> List[Liunian]:
        """
        计算指定年份范围内的流年
        
        Args:
            start_year: 起始年份
            end_year: 结束年份
            direction: 大运方向 (1 或 -1)
        
        Returns:
            List[Liunian]: 流年列表
        """
        liunians = []
        gan_seq = self.Gan.index(self.gans[1])  # 从月干开始
        zhi_seq = self.Zhi.index(self.zhis[1])  # 从月支开始
        
        year = start_year
        while year <= end_year:
            # 计算流年干支
            gan_seq += direction
            zhi_seq += direction
            gan_ = self.Gan[gan_seq % 10]
            zhi_ = self.Zhi[zhi_seq % 12]
            ganzhi = f"{gan_}{zhi_}"
            
            # 计算年龄（相对于出生年）
            birth_year = int(self.result.solar[:4])
            age = year - birth_year + 1  # 虚岁
            
            # 计算流年地支关系
            zhi_relations = self._calc_zhi_relations(zhi_)
            
            # 检查空亡
            empty = self._check_empty(zhi_)
            
            # 计算藏干详情
            zhi5_detail = self._calc_zhi5_detail(zhi_)
            
            # 计算十神
            gan_shens = self.ten_deities[self.me][gan_]
            zhi_shens = self.ten_deities[self.me][zhi_]
            
            # 纳音
            nayin = self.nayins.get((gan_, zhi_), '')
            
            # 福德标记
            fu = '*' if (gan_, zhi_) in self.zhus else ''
            
            # 流年神煞（简化版）
            shens = self._calc_shens(gan_, zhi_)
            
            # 检查四柱特殊组合
            all_zhis = set(self.zhis) | {zhi_}
            special = self._check_special_combinations(all_zhis)
            
            liunian = Liunian(
                age=age,
                year=year,
                ganzhi=ganzhi,
                gan_shens=gan_shens,
                zhi_shens=zhi_shens,
                zhi5_detail=zhi5_detail,
                relations=zhi_relations,
                empty=empty,
                fu=fu,
                nayin=nayin,
                shens=shens,
                special=special
            )
            liunians.append(liunian)
            
            year += 1
        
        return liunians
    
    def calculate_from_dayun(self, dayun_index: int = 0, 
                            count: int = 10) -> List[Liunian]:
        """
        从指定大运开始计算流年
        
        Args:
            dayun_index: 大运索引（0=当前大运）
            count: 流年数量
        
        Returns:
            List[Liunian]: 流年列表
        """
        if not self.result.dayuns or dayun_index >= len(self.result.dayuns):
            return []
        
        dayun = self.result.dayuns[dayun_index]
        start_year = dayun.start_year
        
        # 根据大运干支确定方向
        dayun_gan = dayun.ganzhi[0]
        dayun_zhi = dayun.ganzhi[1]
        
        # 判断方向：阳顺阴逆
        if self.Gan.index(dayun_gan) % 2 == 0:
            direction = 1
        else:
            direction = -1
        
        return self.calculate(start_year, start_year + count - 1, direction)
    
    def _calc_zhi_relations(self, zhi_: str) -> str:
        """计算地支关系"""
        relations = set()
        for item in self.zhis:
            for type_ in self.zhi_atts[item]:
                if zhi_ in self.zhi_atts[item][type_]:
                    relations.add(f"{type_}:{item}")
        return '  '.join(sorted(relations))
    
    def _check_empty(self, zhi_: str) -> str:
        """检查空亡"""
        key = (self.gan5[self.gans[0]], self.zhis[2])
        if key in self.empties and zhi_ in self.empties[key]:
            return '空'
        return ''
    
    def _calc_zhi5_detail(self, zhi_: str) -> str:
        """计算藏干详情"""
        detail = ''
        for gan in self.zhi5[zhi_]:
            detail += f"{gan}{self.ten_deities[self.me][gan]}　"
        return detail.strip()
    
    def _calc_shens(self, gan_: str, zhi_: str) -> str:
        """计算流年神煞（简化版）"""
        shens = []
        
        # 太岁关系
        if zhi_ == self.zhis[0]:
            shens.append("值太岁")
        
        # 冲太岁
        if self.zhi_atts[self.zhis[0]].get('冲') == zhi_:
            shens.append("冲太岁")
        
        # 三会
        all_zhis = set(self.zhis) | {zhi_}
        if set('寅申巳亥').issubset(all_zhis):
            shens.append("四生")
        if set('子午卯酉').issubset(all_zhis):
            shens.append("四败")
        if set('辰戌丑未').issubset(all_zhis):
            shens.append("四库")
        
        # 天罗地网
        if set('戌亥辰巳').issubset(all_zhis):
            shens.append("天罗地网")
        
        return ' '.join(shens)
    
    def _check_special_combinations(self, all_zhis: set) -> str:
        """检查特殊组合"""
        special = []
        
        if set('寅申巳亥').issubset(all_zhis):
            special.append("四生")
        if set('子午卯酉').issubset(all_zhis):
            special.append("四败")
        if set('辰戌丑未').issubset(all_zhis):
            special.append("四库")
        if set('戌亥辰巳').issubset(all_zhis):
            special.append("天罗地网")
        
        return ' '.join(special)


# ============================================================
# 流年运势解读
# ============================================================

class LiunianReader:
    """
    流年运势解读
    
    用法:
        from bazi_calc import BaziCalculator
        from bazi_calc.liunian import LiunianReader
        
        result = BaziCalculator().calculate(1990, 3, 15, 19)
        reader = LiunianReader(result)
        
        # 获取 2025 年流年
        prediction = reader.predict_year(2025)
        print(prediction['summary'])
    """
    
    def __init__(self, result: BaziResult):
        self.result = result
        self.me = result.me
        self.ten_deities = BD.ten_deities()
        self.gan5 = BD.gan5()
        
        # 五行生克关系
        self.wuxing_cycle = {
            '木': {'生': '火', '克': '土'},
            '火': {'生': '土', '克': '金'},
            '土': {'生': '金', '克': '水'},
            '金': {'生': '水', '克': '木'},
            '水': {'生': '木', '克': '火'},
        }
    
    def predict_year(self, year: int) -> Dict[str, Any]:
        """
        预测指定年份的运势
        
        Args:
            year: 年份
        
        Returns:
            Dict: 包含运势预测的字典
        """
        from bazi_calc.liunian import LiunianCalculator
        
        calc = LiunianCalculator(self.result)
        liunians = calc.calculate(year, year)
        
        if not liunians:
            return {'error': '无法计算该年份流年'}
        
        liunian = liunians[0]
        
        # 计算运势
        prediction = {
            'year': year,
            'age': liunian.age,
            'ganzhi': liunian.ganzhi,
            'gan': liunian.ganzhi[0],
            'zhi': liunian.ganzhi[1],
            'gan_shens': liunian.gan_shens,
            'zhi_shens': liunian.zhi_shens,
            'nayin': liunian.nayin,
            'relations': liunian.relations,
            'empty': liunian.empty,
            'special': liunian.special,
            'summary': '',
            'advice': [],
            'lucky': [],
            'unlucky': []
        }
        
        # 生成运势总结
        prediction['summary'] = self._generate_summary(prediction)
        prediction['advice'] = self._generate_advice(prediction)
        
        return prediction
    
    def _generate_summary(self, pred: Dict) -> str:
        """生成运势总结"""
        parts = []
        
        # 流年十神
        if pred['gan_shens'] == '官':
            parts.append("流年遇正官：事业有成，运势上升")
        elif pred['gan_shens'] == '杀':
            parts.append("流年遇七杀：挑战与机遇并存")
        elif pred['gan_shens'] == '财':
            parts.append("流年遇正财：财运稳定，适宜守成")
        elif pred['gan_shens'] == '才':
            parts.append("流年遇偏财：有意外之财")
        elif pred['gan_shens'] == '印':
            parts.append("流年遇正印：学业进步，贵人相助")
        elif pred['gan_shens'] == '枭':
            parts.append("流年遇偏印：需防小人")
        elif pred['gan_shens'] == '食':
            parts.append("流年遇食神：才华展现，有口福")
        elif pred['gan_shens'] == '伤':
            parts.append("流年遇伤官：创意丰富，但需注意表达")
        elif pred['gan_shens'] == '比':
            parts.append("流年遇比肩：合作共赢，人际活跃")
        elif pred['gan_shens'] == '劫':
            parts.append("流年遇劫财：需防盗破财")
        
        # 纳音五行
        if pred['nayin']:
            parts.append(f"纳音{pred['nayin']}")
        
        # 特殊组合
        if pred['special']:
            parts.append(f"命局组合：{pred['special']}")
        
        # 空亡
        if pred['empty']:
            parts.append(f"注意：{pred['empty']}")
        
        return '。'.join(parts)
    
    def _generate_advice(self, pred: Dict) -> List[str]:
        """生成运势建议"""
        advice = []
        
        me_wx = self.gan5[self.me]
        
        # 流年天干五行
        gan_wx = self.gan5[pred['gan']]
        
        # 相生相克分析
        if self.wuxing_cycle[me_wx].get('生') == gan_wx:
            advice.append("天干相生：贵人运强，适宜拓展")
        elif self.wuxing_cycle[me_wx].get('克') == gan_wx:
            advice.append("天干相克：需谨慎行事，避免冲突")
        elif self.wuxing_cycle[gan_wx].get('克') == me_wx:
            advice.append("天干被克：压力较大，需顶住压力")
        
        # 特殊年份建议
        if '冲太岁' in pred['special']:
            advice.append("犯太岁：低调行事，注意安全")
        if '空' in pred['empty']:
            advice.append("逢空亡：不宜冒险，稳扎稳打")
        
        return advice


# ============================================================
# 便捷函数
# ============================================================

def calculate_liunians(result: BaziResult, start_year: int = 2020, 
                       end_year: int = 2030) -> List[Liunian]:
    """
    便捷流年计算函数
    
    用法:
        from bazi_calc import BaziCalculator
        from bazi_calc.liunian import calculate_liunians
        
        result = BaziCalculator().calculate(1990, 3, 15, 19)
        liunians = calculate_liunians(result, 2020, 2030)
        for ln in liunians:
            print(f"{ln.year}年({ln.age}岁): {ln.ganzhi}")
    """
    return LiunianCalculator(result).calculate(start_year, end_year)


def predict_liunian(result: BaziResult, year: int) -> Dict[str, Any]:
    """
    便捷流年运势预测函数
    
    用法:
        from bazi_calc import BaziCalculator
        from bazi_calc.liunian import predict_liunian
        
        result = BaziCalculator().calculate(1990, 3, 15, 19)
        pred = predict_liunian(result, 2025)
        print(pred['summary'])
    """
    return LiunianReader(result).predict_year(year)