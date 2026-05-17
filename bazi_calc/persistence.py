# -*- coding: utf-8 -*-
"""
bazi_calc.persistence - 导出/导入功能
支持将八字结果导出为 JSON 或从 JSON 导入

用法:
    from bazi_calc import BaziCalculator
    from bazi_calc.persistence import export_json, import_json
    
    # 导出
    result = BaziCalculator().calculate(1990, 3, 15, 19)
    export_json(result, 'bazi_result.json')
    
    # 导入
    result = import_json('bazi_result.json')
"""

import json
from typing import Dict, Any, Optional
from pathlib import Path

from .types import BaziResult, Dayun, Liunian


# ============================================================
# 序列化/反序列化
# ============================================================

def dayun_to_dict(dayun: Dayun) -> Dict[str, Any]:
    """将 Dayun 转换为字典"""
    return {
        'age': dayun.age,
        'start_year': dayun.start_year,
        'ganzhi': dayun.ganzhi,
        'gan_shens': dayun.gan_shens,
        'zhi_shens': dayun.zhi_shens,
        'zhi5_detail': dayun.zhi5_detail,
        'relations': dayun.relations,
        'empty': dayun.empty,
        'fu': dayun.fu,
        'nayin': dayun.nayin,
        'shens': dayun.shens
    }


def dict_to_dayun(d: Dict[str, Any]) -> Dayun:
    """将字典转换为 Dayun"""
    return Dayun(
        age=d['age'],
        start_year=d.get('start_year', 0),
        ganzhi=d['ganzhi'],
        gan_shens=d['gan_shens'],
        zhi_shens=d['zhi_shens'],
        zhi5_detail=d.get('zhi5_detail', ''),
        relations=d.get('relations', ''),
        empty=d.get('empty', ''),
        fu=d.get('fu', ''),
        nayin=d.get('nayin', ''),
        shens=d.get('shens', '')
    )


def result_to_dict(result: BaziResult, include_mingli: bool = True) -> Dict[str, Any]:
    """将 BaziResult 转换为字典"""
    data = {
        'version': '2.1',
        'meta': {
            'sex': result.sex,
            'solar': result.solar,
            'lunar': result.lunar,
            'ming_gong': result.ming_gong,
            'tai_yuan': result.tai_yuan,
            'shen_gong': result.shen_gong
        },
        'bazi': {
            'gans': list(result.gans),
            'zhis': list(result.zhis),
            'gan_shens': result.gan_shens,
            'zhi_shens': result.zhi_shens,
            'zhi_shen3': result.zhi_shen3,
            'zhus': [list(z) for z in result.zhus]
        },
        'analysis': {
            'me': result.me,
            'month_zhi': result.month_zhi,
            'strong': result.strong,
            'weak': result.weak,
            'scores': dict(result.scores),
            'gan_scores': dict(result.gan_scores),
            'temps_score': result.temps_score,
            'humidity': result.humidity
        },
        'relations': {
            'gong': result.gong,
            'zhi_6he': result.zhi_6he,
            'zhi_6chong': result.zhi_6chong,
            'gan_he': result.gan_he,
            'zhi_xing': result.zhi_xing
        },
        'dayuns': [dayun_to_dict(d) for d in result.dayuns],
        'ges': result.all_ges,
        'jus': result.jus,
        'all_shens': result.all_shens,
        'column_shens': list(result.column_shens)
    }
    
    return data


