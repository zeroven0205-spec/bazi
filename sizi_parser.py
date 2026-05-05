# -*- coding: utf-8 -*-
"""
bazi.sizi - 命理文本结构化解析
从 sizi.py 的 summarys 提取结构化标签，支持智能检索
"""

import re
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass, field

# ============================================================
# 结构化数据模型
# ============================================================

@dataclass
class SiziRef:
    """命理文献引用"""
    code: str          # 如 "2-86"
    desc: str          # 如 "天月德贵人"


@dataclass
class SiziCase:
    """命例片段"""
    ganzhi: str        # 如 "甲寅日甲子时"
    desc: str          # 如 "拱丑中辛，贵"


@dataclass
class SiziEntry:
    """结构化的八字解读条目"""
    key: str                           # 如 "甲日甲子"
    text: str                          # 原始文本
    tags: List[str] = field(default_factory=list)       # 特征标签
    refs: List[SiziRef] = field(default_factory=list)    # 文献引用
    cases: List[SiziCase] = field(default_factory=list) # 命例片段
    wuhang: Optional[str] = None       # 日主五行
    pattern: Optional[str] = None      # 命局特征


# ============================================================
# 注释标签解析
# ============================================================

# 匹配 # 2-86 这种引用格式
REF_PATTERN = re.compile(r"#\s*(\d+-\d+)\s*(.*)")

# 匹配命例片段（甲寅日甲子时，...）
CASE_PATTERN = re.compile(r"([^，,。\n]{2,8}日[^，,。\n]{2,6}时?[,，。]?\s*[^。\n]*)")

# 匹配日主五行（甲木春月、乙木秋令 等）
WUHANG_PATTERN = re.compile(r"^([甲乙丙丁戊己庚辛壬癸])日")


