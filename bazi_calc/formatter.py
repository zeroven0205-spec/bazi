# -*- coding: utf-8 -*-
"""
bazi_calc.formatter - 八字输出格式化
支持 terminal / json / html / plain 等多格式输出
"""

import json
from typing import List, Dict, Any, Optional

from .types import BaziResult, Dayun, WuXingScores
from .bazi_data import BD


# ============================================================
# 颜色常量
# ============================================================

class Colors:
    """终端颜色码"""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'
    BG_YELLOW = '\033[43m'

    @classmethod
    def colored(cls, text: str, *styles: str) -> str:
        """给文本应用颜色样式"""
        if not styles:
            return text
        prefix = ''.join(getattr(cls, s) for s in styles if hasattr(cls, s))
        return f"{prefix}{text}{cls.RESET}"


# ============================================================
# 格式化器基类
# ============================================================

class BaziFormatter:
    """八字格式化器基类"""
    
    def format(self, result: BaziResult) -> str:
        raise NotImplementedError


# ============================================================
# 终端格式化器
# ============================================================

class TerminalFormatter(BaziFormatter):
    """
    终端彩色输出格式化器
    
    用法:
        from bazi_calc import BaziCalculator
        from bazi_calc.formatter import TerminalFormatter
        
        result = BaziCalculator().calculate(1990, 3, 15, 19)
        print(TerminalFormatter().format(result))
    """
    
    WIDE_SPACE = chr(12288)  # 全角空格，用于对齐
    
    def format(self, result: BaziResult) -> str:
        lines = []
        
        # 头部信息
        lines.append(self._format_header(result))
        
        # 四柱信息
        lines.append(self._format_bazi(result))
        
        # 五行得分
        lines.append(self._format_wuxing(result))
        
        # 神煞
        lines.append(self._format_shens(result))
        
        # 大运
        lines.append(self._format_dayuns(result))
        
        return '\n'.join(lines)
    
    def _format_header(self, result: BaziResult) -> str:
        """格式化头部信息"""
        header = f"{Colors.CYAN}{Colors.BOLD}{'─' * 80}{Colors.RESET}\n"
        header += f"{Colors.CYAN}{Colors.BOLD}  八字排盘  {Colors.RESET}\n"
        header += f"{Colors.CYAN}{'─' * 80}{Colors.RESET}\n"
        header += f"性别: {result.sex} | {result.solar} | {result.lunar}\n"
        
        # 命宫/胎元/身宫
        if result.ming_gong or result.tai_yuan or result.shen_gong:
            gong_info = []
            if result.ming_gong:
                gong_info.append(f"命宫:{result.ming_gong}")
            if result.tai_yuan:
                gong_info.append(f"胎元:{result.tai_yuan}")
            if result.shen_gong:
                gong_info.append(f"身宫:{result.shen_gong}")
            header += f"{Colors.YELLOW}{' | '.join(gong_info)}{Colors.RESET}\n"
        
        header += f"{Colors.CYAN}{'─' * 80}{Colors.RESET}"
        return header
    
    def _format_bazi(self, result: BaziResult) -> str:
        """格式化八字四柱"""
        lines = []
        
        # 表头
        col_labels = ["年柱", "月柱", "日柱", "时柱"]
        line1 = "      " + "".join(f"{label:<12}" for label in col_labels)
        lines.append(Colors.colored(line1, 'YELLOW', 'BOLD'))
        
        # 天干
        gan_row = "天干  " + "".join(f"{g:<12}" for g in result.gans)
        lines.append(Colors.colored(gan_row, 'GREEN'))
        
        # 天干十神
        shen_row = f"     " + "".join(f"{s:<12}" for s in result.gan_shens)
        lines.append(shen_row)
        
        # 地支
        zhi_row = "地支  " + "".join(f"{z:<12}" for z in result.zhis)
        lines.append(Colors.colored(zhi_row, 'MAGENTA'))
        
        # 地支十神
        zhi_shen_row = f"     " + "".join(
            f"{result.zhi_shens[i]:<12}" for i in range(4)
        )
        lines.append(zhi_shen_row)
        
        # 地支藏干十神
        zhi_shen3_row = "藏干神 " + "".join(
            f"{'/'.join(result.zhi_shen3[i]):<12}" for i in range(4)
        )
        lines.append(zhi_shen3_row)
        
        # 日主五行
        gan5_me = BD.gan5()[result.me]
        me_info = f"日主 {result.me} ({gan5_me})"
        lines.append(Colors.colored(me_info, 'CYAN', 'BOLD'))
        
        # 强弱判断
        strong_label = "强" if not result.weak else "弱"
        strong_color = 'GREEN' if not result.weak else 'RED'
        strong_info = f"身 {strong_label} | 五行得分: "
        lines.append(Colors.colored(strong_info, strong_color) + 
                    ', '.join(f"{k}:{v}" for k, v in result.scores.items()))
        
        # 调候
        if result.temps_score > 0:
            temps_info = f"调候: {result.temps_score}"
            lines.append(Colors.colored(temps_info, 'YELLOW'))
        
        return '\n'.join(lines)
    
    def _format_wuxing(self, result: BaziResult) -> str:
        """格式化五行得分"""
        scores = result.scores
        total = sum(scores.values()) if scores else 0
        
        lines = []
        lines.append(Colors.colored("\n【五行统计】", 'YELLOW', 'BOLD'))
        
        if scores:
            max_val = max(scores.values()) if scores else 1
            bar_width = 20
            
            for wx, val in scores.items():
                pct = val / total * 100 if total > 0 else 0
                filled = int(bar_width * val / max_val) if max_val > 0 else 0
                bar = '█' * filled + '░' * (bar_width - filled)
                
                wx_color = {'金': 'YELLOW', '木': 'GREEN', 
                           '水': 'CYAN', '火': 'RED', '土': 'MAGENTA'}.get(wx, 'WHITE')
                
                lines.append(
                    f"{Colors.colored(wx, wx_color)} {bar} {val} ({pct:.0f}%)"
                )
        
        return '\n'.join(lines)
    
    def _format_shens(self, result: BaziResult) -> str:
        """格式化神煞"""
        lines = []
        
        if result.all_shens:
            lines.append(Colors.colored("\n【神煞】", 'YELLOW', 'BOLD'))
            lines.append("  " + ", ".join(result.all_shens))
        
        # 各柱神煞
        col_names = ["年柱", "月柱", "日柱", "时柱"]
        has_col_shens = any(result.column_shens[i] for i in range(4))
        
        if has_col_shens:
            lines.append(Colors.colored("\n【各柱神煞】", 'YELLOW', 'BOLD'))
            for i in range(4):
                if result.column_shens[i]:
                    lines.append(f"  {col_names[i]}: {result.column_shens[i]}")
        
        return '\n'.join(lines)
    
    def _format_dayuns(self, result: BaziResult) -> str:
        """格式化大运"""
        lines = []
        
        if result.dayuns:
            lines.append(Colors.colored("\n【大运】", 'YELLOW', 'BOLD'))
            
            # 表头
            header = f"  {'岁运':>4} {'干支':^8} {'天干神':^6} {'地支神':^6}"
            lines.append(Colors.colored(header, 'DIM'))
            lines.append('  ' + '-' * 40)
            
            for dayun in result.dayuns:
                line = f"  {dayun.age:>4} {dayun.ganzhi:^8} "
                line += f"{dayun.gan_shens:^6} {dayun.zhi_shens:^6}"
                lines.append(line)
        
        return '\n'.join(lines)


