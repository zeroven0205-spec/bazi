# -*- coding: utf-8 -*-
"""
bazi.cli - 统一命令行入口
支持 bazi/luohou/shengxiao/convert 子命令
"""

import argparse
import sys
import os
import datetime
import importlib
from typing import Optional, Callable

# 子命令注册表
SUBCOMMANDS = {}


def subcommand(name: str, help_text: str):
    """子命令装饰器"""
    def decorator(func: Callable):
        SUBCOMMANDS[name] = {"func": func, "help": help_text}
        return func
    return decorator


# ============================================================
# 子命令实现
# ============================================================

@subcommand("bazi", "八字排盘 - 四柱五行分析、合冲刑害、大运计算")
def cmd_bazi(args):
    """八字排盘子命令"""
    # 将参数转换为 sys.argv 格式，调用 bazi 模块
    sys.argv = ["bazi"]

    if args.start:
        sys.argv.extend(["--start", str(args.start)])
    if args.end:
        sys.argv.extend(["--end", str(args.end)])

    if args.female:
        sys.argv.append("-n")
    if args.lunar:
        sys.argv.append("-g")
    if args.leap:
        sys.argv.append("-r")
    if args.bazi_input:
        sys.argv.append("-b")

    sys.argv.extend([str(args.year), str(args.month), str(args.day), str(args.time)])

    # 通过 subprocess 调用 bazi_calc.py（保持原模块的 argparse 独立运行）
    import subprocess
    bazi_cmd = ["python3", "bazi_calc.py"] + sys.argv[1:]
    result = subprocess.run(bazi_cmd, capture_output=False)
    return result.returncode


@subcommand("luohou", "罗喉日时 - 九宫飞星、太岁位置、杀师日时")
def cmd_luohou(args):
    """罗喉日时子命令"""
    sys.argv = ["luohou"]

    if args.date:
        sys.argv.extend(["-d", args.date])
    if args.days and args.days > 1:
        sys.argv.extend(["-n", str(args.days)])

    import runpy
    return runpy.run_module("luohou", run_name="__main__")


@subcommand("shengxiao", "生肖合婚 - 三合六合、相冲相刑、相害相破")
def cmd_shengxiao(args):
    """生肖合婚子命令"""
    sys.argv = ["shengxiao", args.zodiac]

    import runpy
    return runpy.run_module("shengxiao", run_name="__main__")


@subcommand("convert", "格式转换 - 干支字符串转换")
def cmd_convert(args):
    """格式转换子命令"""
    sys.argv = ["convert", args.gan, args.zhi]

    import runpy
    return runpy.run_module("convert", run_name="__main__")


@subcommand("dashi", "大运流年 - 输入八字，分析大运流年")
def cmd_dashi(args):
    """大运流年子命令"""
    print("大运流年分析功能开发中...")
    return 0


@subcommand("cache-clear", "清空万年历缓存")
def cmd_cache_clear(args):
    """清空缓存子命令"""
    from cache import get_lunar_cache
    cache = get_lunar_cache()
    cache.clear()
    print("✅ 缓存已清空")
    return 0


@subcommand("cache-info", "查看缓存状态")
def cmd_cache_info(args):
    """缓存状态子命令"""
    from cache import get_lunar_cache
    cache = get_lunar_cache()
    print(f"缓存条目数: {len(cache._cache)}")
    print(f"缓存文件: {os.path.dirname(os.path.abspath(__file__))}/.bazi_lunar_cache.pkl")
    return 0


@subcommand("search", "命例检索 - 基于结构化标签检索命理文本")
def cmd_search(args):
    """命例检索子命令"""
    from sizi_parser import get_sizi_parser
    from sizi import summarys

    parser = get_sizi_parser()
    parser.build_index(summarys)

    results = parser.search(
        tags=args.tags.split(",") if args.tags else None,
        wuhang=args.wuhang or None,
        keyword=args.keyword or None,
        limit=args.limit
    )

    print(f"找到 {len(results)} 条结果:\n")
    for entry in results:
        print(f"【{entry.key}】")
        if entry.tags:
            print(f"  标签: {', '.join(entry.tags)}")
        if entry.wuhang:
            print(f"  日主: {entry.wuhang}")
        print(f"  预览: {entry.text[:100]}...")
        print()

    return 0


