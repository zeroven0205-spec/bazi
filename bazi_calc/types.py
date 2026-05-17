# -*- coding: utf-8 -*-
"""
bazi_calc.types - 共享类型定义
八字计算中的核心数据结构
"""

from collections import namedtuple
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

# ============================================================
# 基础类型
# ============================================================

Gans = namedtuple("Gans", "year month day time")
Zhis = namedtuple("Zhis", "year month day time")
Gans3 = namedtuple("Gans3", "year month day")  # 三字版本（luohou 用）
Zhis3 = namedtuple("Zhis3", "year month day")


@dataclass
class BaziInput:
    """八字输入参数"""
    year: int
    month: int
    day: int
    time: int
    female: bool = False
    lunar: bool = False
    leap: bool = False  # 闰月
    direct_input: bool = False  # 直接输入八字


@dataclass
class BaziCore:
    """八字核心四柱"""
    gans: Gans
    zhis: Zhis
    me: str  # 日干
    month_zhi: str  # 月支


@dataclass
class WuXingScores:
    """五行分数"""
    金: int = 0
    木: int = 0
    水: int = 0
    火: int = 0
    土: int = 0


@dataclass
class GanScores:
    """天干分数"""
    甲: int = 0
    乙: int = 0
    丙: int = 0
    丁: int = 0
    戊: int = 0
    己: int = 0
    庚: int = 0
    辛: int = 0
    壬: int = 0
    癸: int = 0


@dataclass
class BaziColumn:
    """单柱信息"""
    gan: str
    zhi: str
    gan_shens: str  # 天干十神
    zhi_main_shen: str  # 地支主气十神
    zhi_all_shens: List[str]  # 地支所有十神
    zhi_relations: Dict[str, List[str]]  # 地支关系（冲合刑害等）


@dataclass
class Dayun:
    """大运信息"""
    age: int
    start_year: int
    ganzhi: str
    gan_shens: str
    zhi_shens: str
    zhi5_detail: str  # 地支藏干详情
    relations: str  # 与原局的关系
    empty: str  # 空亡
    fu: str  # 福禄标记
    nayin: str  # 纳音五行
    shens: str  # 神煞


@dataclass
class Liunian:
    """流年信息"""
    age: int
    year: int
    ganzhi: str
    gan_shens: str
    zhi_shens: str
    zhi5_detail: str
    relations: str
    empty: str
    fu: str
    nayin: str
    shens: str
    special: str = ''  # 特殊组合（四生/四败/四库/天罗地网等）


@dataclass
class BaziResult:
    """八字计算完整结果"""
    # 基本信息
    sex: str  # 男/女
    solar: str  # 公历日期
    lunar: str  # 农历日期
    ming_gong: str  # 命宫
    tai_yuan: str  # 胎元
    shen_gong: str  # 身宫
    
    # 核心四柱
    gans: Gans
    zhis: Zhis
    me: str
    month_zhi: str
    
    # 十神
    gan_shens: List[str]
    zhi_shens: List[str]
    zhi_shen3: List[List[str]]  # 每柱所有神（包含余气）
    zhus: List[tuple]  # (干, 支) 元组列表
    
    # 五行
    scores: Dict[str, int]
    gan_scores: Dict[str, int]
    strong: int
    weak: bool
    
    # 调候
    temps_score: int
    humidity: int  # 湿度分数
    gong: List[str]  # 拱
    
    # 关系
    zhi_6he: List[bool]
    zhi_6chong: List[bool]
    gan_he: List[bool]
    zhi_xing: List[bool]
    
    # 大运
    dayuns: List[Dayun]
    
    # 神煞
    all_shens: List[str]
    column_shens: tuple  # 每柱神煞
    
    # 格局
    all_ges: List[str]
    jus: List[str]  # 三合三会局
    
    # 输出行（用于终端/JSON输出）
    lines: List[str] = field(default_factory=list)
    
    # 命理分析文本
    mingli_texts: List[str] = field(default_factory=list)


@dataclass
class ShenShaInfo:
    """神煞详细信息"""
    name: str
    desc: str