def dict_to_result(data: Dict[str, Any]) -> BaziResult:
    """将字典转换为 BaziResult"""
    from collections import namedtuple
    
    Gans = namedtuple('Gans', 'year month day time')
    Zhis = namedtuple('Zhis', 'year month day time')
    
    bazi = data['bazi']
    analysis = data['analysis']
    
    result = BaziResult(
        sex=data['meta']['sex'],
        solar=data['meta']['solar'],
        lunar=data['meta']['lunar'],
        ming_gong=data['meta'].get('ming_gong', ''),
        tai_yuan=data['meta'].get('tai_yuan', ''),
        shen_gong=data['meta'].get('shen_gong', ''),
        gans=Gans(*bazi['gans']),
        zhis=Zhis(*bazi['zhis']),
        me=analysis['me'],
        month_zhi=analysis['month_zhi'],
        gan_shens=bazi['gan_shens'],
        zhi_shens=bazi['zhi_shens'],
        zhi_shen3=bazi['zhi_shen3'],
        zhus=[tuple(z) for z in bazi['zhus']],
        scores=analysis['scores'],
        gan_scores=analysis['gan_scores'],
        strong=analysis['strong'],
        weak=analysis['weak'],
        temps_score=analysis.get('temps_score', 0),
        humidity=analysis.get('humidity', 0),
        gong=data['relations']['gong'],
        zhi_6he=data['relations']['zhi_6he'],
        zhi_6chong=data['relations']['zhi_6chong'],
        gan_he=data['relations']['gan_he'],
        zhi_xing=data['relations']['zhi_xing'],
        dayuns=[dict_to_dayun(d) for d in data['dayuns']],
        all_shens=data['all_shens'],
        column_shens=tuple(data['column_shens']),
        all_ges=data['ges'],
        jus=data['jus']
    )
    
    return result


# ============================================================
# 导出函数
# ============================================================

def export_json(result: BaziResult, filepath: str, 
               include_mingli: bool = False) -> str:
    """
    导出八字结果为 JSON 文件
    
    用法:
        from bazi_calc import BaziCalculator
        from bazi_calc.persistence import export_json
        
        result = BaziCalculator().calculate(1990, 3, 15, 19)
        export_json(result, 'bazi_result.json')
    """
    data = result_to_dict(result, include_mingli)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    return filepath


def to_json(result: BaziResult) -> str:
    """
    将八字结果转换为 JSON 字符串
    
    用法:
        from bazi_calc import BaziCalculator
        from bazi_calc.persistence import to_json
        
        result = BaziCalculator().calculate(1990, 3, 15, 19)
        json_str = to_json(result)
    """
    data = result_to_dict(result)
    return json.dumps(data, ensure_ascii=False, indent=2)


# ============================================================
# 导入函数
# ============================================================

class PersistenceError(Exception):
    """持久化相关错误"""
    pass


def import_json(filepath: str) -> BaziResult:
    """
    从 JSON 文件导入八字结果
    
    用法:
        from bazi_calc.persistence import import_json
        
        result = import_json('bazi_result.json')
    
    Raises:
        PersistenceError: 文件不存在、格式错误或解析失败
    """
    import os
    
    if not os.path.exists(filepath):
        raise PersistenceError(f"文件不存在: {filepath}")
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise PersistenceError(f"JSON 格式错误: {e}") from e
    except IOError as e:
        raise PersistenceError(f"文件读取失败: {e}") from e
    
    try:
        return dict_to_result(data)
    except (KeyError, TypeError, ValueError) as e:
        raise PersistenceError(f"数据解析失败: {e}") from e


def from_json(json_str: str) -> BaziResult:
    """
    从 JSON 字符串导入八字结果
    
    用法:
        from bazi_calc.persistence import from_json
        
        result = from_json(json_string)
    
    Raises:
        PersistenceError: JSON 格式错误或解析失败
    """
    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as e:
        raise PersistenceError(f"JSON 格式错误: {e}") from e
    
    try:
        return dict_to_result(data)
    except (KeyError, TypeError, ValueError) as e:
        raise PersistenceError(f"数据解析失败: {e}") from e


# ============================================================
# CLI 辅助
# ============================================================

def save_result(result: BaziResult, filepath: str, format: str = 'json') -> str:
    """
    保存八字结果到文件
    
    Args:
        result: 八字结果
        filepath: 文件路径
        format: 格式 ('json', 'txt')
    
    Returns:
        保存的文件路径
    """
    filepath = Path(filepath)
    
    if format == 'json':
        return export_json(result, str(filepath))
    elif format == 'txt':
        from .formatter import PlainFormatter
        formatter = PlainFormatter()
        content = formatter.format(result)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return str(filepath)
    else:
        raise ValueError(f"不支持的格式: {format}")