# ============================================================
# 主 CLI 解析器
# ============================================================

def build_parser() -> argparse.ArgumentParser:
    """构建主解析器"""
    description = '''
bazi - 八字命理工具集

支持以下子命令：
  bazi       八字排盘
  luohou     罗喉日时
  shengxiao  生肖合婚
  convert    格式转换
  dashi      大运流年
  search     命例检索
  cache-clear  清空缓存
  cache-info  查看缓存

使用示例：
  python -m bazi bazi 1990 3 15 子
  python -m bazi luohou -d "2024 1 1" -n 7
  python -m bazi shengxiao 虎
  python -m bazi search --wuhang 木 --tags 贵格
    '''

    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # bazi 子命令
    p_bazi = subparsers.add_parser("bazi", help="八字排盘")
    p_bazi.add_argument("year", help="年")
    p_bazi.add_argument("month", help="月")
    p_bazi.add_argument("day", help="日")
    p_bazi.add_argument("time", help="时")
    p_bazi.add_argument("-s", "--start", type=int, default=1850, help="起始年份")
    p_bazi.add_argument("-e", "--end", type=int, default=2030, help="结束年份")
    p_bazi.add_argument("-n", "--female", action="store_true", help="女命")
    p_bazi.add_argument("--lunar", action="store_true", help="使用农历")
    p_bazi.add_argument("--leap", action="store_true", help="闰月")
    p_bazi.add_argument("-b", "--bazi-input", action="store_true", help="直接输入八字")

    # luohou 子命令
    p_luohou = subparsers.add_parser("luohou", help="罗喉日时")
    p_luohou.add_argument("-d", "--date", help="公历日期 (YYYY M D)")
    p_luohou.add_argument("-n", "--days", type=int, default=1, help="查询天数")

    # shengxiao 子命令
    p_shengxiao = subparsers.add_parser("shengxiao", help="生肖合婚")
    p_shengxiao.add_argument("zodiac", help="生肖 (鼠/牛/虎/兔/龙/蛇/马/羊/猴/鸡/狗/猪)")

    # convert 子命令
    p_convert = subparsers.add_parser("convert", help="格式转换")
    p_convert.add_argument("gan", help="天干")
    p_convert.add_argument("zhi", help="地支")

    # dashi 子命令
    p_dashi = subparsers.add_parser("dashi", help="大运流年")
    p_dashi.add_argument("year", help="年")
    p_dashi.add_argument("month", help="月")
    p_dashi.add_argument("day", help="日")
    p_dashi.add_argument("time", help="时")

    # search 子命令
    p_search = subparsers.add_parser("search", help="命例检索")
    p_search.add_argument("--tags", help="标签（逗号分隔，如'贵格,秋'）")
    p_search.add_argument("--wuhang", help="日主五行（木/火/土/金/水）")
    p_search.add_argument("--keyword", help="关键词")
    p_search.add_argument("--limit", type=int, default=10, help="结果条数限制")

    # cache 子命令
    p_cache = subparsers.add_parser("cache-clear", help="清空缓存")
    p_cache_info = subparsers.add_parser("cache-info", help="查看缓存")

    return parser


def main():
    """CLI 主入口"""
    # 动态设置模块路径（支持 python -m bazi）
    if __name__ == "__main__" or __name__ == "bazi.cli":
        pass
    else:
        pass

    parser = build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        print("\n请指定子命令，或使用 --help 查看子命令帮助")
        return 1

    if args.command not in SUBCOMMANDS:
        parser.print_help()
        return 1

    # 调用子命令
    try:
        cmd_info = SUBCOMMANDS[args.command]
        return cmd_info["func"](args)
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