# ============================================================
# JSON 格式化器
# ============================================================

class JsonFormatter(BaziFormatter):
    """
    JSON 格式输出
    
    用法:
        from bazi_calc import BaziCalculator
        from bazi_calc.formatter import JsonFormatter
        
        result = BaziCalculator().calculate(1990, 3, 15, 19)
        print(JsonFormatter().format(result))
    """
    
    def format(self, result: BaziResult) -> str:
        data = {
            "meta": {
                "sex": result.sex,
                "solar": result.solar,
                "lunar": result.lunar,
                "ming_gong": result.ming_gong,
                "tai_yuan": result.tai_yuan,
                "shen_gong": result.shen_gong
            },
            "bazi": {
                "gans": list(result.gans),
                "zhis": list(result.zhis),
                "gan_shens": result.gan_shens,
                "zhi_shens": result.zhi_shens,
                "zhi_shen3": result.zhi_shen3
            },
            "analysis": {
                "me": result.me,
                "month_zhi": result.month_zhi,
                "strong": result.strong,
                "weak": result.weak,
                "scores": dict(result.scores),
                "gan_scores": dict(result.gan_scores),
                "temps_score": result.temps_score,
                "humidity": result.humidity
            },
            "relations": {
                "gong": result.gong,
                "zhi_6he": result.zhi_6he,
                "zhi_6chong": result.zhi_6chong,
                "gan_he": result.gan_he,
                "zhi_xing": result.zhi_xing
            },
            "ges": result.all_ges,
            "jus": result.jus,
            "all_shens": result.all_shens,
            "column_shens": list(result.column_shens),
            "dayuns": [
                {
                    "age": d.age,
                    "start_year": d.start_year,
                    "ganzhi": d.ganzhi,
                    "gan_shens": d.gan_shens,
                    "zhi_shens": d.zhi_shens,
                    "relations": d.relations,
                    "empty": d.empty,
                    "fu": d.fu,
                    "nayin": d.nayin,
                    "shens": d.shens
                }
                for d in result.dayuns
            ]
        }
        
        return json.dumps(data, ensure_ascii=False, indent=2)


