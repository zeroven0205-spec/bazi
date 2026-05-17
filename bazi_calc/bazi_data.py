# -*- coding: utf-8 -*-
"""
bazi_calc.bazi_data - 数据层封装
统一封装对 ganzhi.py, datas.py, yue.py, sizi.py 等数据的访问
"""

from typing import Dict, List, Set, Optional, Tuple, Any
from bidict import bidict

# 延迟导入避免循环依赖
_ganzhi_cache = {}
_datas_cache = {}
_yue_cache = {}
_sizi_cache = {}


def _load_ganzhi():
    """懒加载 ganzhi.py 数据"""
    global _ganzhi_cache
    if not _ganzhi_cache:
        from ganzhi import (
            Gan, Zhi, datouxiu, xiaotouxiu, temps, zhi_time, zhengs, wuhangs,
            ganzhi60, zhi5, zhi5_list, ShX, numCn, Week, jqmc, jis, ymc, rmc,
            ten_deities, ju, shengxiaos, zhi_atts, kus, gan_hes, gan_chongs,
            chongs, zhi_6hes, zhi_3hes, gong_he, zhi_half_3hes, zhi_hes, zhi_huis,
            gong_hui, zhi_chongs, zhi_poes, zhi_haies, zhi_xings, xings, zhi_zixings,
            gan5, zhi_wuhangs, relations, guans, gan_desc, zhi_desc, gan3, gan4,
            zhi3, getGZ, get_jizhu, get_year_of_ganzhi, get_current_year,
            gan_health, mu_years, gan_zangs, zangs, zhi_zangs
        )
        _ganzhi_cache = {
            'Gan': Gan, 'Zhi': Zhi, 'datouxiu': datouxiu, 'xiaotouxiu': xiaotouxiu,
            'temps': temps, 'zhi_time': zhi_time, 'zhengs': zhengs, 'wuhangs': wuhangs,
            'ganzhi60': ganzhi60, 'zhi5': zhi5, 'zhi5_list': zhi5_list,
            'ShX': ShX, 'numCn': numCn, 'Week': Week, 'jqmc': jqmc, 'jis': jis,
            'ymc': ymc, 'rmc': rmc, 'ten_deities': ten_deities, 'ju': ju,
            'shengxiaos': shengxiaos, 'zhi_atts': zhi_atts, 'kus': kus,
            'gan_hes': gan_hes, 'gan_chongs': gan_chongs, 'chongs': chongs,
            'zhi_6hes': zhi_6hes, 'zhi_3hes': zhi_3hes, 'gong_he': gong_he,
            'zhi_half_3hes': zhi_half_3hes, 'zhi_hes': zhi_hes, 'zhi_huis': zhi_huis,
            'gong_hui': gong_hui, 'zhi_chongs': zhi_chongs, 'zhi_poes': zhi_poes,
            'zhi_haies': zhi_haies, 'zhi_xings': zhi_xings, 'xings': xings,
            'zhi_zixings': zhi_zixings, 'gan5': gan5, 'zhi_wuhangs': zhi_wuhangs,
            'relations': relations, 'guans': guans, 'gan_desc': gan_desc,
            'zhi_desc': zhi_desc, 'gan3': gan3, 'gan4': gan4, 'zhi3': zhi3,
            'getGZ': getGZ, 'get_jizhu': get_jizhu, 'gan_health': gan_health,
            'mu_years': mu_years, 'gan_zangs': gan_zangs, 'zangs': zangs,
            'zhi_zangs': zhi_zangs
        }
    return _ganzhi_cache


