# -*- coding: utf-8 -*-
"""
bazi_calc - 八字排盘模块化包

拆分自 bazi_calc.py，提供模块化的八字计算功能

主要模块:
- types: 共享类型定义
- bazi_data: 数据层封装
- calculator: 核心计算引擎
- formatter: 输出格式化
- mingli: 命理分析
- main: CLI 入口

用法:
    from bazi_calc import BaziCalculator, BaziResult
    
    # 计算八字
    result = BaziCalculator().calculate(1990, 3, 15, 19)
    
    # 格式化输出
    from bazi_calc.formatter import TerminalFormatter
    print(TerminalFormatter().format(result))
    
    # 命理分析
    from bazi_calc.mingli import analyze_mingli
    for line in analyze_mingli(result):
        print(line)
"""

from .types import (
    BaziInput,
    BaziCore,
    WuXingScores,
    GanScores,
    BaziColumn,
    Dayun,
    Liunian,
    BaziResult
)

from .calculator import BaziCalculator, get_calculator

from .formatter import (
    BaziFormatter,
    TerminalFormatter,
    JsonFormatter,
    PlainFormatter,
    HtmlFormatter,
    get_formatter,
    format_bazi,
    Colors
)

from .mingli import (
    MingliAnalyzer,
    analyze_mingli
)

from .liunian import (
    LiunianCalculator,
    LiunianReader,
    calculate_liunians,
    predict_liunian
)

from .luohou import (
    LuohouCalculator,
    calculate_luohou
)

from .persistence import (
    export_json,
    import_json,
    to_json,
    from_json,
    save_result,
    PersistenceError
)

__version__ = '2.1'
__all__ = [
    # 类型
    'BaziInput',
    'BaziCore',
    'WuXingScores',
    'GanScores',
    'BaziColumn',
    'Dayun',
    'Liunian',
    'BaziResult',
    # 计算器
    'BaziCalculator',
    'get_calculator',
    # 格式化器
    'BaziFormatter',
    'TerminalFormatter',
    'JsonFormatter',
    'PlainFormatter',
    'HtmlFormatter',
    'get_formatter',
    'format_bazi',
    'Colors',
    # 命理分析
    'MingliAnalyzer',
    'analyze_mingli',
    # 流年
    'LiunianCalculator',
    'LiunianReader',
    'calculate_liunians',
    'predict_liunian',
    # 罗喉派
    'LuohouCalculator',
    'calculate_luohou',
    # 导出/导入
    'export_json',
    'import_json',
    'to_json',
    'from_json',
    'save_result',
]