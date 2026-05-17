# -*- coding: utf-8 -*-
"""
bazi_calc.main - CLI 入口
提供命令行接口，兼容原有 bazi_calc.py 的 CLI 参数
"""

import argparse
import sys
from typing import Optional, List

from .calculator import BaziCalculator, get_calculator
from .formatter import get_formatter, format_bazi
from .mingli import analyze_mingli


# ============================================================
# CLI 参数定义
# ============================================================

DESCRIPTION = '''
八字排盘工具
-----------
支持公历/农历输入，直接输入八字（大运反查），自动计算四柱、大运、神煞、命理分析
'''

parser = argparse.ArgumentParser(
    description=DESCRIPTION,
    formatter_class=argparse.RawTextHelpFormatter
)
parser.add_argument('year', nargs='?', action='store', help='年(数字) 或 年柱干支(如"庚午"，配合-b使用)')
parser.add_argument('month', nargs='?', action='store', help='月(数字) 或 月柱干支(配合-b使用)')
parser.add_argument('day', nargs='?', action='store', help='日(数字) 或 日柱干支(配合-b使用)')
parser.add_argument('time', nargs='?', action='store', help='时(数字) 或 时柱干支(配合-b使用)')
parser.add_argument('--start', help='起始年份（用于八字反查），默认1850', type=int, default=1850)
parser.add_argument('--end', help='结束年份（用于八字反查），默认2030', default='2030')
parser.add_argument('-b', action='store_true', default=False,
                   help='直接输入八字，参数为四柱干支(如: 庚午 己卯 己卯 甲戌)')
parser.add_argument('-g', action='store_true', default=False,
                   help='是否采用公历（默认农历）')
parser.add_argument('-r', action='store_true', default=False,
                   help='是否为闰月（仅用于农历）')
parser.add_argument('-n', action='store_true', default=False,
                   help='是否为女命（默认男命）')
parser.add_argument('-f', '--format', choices=['terminal', 'json', 'plain', 'html'],
                   default='terminal', help='输出格式，默认terminal')
parser.add_argument('-y', '--liunian', nargs='?', const='current',
                   metavar='YEAR', help='查看流年运势，如 -y 2025 或 -y 查看今年')
parser.add_argument('-o', '--output', help='输出到文件')
parser.add_argument('--version', action='version',
                   version='%(prog)s 2.1 (模块化版本)')


# ============================================================
# CLI 主函数
# ============================================================

def main(argv: Optional[List[str]] = None) -> int:
    """
    CLI 主入口
    
    用法:
        # 基本用法（农历）
        python -m bazi_calc.main 1990 3 15 19
        
        # 女命
        python -m bazi_calc.main 1990 3 15 19 -n
        
        # 公历输入
        python -m bazi_calc.main 1990 3 15 19 -g
        
        # JSON 输出
        python -m bazi_calc.main 1990 3 15 19 -f json
        
        # 直接输入八字（大运反查）
        python -m bazi_calc.main 庚午 己卯 己卯 甲戌 -b --start 1990 --end 2000
        
        # 带参数
        python -m bazi_calc.main 1990 3 15 19 -n --start 1950 --end 2050
    """
    options = parser.parse_args(argv)
    
    try:
        calculator = get_calculator()
        
        if options.b:
            # 直接输入八字模式：参数为完整的干支字符串
            if not all([options.year, options.month, options.day, options.time]):
                print("错误: -b 模式需要提供四个干支 (年柱 月柱 日柱 时柱)", file=sys.stderr)
                return 1
            
            # 参数是完整的干支，如 "庚午" "己卯"
            year_gz = options.year
            month_gz = options.month
            day_gz = options.day
            time_gz = options.time
            
            result = calculator.calculate(
                year=year_gz,
                month=month_gz,
                day=day_gz,
                time=time_gz,
                female=options.n,
                lunar=False,
                leap=False,
                direct_input=True,
                start_year=options.start,
                end_year=int(options.end) if isinstance(options.end, str) else options.end
            )
        else:
            # 普通模式：数字输入
            if not all([options.year, options.month, options.day, options.time]):
                print("错误: 请提供年、月、日、时", file=sys.stderr)
                return 1
            
            result = calculator.calculate(
                year=int(options.year),
                month=int(options.month),
                day=int(options.day),
                time=int(options.time),
                female=options.n,
                lunar=not options.g,
                leap=options.r,
                start_year=options.start,
                end_year=int(options.end) if isinstance(options.end, str) else options.end
            )
        
        # 流年查询模式
        if options.liunian:
            from .liunian import predict_liunian
            import datetime
            
            if options.liunian == 'current':
                year = datetime.datetime.now().year
            else:
                try:
                    year = int(options.liunian)
                except ValueError:
                    print(f"错误: 无效的年份 '{options.liunian}'", file=sys.stderr)
                    return 1
            
            pred = predict_liunian(result, year)
            print(f"\n{'='*60}")
            print(f"  {year}年流年运势")
            print(f"{'='*60}")
            print(f"岁数: {pred['age']}岁 | 干支: {pred['ganzhi']} | 纳音: {pred['nayin']}")
            print(f"天干神: {pred['gan_shens']} | 地支神: {pred['zhi_shens']}")
            if pred['relations']:
                print(f"关系: {pred['relations']}")
            if pred['empty']:
                print(f"空亡: {pred['empty']}")
            print()
            print(pred['summary'])
            if pred['advice']:
                print()
                for a in pred['advice']:
                    print(f"  • {a}")
            return 0
        
        # 格式化输出
        formatter = get_formatter(options.format)
        output = formatter.format(result)
        
        # 输出到文件或标准输出
        if options.output:
            with open(options.output, 'w', encoding='utf-8') as f:
                f.write(output)
            print(f"已保存到: {options.output}", file=sys.stderr)
        else:
            print(output)
        
        # 命理分析（仅终端格式）
        if options.format == 'terminal' and not options.output:
            print()
            mingli_lines = analyze_mingli(result, options.n)
            if mingli_lines:
                print('\033[1;33;40m' + '【命理分析】' + '\033[0m')
                for line in mingli_lines:
                    print(line)
        
        return 0
        
    except NotImplementedError as e:
        print(f"错误: {e}", file=sys.stderr)
        return 1
    except ValueError as e:
        print(f"参数错误: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"未知错误: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())