def _load_datas():
    """懒加载 datas.py 数据"""
    global _datas_cache
    if not _datas_cache:
        from datas import (
            xingxius, jianchus, nayins, empties, shengxiaos, zhi_atts as datas_zhi_atts,
            siling, tiaohous, jins, ges, xiuqius, shens_infos, year_shens,
            month_shens, day_shens, g_shens, tianyis, yutangs, jianlus,
            jianlu_desc, self_zuo, days60, chens
        )
        _datas_cache = {
            'xingxius': xingxius, 'jianchus': jianchus, 'nayins': nayins,
            'empties': empties, 'shengxiaos': shengxiaos, 'zhi_atts': datas_zhi_atts,
            'siling': siling, 'tiaohous': tiaohous, 'jins': jins, 'ges': ges,
            'xiuqius': xiuqius, 'shens_infos': shens_infos, 'year_shens': year_shens,
            'month_shens': month_shens, 'day_shens': day_shens, 'g_shens': g_shens,
            'tianyis': tianyis, 'yutangs': yutangs, 'jianlus': jianlus,
            'jianlu_desc': jianlu_desc, 'self_zuo': self_zuo, 'days60': days60,
            'chens': chens
        }
    return _datas_cache


def _load_yue():
    """懒加载 yue.py 数据"""
    global _yue_cache
    if not _yue_cache:
        from yue import months
        _yue_cache = {'months': months}
    return _yue_cache


def _load_sizi():
    """懒加载 sizi.py 数据"""
    global _sizi_cache
    if not _sizi_cache:
        from sizi import summarys
        _sizi_cache = {'summarys': summarys}
    return _sizi_cache


# ============================================================
# 便捷访问接口
# ============================================================