class SiziParser:
    """四柱命理文本解析器"""

    def __init__(self):
        self.entries: Dict[str, SiziEntry] = {}
        self._tag_index: Dict[str, Set[str]] = {}  # tag -> set of keys
        self._wuhang_index: Dict[str, Set[str]] = {}  # wuhang -> set of keys

    def parse_text(self, key: str, text: str) -> SiziEntry:
        """
        解析单条 summarys 文本

        Args:
            key: 如 "甲日甲子"
            text: 原始文本

        Returns:
            SiziEntry: 结构化后的条目
        """
        entry = SiziEntry(key=key, text=text)

        # 提取日主五行
        wuhang_match = WUHANG_PATTERN.match(key)
        if wuhang_match:
            gan = wuhang_match.group(1)
            wuhang_map = {
                "甲": "木", "乙": "木", "丙": "火", "丁": "火",
                "戊": "土", "己": "土", "庚": "金", "辛": "金",
                "壬": "水", "癸": "水"
            }
            entry.wuhang = wuhang_map.get(gan)

        # 提取文献引用
        for match in REF_PATTERN.finditer(text):
            entry.refs.append(SiziRef(code=match.group(1), desc=match.group(2).strip()))

        # 提取命例片段
        for match in CASE_PATTERN.finditer(text):
            case_text = match.group(1).strip()
            if len(case_text) > 4:
                # 简单判断是否包含"贵"/"富"/"凶"等关键词
                entry.cases.append(SiziCase(ganzhi=case_text[:4], desc=case_text[4:]))

        # 自动生成标签
        entry.tags = self._extract_tags(entry)

        return entry

    def _extract_tags(self, entry: SiziEntry) -> List[str]:
        """基于内容自动提取标签"""
        tags = []
        text = entry.text

        # 基于关键词提取标签
        tag_keywords = {
            "贵格": ["贵", "大贵", "近侍之贵", "文武职"],
            "富格": ["富", "大富", "财"],
            "凶格": ["凶", "死", "刑", "夭"],
            "官杀": ["官", "杀", "煞"],
            "印绶": ["印", "印绶"],
            "食神": ["食", "食神"],
            "伤官": ["伤", "伤官"],
            "比劫": ["比", "劫", "比劫"],
            "财星": ["财", "财星"],
            "日主弱": ["衰", "弱", "无气"],
            "日主旺": ["旺", "盛", "强"],
        }

        for tag, keywords in tag_keywords.items():
            if any(kw in text for kw in keywords):
                tags.append(tag)

        # 四季特征
        seasons = ["春", "夏", "秋", "冬"]
        for season in seasons:
            if season in entry.key or season in text:
                tags.append(season)

        # 月令特征
        months = ["正月", "二月", "三月", "四月", "五月", "六月",
                  "七月", "八月", "九月", "十月", "十一月", "十二月"]
        for month in months:
            if month in text:
                tags.append(month)

        return list(set(tags))  # 去重

    def build_index(self, summarys: Dict[str, str]):
        """
        从原始 summarys 构建完整索引

        Args:
            summarys: sizi.py 中的原始 summarys 字典
        """
        self.entries.clear()
        self._tag_index.clear()
        self._wuhang_index.clear()

        for key, text in summarys.items():
            entry = self.parse_text(key, text)
            self.entries[key] = entry

            # 构建标签索引
            for tag in entry.tags:
                if tag not in self._tag_index:
                    self._tag_index[tag] = set()
                self._tag_index[tag].add(key)

            # 构建五行索引
            if entry.wuhang:
                if entry.wuhang not in self._wuhang_index:
                    self._wuhang_index[entry.wuhang] = set()
                self._wuhang_index[entry.wuhang].add(key)

    def search(self, tags: List[str] = None, wuhang: str = None,
               keyword: str = None, limit: int = 10) -> List[SiziEntry]:
        """
        检索命例

        Args:
            tags: 标签列表（AND 匹配）
            wuhang: 日主五行（木/火/土/金/水）
            keyword: 关键词（模糊匹配 text）
            limit: 返回条数限制

        Returns:
            匹配的 SiziEntry 列表
        """
        result_keys = set()

        # 按标签过滤
        if tags:
            for tag in tags:
                if tag in self._tag_index:
                    if not result_keys:
                        result_keys = self._tag_index[tag].copy()
                    else:
                        result_keys &= self._tag_index[tag]
                else:
                    return []  # 标签不存在则无结果

        # 按五行过滤
        if wuhang:
            if wuhang not in self._wuhang_index:
                return []
            if not result_keys:
                result_keys = self._wuhang_index[wuhang].copy()
            else:
                result_keys &= self._wuhang_index[wuhang]

        # 应用所有过滤后转为 entries
        if result_keys:
            entries = [self.entries[k] for k in result_keys]
        else:
            entries = list(self.entries.values())

        # 按关键词过滤（模糊匹配）
        if keyword:
            kw_lower = keyword.lower()
            entries = [e for e in entries if kw_lower in e.text.lower()]

        return entries[:limit]

    def get_by_key(self, key: str) -> Optional[SiziEntry]:
        """按 key 获取条目"""
        return self.entries.get(key)

    def list_tags(self) -> List[str]:
        """列出所有标签"""
        return list(self._tag_index.keys())

    def list_by_wuhang(self, wuhang: str) -> List[SiziEntry]:
        """列出某五行所有命例"""
        if wuhang not in self._wuhang_index:
            return []
        return [self.entries[k] for k in self._wuhang_index[wuhang]]


# ============================================================
# 全局实例
# ============================================================

_sizi_parser: Optional[SiziParser] = None


def get_sizi_parser() -> SiziParser:
    """获取全局 SiziParser 实例（延迟初始化）"""
    global _sizi_parser
    if _sizi_parser is None:
        _sizi_parser = SiziParser()
        # 注意：需要外部调用 build_index(summarys) 来加载数据
    return _sizi_parser


def init_sizi_index(summarys: Dict[str, str]):
    """初始化四柱索引（从外部调用）"""
    parser = get_sizi_parser()
    parser.build_index(summarys)