# ============================================================
# 纯文本格式化器（无颜色）
# ============================================================

class PlainFormatter(BaziFormatter):
    """
    纯文本输出（无 ANSI 颜色码）
    
    用法:
        from bazi_calc import BaziCalculator
        from bazi_calc.formatter import PlainFormatter
        
        result = BaziCalculator().calculate(1990, 3, 15, 19)
        print(PlainFormatter().format(result))
    """
    
    WIDE_SPACE = '  '
    
    def format(self, result: BaziResult) -> str:
        lines = []
        
        # 头部
        lines.append('=' * 60)
        lines.append('  八字排盘')
        lines.append('=' * 60)
        lines.append(f"性别: {result.sex} | {result.solar} | {result.lunar}")
        
        # 命宫/胎元/身宫
        if result.ming_gong or result.tai_yuan or result.shen_gong:
            gong_parts = []
            if result.ming_gong:
                gong_parts.append(f"命宫:{result.ming_gong}")
            if result.tai_yuan:
                gong_parts.append(f"胎元:{result.tai_yuan}")
            if result.shen_gong:
                gong_parts.append(f"身宫:{result.shen_gong}")
            lines.append(' | '.join(gong_parts))
        
        # 四柱
        lines.append('')
        lines.append('      年柱        月柱        日柱        时柱')
        lines.append(f"天干  {result.gans[0]:<10} {result.gans[1]:<10} {result.gans[2]:<10} {result.gans[3]:<10}")
        lines.append(f"       {result.gan_shens[0]:<10} {result.gan_shens[1]:<10} {result.gan_shens[2]:<10} {result.gan_shens[3]:<10}")
        lines.append(f"地支  {result.zhis[0]:<10} {result.zhis[1]:<10} {result.zhis[2]:<10} {result.zhis[3]:<10}")
        lines.append(f"       {result.zhi_shens[0]:<10} {result.zhi_shens[1]:<10} {result.zhi_shens[2]:<10} {result.zhi_shens[3]:<10}")
        lines.append(f"藏干神 {'/'.join(result.zhi_shen3[0]):<10} {'/'.join(result.zhi_shen3[1]):<10} {'/'.join(result.zhi_shen3[2]):<10} {'/'.join(result.zhi_shen3[3]):<10}")
        
        # 日主
        lines.append(f"日主 {result.me}")
        lines.append(f"身 {'强' if not result.weak else '弱'} | 五行: {', '.join(f'{k}:{v}' for k, v in result.scores.items())}")
        
        # 神煞
        if result.all_shens:
            lines.append('')
            lines.append(f"神煞: {', '.join(result.all_shens)}")
        
        # 大运
        if result.dayuns:
            lines.append('')
            lines.append('大运:')
            lines.append('  岁运   干支    天干神  地支神')
            for d in result.dayuns:
                lines.append(f"  {d.age:>4}   {d.ganzhi}   {d.gan_shens:<6}  {d.zhi_shens:<6}")
        
        return '\n'.join(lines)