class BaziData:
    """
    八字数据访问类
    
    用法:
        from bazi_calc.bazi_data import BaziData as BD
        
        gan = BD.Gan
        gan5 = BD.gan5
        ten_deities = BD.ten_deities
        shens_infos = BD.shens_infos
        summarys = BD.summarys
    """
    
    @classmethod
    def _get(cls, module: str, key: str):
        """通用数据获取"""
        if module == 'ganzhi':
            return _load_ganzhi()[key]
        elif module == 'datas':
            return _load_datas()[key]
        elif module == 'yue':
            return _load_yue()[key]
        elif module == 'sizi':
            return _load_sizi()[key]
    
    # ---- ganzhi.py 导出 ----
    @classmethod
    def Gan(cls) -> List[str]:
        return _load_ganzhi()['Gan']
    
    @classmethod
    def Zhi(cls) -> List[str]:
        return _load_ganzhi()['Zhi']
    
    @classmethod
    def gan5(cls) -> Dict[str, str]:
        return _load_ganzhi()['gan5']
    
    @classmethod
    def zhi_wuhangs(cls) -> Dict[str, str]:
        return _load_ganzhi()['zhi_wuhangs']
    
    @classmethod
    def zhi5(cls) -> Dict[str, Any]:
        return _load_ganzhi()['zhi5']
    
    @classmethod
    def zhi5_list(cls) -> Dict[str, List[str]]:
        return _load_ganzhi()['zhi5_list']
    
    @classmethod
    def ten_deities(cls) -> Dict[str, bidict]:
        return _load_ganzhi()['ten_deities']
    
    @classmethod
    def zhi_atts(cls) -> Dict[str, Dict[str, Any]]:
        return _load_ganzhi()['zhi_atts']
    
    @classmethod
    def temps(cls) -> Dict[str, int]:
        return _load_ganzhi()['temps']
    
    @classmethod
    def zhengs(cls) -> str:
        return _load_ganzhi()['zhengs']
    
    @classmethod
    def kus(cls) -> Dict[str, str]:
        return _load_ganzhi()['kus']
    
    @classmethod
    def chongs(cls) -> Dict[str, str]:
        return _load_ganzhi()['chongs']
    
    @classmethod
    def zhi_6hes(cls) -> Dict[str, str]:
        return _load_ganzhi()['zhi_6hes']
    
    @classmethod
    def zhi_3hes(cls) -> Dict[str, str]:
        return _load_ganzhi()['zhi_3hes']
    
    @classmethod
    def gong_he(cls) -> Dict[str, str]:
        return _load_ganzhi()['gong_he']
    
    @classmethod
    def zhi_hes(cls) -> Dict[str, str]:
        return _load_ganzhi()['zhi_hes']
    
    @classmethod
    def zhi_huis(cls) -> Dict[str, str]:
        return _load_ganzhi()['zhi_huis']
    
    @classmethod
    def shengxiaos(cls) -> bidict:
        return _load_ganzhi()['shengxiaos']
    
    @classmethod
    def jianlus(cls) -> Dict[Tuple, str]:
        return _load_ganzhi()['jianlus']
    
    @classmethod
    def jianlu_desc(cls) -> str:
        return _load_ganzhi()['jianlu_desc']
    
    @classmethod
    def self_zuo(cls) -> Dict[str, str]:
        return _load_ganzhi()['self_zuo']
    
    @classmethod
    def get_jizhu(cls, gan: str, zhi: str) -> Dict[str, Any]:
        return _load_ganzhi()['get_jizhu'](gan, zhi)
    
    @classmethod
    def getGZ(cls, gzStr: str):
        return _load_ganzhi()['getGZ'](gzStr)
    
    # ---- datas.py 导出 ----
    @classmethod
    def siling(cls) -> Dict[str, str]:
        return _load_datas()['siling']
    
    @classmethod
    def tiaohous(cls) -> Dict[str, str]:
        return _load_datas()['tiaohous']
    
    @classmethod
    def jins(cls) -> Dict[str, str]:
        return _load_datas()['jins']
    
    @classmethod
    def ges(cls) -> Dict[str, Dict[str, str]]:
        return _load_datas()['ges']
    
    @classmethod
    def xiuqius(cls) -> Dict[str, Dict[str, str]]:
        return _load_datas()['xiuqius']
    
    @classmethod
    def shens_infos(cls) -> Dict[str, str]:
        return _load_datas()['shens_infos']
    
    @classmethod
    def year_shens(cls) -> Dict[str, Dict[str, List[str]]]:
        return _load_datas()['year_shens']
    
    @classmethod
    def month_shens(cls) -> Dict[str, Dict[str, List[str]]]:
        return _load_datas()['month_shens']
    
    @classmethod
    def day_shens(cls) -> Dict[str, Dict[str, List[str]]]:
        return _load_datas()['day_shens']
    
    @classmethod
    def g_shens(cls) -> Dict[str, Dict[str, List[str]]]:
        return _load_datas()['g_shens']
    
    @classmethod
    def tianyis(cls) -> Dict[str, List[Tuple[str]]]:
        return _load_datas()['tianyis']
    
    @classmethod
    def yutangs(cls) -> Dict[str, List[Tuple[str]]]:
        return _load_datas()['yutangs']
    
    @classmethod
    def empties(cls) -> Dict[Tuple, Tuple]:
        return _load_datas()['empties']
    
    @classmethod
    def jianchus(cls) -> Dict[int, Tuple[str, str]]:
        return _load_datas()['jianchus']
    
    @classmethod
    def xingxius(cls) -> Dict[int, Tuple[str, str]]:
        return _load_datas()['xingxius']
    
    @classmethod
    def days60(cls) -> Dict[str, str]:
        return _load_datas()['days60']
    
    @classmethod
    def chens(cls) -> Dict[str, str]:
        return _load_datas()['chens']
    
    @classmethod
    def gan_hes(cls) -> Dict[Tuple, str]:
        """天干合表"""
        return _load_ganzhi()['gan_hes']
    
    @classmethod
    def nayins(cls) -> Dict[Tuple, str]:
        return _load_datas()['nayins']
    
    # ---- yue.py 导出 ----
    @classmethod
    def months(cls) -> Dict[str, str]:
        return _load_yue()['months']
    
    # ---- sizi.py 导出 ----
    @classmethod
    def summarys(cls) -> Dict[str, str]:
        return _load_sizi()['summarys']


# 快捷别名
BD = BaziData