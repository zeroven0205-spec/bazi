# -*- coding: utf-8 -*-
"""
bazi_calc.luohou - 罗喉派（玄空飞星）兼容层
封装 luohou.py 的罗喉派计算逻辑

注意：这是独立的命理系统，与八字不同，使用玄空飞星算法
需要单独运行: python luohou.py -d "2019 6 16"
"""

from typing import Dict, List, Tuple, Any

# 罗喉派核心数据（从 luohou.py 迁移）
YEAR_HOUS = {
    '子': '癸酉', '丑': '甲戌', '寅': '丁亥', '卯': '甲子', '辰': '乙丑',
    '巳': '甲寅', '午': '丁卯', '未': '甲辰', '申': '己巳', '酉': '甲午',
    '戌': '丁未', '亥': '甲申'
}

JI_HOUS = {'春': '乙卯', '夏': '丙午', '秋': '庚申', '冬': '辛酉'}

YUE_HOUS = {
    1: '亥', 2: '子', 3: '丑', 4: '寅', 5: '卯', 6: '辰',
    7: '巳', 8: '午', 9: '未', 10: '申', 11: '酉', 12: '戌'
}

SHI_HOUS = {
    '子': '丑午', '丑': '巳亥', '寅': '寅午', '卯': '辰戌', '辰': '巳丑',
    '巳': '辰戌', '午': '卯申', '未': '午辰', '申': '戌丑', '酉': '子午',
    '戌': '卯午', '亥': '辰卯'
}

FANGWEIS = ['九紫火', '一白水', '二黑土', '三碧木', '四绿木', '五黄土', '六白金', '七赤金', '八白土']

ZHENG_JIUXINGS = {
    1: '八白土', 2: '七赤金', 3: '六白金', 4: '五黄土', 5: '四绿木',
    6: '三碧木', 7: '二黑土', 8: '一白水', 9: '九紫火',
    10: '八白土', 11: '七赤金', 12: '六白金'
}

KU_JIUXINGS = {
    1: '五黄土', 2: '四绿木', 3: '三碧木', 4: '二黑土', 5: '一白水',
    6: '九紫火', 7: '八白土', 8: '七赤金', 9: '六白金',
    10: '五黄土', 11: '四绿木', 12: '三碧木'
}

SHENG_JIUXINGS = {
    1: '二黑土', 2: '一白水', 3: '九紫火', 4: '八白土', 5: '七赤金',
    6: '六白金', 7: '五黄土', 8: '四绿木', 9: '三碧木',
    10: '二黑土', 11: '一白水', 12: '九紫火'
}

JIUXING_NAMES = {
    1: '一白水星（贪狼）',
    2: '二黑土星（巨门）',
    3: '三碧木星（禄存）',
    4: '四绿木星（文曲）',
    5: '五黄土星（廉贞）',
    6: '六白金星（武曲）',
    7: '七赤金星（破军）',
    8: '八白土星（左辅）',
    9: '九紫火星（右弼）'
}

MONTH_FEIXINGS = {
    '子': ZHENG_JIUXINGS, '丑': KU_JIUXINGS, '寅': SHENG_JIUXINGS, '卯': ZHENG_JIUXINGS,
    '辰': KU_JIUXINGS, '巳': SHENG_JIUXINGS, '午': ZHENG_JIUXINGS, '未': KU_JIUXINGS,
    '申': SHENG_JIUXINGS, '酉': ZHENG_JIUXINGS, '戌': KU_JIUXINGS, '亥': SHENG_JIUXINGS
}


# ============================================================
# 罗喉派计算器
# ============================================================