# ============================================================
# HTML 格式化器
# ============================================================

class HtmlFormatter(BaziFormatter):
    """
    HTML 格式输出
    
    用法:
        from bazi_calc import BaziCalculator
        from bazi_calc.formatter import HtmlFormatter
        
        result = BaziCalculator().calculate(1990, 3, 15, 19)
        print(HtmlFormatter().format(result))
    """
    
    def format(self, result: BaziResult) -> str:
        html = ['<div class="bazi-result">']
        
        # 头部
        html.append('<div class="header">')
        html.append(f'<h1>八字排盘</h1>')
        html.append(f'<p>性别: {result.sex} | {result.solar} | {result.lunar}</p>')
        html.append('</div>')
        
        # 四柱
        html.append('<div class="bazi-table">')
        html.append('<table>')
        html.append('<tr><th></th><th>年柱</th><th>月柱</th><th>日柱</th><th>时柱</th></tr>')
        html.append(f'<tr><td>天干</td>{"".join(f"<td>{g}</td>" for g in result.gans)}</tr>')
        html.append(f'<tr><td>十神</td>{"".join(f"<td>{s}</td>" for s in result.gan_shens)}</tr>')
        html.append(f'<tr><td>地支</td>{"".join(f"<td>{z}</td>" for z in result.zhis)}</tr>')
        html.append(f'<tr><td>十神</td>{"".join(f"<td>{s}</td>" for s in result.zhi_shens)}</tr>')
        html.append('</table>')
        html.append('</div>')
        
        # 五行得分
        if result.scores:
            html.append('<div class="wuxing">')
            html.append('<h3>五行统计</h3>')
            html.append('<ul>')
            for wx, val in result.scores.items():
                html.append(f'<li>{wx}: {val}</li>')
            html.append('</ul>')
            html.append('</div>')
        
        # 神煞
        if result.all_shens:
            html.append('<div class="shens">')
            html.append(f'<h3>神煞</h3>')
            html.append('<p>' + ', '.join(result.all_shens) + '</p>')
            html.append('</div>')
        
        # 大运
        if result.dayuns:
            html.append('<div class="dayuns">')
            html.append('<h3>大运</h3>')
            html.append('<table>')
            html.append('<tr><th>岁运</th><th>干支</th><th>天干神</th><th>地支神</th></tr>')
            for d in result.dayuns:
                html.append(f'<tr><td>{d.age}</td><td>{d.ganzhi}</td><td>{d.gan_shens}</td><td>{d.zhi_shens}</td></tr>')
            html.append('</table>')
            html.append('</div>')
        
        html.append('</div>')
        return '\n'.join(html)


# ============================================================
# 工厂函数
# ============================================================

def get_formatter(fmt: str = 'terminal') -> BaziFormatter:
    """
    获取格式化器实例
    
    Args:
        fmt: 格式类型 ('terminal', 'json', 'plain', 'html')
    
    Returns:
        BaziFormatter: 格式化器实例
    """
    formatters = {
        'terminal': TerminalFormatter,
        'json': JsonFormatter,
        'plain': PlainFormatter,
        'html': HtmlFormatter
    }
    
    formatter_class = formatters.get(fmt, TerminalFormatter)
    return formatter_class()


def format_bazi(result: BaziResult, fmt: str = 'terminal') -> str:
    """
    格式化八字结果的便捷函数
    
    用法:
        from bazi_calc import BaziCalculator
        from bazi_calc.formatter import format_bazi
        
        result = BaziCalculator().calculate(1990, 3, 15, 19)
        print(format_bazi(result, 'json'))
    """
    return get_formatter(fmt).format(result)