class LuohouCalculator:
    """
    罗喉派（玄空飞星）计算器
    
    用法:
        from bazi_calc.luohou import LuohouCalculator
        
        calc = LuohouCalculator()
        result = calc.calculate(2019, 6, 16)
        print(result)
    """
    
    def __init__(self):
        from lunar_python import Lunar
        self.Lunar = Lunar
        self.zhi_time = {
            '子': '23-1', '丑': '1-3', '寅': '3-5', '卯': '5-7', '辰': '7-9',
            '巳': '9-11', '午': '11-13', '未': '13-15', '申': '15-17', '酉': '17-19',
            '戌': '19-21', '亥': '21-23'
        }
        self.zhi_atts = None  # 需要从 ganzhi 加载
    
    def calculate(self, year: int, month: int, day: int, 
                 include_details: bool = True) -> Dict[str, Any]:
        """
        计算罗喉派信息
        
        Args:
            year: 公历年
            month: 公历月
            day: 公历日
            include_details: 是否包含详细信息
        
        Returns:
            Dict: 包含罗喉派信息的字典
        """
        from lunar_python import Solar, Lunar
        from ganzhi import Gan, Zhi, zhi_atts
        
        self.zhi_atts = zhi_atts
        
        solar = Solar.fromYmdHms(year, month, day, 12, 0, 0)
        lunar = solar.getLunar()
        ba = lunar.getEightChar()
        
        # 获取三柱（不含时柱）
        gans = ba.getYearGan(), ba.getMonthGan(), ba.getDayGan()
        zhis = ba.getYearZhi(), ba.getMonthZhi(), ba.getDayZhi()
        
        result = {
            'date': f'{year}年{month}月{day}日',
            'lunar': f'{lunar.getYear()}年{lunar.getMonth()}月{lunar.getDay()}日',
            'gans': list(gans),
            'zhis': list(zhis),
            'bazi': f'{gans[0]}{zhis[0]} {gans[1]}{zhis[1]} {gans[2]}{zhis[2]}',
            'shi_hou': '',
            'year_hou': '',
            'yue_hou': '',
            'ji_hou': '',
            'jiuxing': '',
            'feixing': []
        }
        
        day_ganzhi = gans[2] + zhis[2]
        
        # 时煞
        for item in SHI_HOUS.get(zhis[2], ''):
            if item in self.zhi_time:
                result['shi_hou'] += f'{item}时({self.zhi_time[item]})'
        
        # 年猴
        if day_ganzhi == YEAR_HOUS.get(zhis[0], ''):
            result['year_hou'] = f'{zhis[0]}年猴:{day_ganzhi}'
        
        # 月罗
        if zhis[2] == YUE_HOUS.get(lunar.getMonth(), ''):
            result['yue_hou'] = f'{zhis[2]}月罗'
        
        # 季猴
        for season, hou in JI_HOUS.items():
            if day_ganzhi == hou:
                result['ji_hou'] = f'{season}猴'
        
        # 九星信息
        month_zhi = zhis[1]
        month_feixing = MONTH_FEIXINGS.get(month_zhi, ZHENG_JIUXINGS)
        result['jiuxing'] = month_feixing.get(lunar.getMonth(), '八白土')
        
        if include_details:
            result['feixing'] = self._get_feixing_details(month_zhi, lunar, day_ganzhi)
        
        return result
    
    def _get_feixing_details(self, month_zhi: str, lunar: Any, day_ganzhi: str) -> List[Dict]:
        """获取飞星详情"""
        details = []
        
        # 九星列表
        for i in range(1, 10):
            pos = self._calc_feixing_position(lunar.getMonth(), i)
            name = JIUXING_NAMES[i]
            details.append({
                'index': i,
                'name': name,
                'position': pos
            })
        
        return details
    
    def _calc_feixing_position(self, month: int, star: int) -> str:
        """计算飞星位置"""
        # 简化版：基于月份计算星宿位置
        positions = ['坎', '坤', '震', '巽', '中', '乾', '兑', '艮', '离']
        idx = (month - star + 9) % 9
        return positions[idx] if idx < 9 else positions[8]


def calculate_luohou(year: int, month: int, day: int) -> Dict[str, Any]:
    """
    便捷罗喉派计算函数
    
    用法:
        from bazi_calc.luohou import calculate_luohou
        
        result = calculate_luohou(2019, 6, 16)
        print(result['bazi'])
        print(result['jiuxing'])
    """
    return LuohouCalculator().calculate(year, month, day)


if __name__ == '__main__':
    import sys
    sys.path.insert(0, '.')
    
    from datetime import datetime
    
    if len(sys.argv) > 1:
        d = datetime.strptime(sys.argv[1], '%Y %m %d')
    else:
        d = datetime.today()
    
    result = calculate_luohou(d.year, d.month, d.day)
    print(f"日期: {result['date']}")
    print(f"农历: {result['lunar']}")
    print(f"三柱: {result['bazi']}")
    print(f"时煞: {result['shi_hou']}")
    print(f"九星: {result['jiuxing']}")