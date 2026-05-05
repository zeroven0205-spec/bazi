# bazi 项目优化方案

> 文档版本: v1.0
> 创建时间: 2026-05-05
> 状态: 进行中

---

## 一、项目概述

**项目名称:** bazi (八字) - 中国传统命理计算工具集

**核心功能:**

| 模块 | 功能 |
|------|------|
| `bazi.py` | 八字排盘：四柱五行分析、合冲刑害、大运计算 |
| `luohou.py` | 罗喉日时计算：九宫飞星、太岁位置 |
| `shengxiao.py` | 生肖合婚：三合/六合/相冲/相刑 |
| `ganzhi.py` | 核心数据：天干/地支/五行/十神/神煞定义 |
| `sizi.py` | 命理文本：《三命通会》《穷通宝鉴》解读 |
| `datas.py` | 参考数据：纳音五行、星宿、建除十二神 |

**依赖:** `bidict`, `lunar_python`, `colorama`, `sxtwl`

---

## 二、现状问题诊断

| 环节 | 当前状态 | 问题根因 |
|------|---------|---------|
| **数据管理** | 所有数据以全局字典/列表散落定义在 `ganzhi.py` 和各模块中 | 无数据层抽象，无法复用 |
| **万年历依赖** | 直接依赖 `lunar_python`、`sxtwl`、`bidict` 三个外部库，无缓存 | 每次计算重复调用 |
| **十神系统** | `ten_deities` 是 bidict 字典，但查询逻辑分散在 `bazi.py` 的 `get_gen()` 中 | 未封装，逻辑冗余 |
| **神煞系统** | `year_shens`/`month_shens`/`day_shens`/`g_shens` 硬编码在 `datas.py` 中，数据量大且无索引 | 查询 O(n) 线性扫描 |
| **合冲刑害** | `zhi_atts`/`gan_hes`/`zhi_6hes` 等关系数据独立存储 | 无法联合查询（例：查某地支的所有关系） |
| **命令行接口** | 每个功能独立一个入口文件（bazi.py/luohou.py/shengxiao.py/convert.py），无统一入口 | 用户使用碎片化 |
| **文本解读** | `sizi.py` 中 `summarys` 是静态字符串，无结构化标签 | 无法做智能检索 |
| **大运计算** | `dayuns` 在 `bazi.py` 中线性计算，无缓存 | 重复计算耗时 |

---

## 三、优化方案

### P0：数据层重构 - 建立索引化的数据结构

**为什么要这样做：**

当前 `ganzhi.py` 中 `ten_deities` 是10个独立 bidict，每个干支查十神需要：
```python
ten_deities[gan]['本']   # 查五行归属
ten_deities[gan]['克']   # 查所克五行
```

这种设计导致：
1. 无法批量查询（例如：查"所有克金的干支"）
2. 关系查询（合/冲/刑/害）散落在多个字典中
3. 神煞查询是 O(n) 线性扫描

**优化方案：**

```python
# 建立中心化的五行-干支关系索引
class WuxingIndex:
    """五行索引 - 从任意角度快速查询干支关系"""

    # 五行 → 对应天干/地支集合
    wuhang_stems = {"金": {"庚", "辛"}, "木": {"甲", "乙"}, ...}
    wuhang_branches = {"金": {"申", "酉"}, ...}

    # 天干 → 五行
    stem_wuhang = {gan: wuhang for wuhang, stems in wuhang_stems.items() for gan in stems}

    # 任意查：某五行的强弱（通根/中根/余气）
    def query_by_wuhang(self, wuhang: str) -> dict:
        # 返回 {gan: {root_strength, ...}}
```

神煞系统同样建立哈希索引（以地支为键）：
```python
day_shens_index = {zhi: [shen1, shen2, ...] for shen, zhi_map in day_shens.items() for zhi in zhi_map[...]}
```

---

### P1：万年历缓存层

**为什么要这样做：**

`lunar_python` 和 `sxtwl` 的转换计算并不轻量。在批量计算时，重复调用造成浪费。

**优化方案：**

```python
class LunarCache:
    """万年历缓存 - 基于文件/LRU 的二次缓存"""

    _cache = {}
    _cache_file = ".bazi_cache.pkl"

    def solar_to_lunar(self, year, month, day):
        key = (year, month, day)
        if key in self._cache:
            return self._cache[key]
        result = lunar_python.Solar.fromYmd(year, month, day).getLunar()
        self._cache[key] = result
        return result
```

---

### P2：统一 CLI 入口

**为什么要这样做：**

当前 `bazi.py`、`luohou.py`、`shengxiao.py`、`convert.py` 是四个独立入口，用户无法用单一命令调用所有功能。

**优化方案：**

```bash
python -m bazi --type bazi      # 八字排盘
python -m bazi --type luohou    # 罗喉日时
python -m bazi --type shengxiao # 生肖合婚
python -m bazi --type convert   # 格式转换
python -m bazi --type dashi     # 大运流年分析
```

---

### P3：文本解读结构化

**为什么要这样做：**

`sizi.py` 中 `summarys` 是大字文本块，包含 `# 2-86`、`# 1-155` 等标签但未解析。这些标签代表命局特征，无法基于标签检索。

**优化方案：**

```python
summarysStructured = {
    '甲日甲子': {
        'text': '''六甲日生甲子时...''',
        'tags': ['印绶', '丑绊午冲', '贵格'],
        'refs': [{'type': '2-86', 'desc': '天月德贵人'}, ...],
        'cases': ['甲寅日甲子时', '甲午日甲子时'],
    }
}
```

---

## 四、实现优先级与预期收益

| 优先级 | 优化项 | 预期收益 | 难度 |
|--------|-------|---------|------|
| **P0** | 数据层重构（WuxingIndex + 神煞索引） | 查询效率提升，代码复用 | 中 |
| **P1** | LunarCache 缓存层 | 批量计算性能提升 | 低 |
| **P2** | 统一 CLI 入口 | 用户体验统一 | 低 |
| **P3** | sizi.py 文本结构化 | 智能检索能力 | 中 |

**核心逻辑：** P0 是一切后续优化的基础——当前散落的数据结构无法支撑高效查询和智能检索。先建立索引化的数据层，P1/P2/P3 都能在此基础上自然延伸。

---

## 五、技术实现记录

### P0 实现清单
- [x] `data.py` - `WuxingIndex` 类：五行/干支关系索引
- [x] `data.py` - `ShenShaIndex` 类：神煞 O(1) 查询索引
- [x] `data.py` - `query_all_shens()` / `query_column_shens()` 兼容层
- [x] `data.py` - `_build_shensha_index()` 延迟加载 + 索引构建
- [x] `test_bazi.py` - 单元测试覆盖（P0 相关测试）

### P1 实现清单
- [x] `cache.py` - `LunarCache` 类：万年历二次缓存（LRU + 磁盘持久化）
- [x] `cache.py` - `cached_solar_to_lunar()` 带缓存的公历转农历
- [x] `cache.py` - `cached_sxtwl_solar_to_ganzhi()` 带缓存的 sxtwl 干支计算
- [x] `test_bazi.py` - 单元测试覆盖（P1 相关测试）

### P2 实现清单
- [x] `cli.py` - 统一 CLI 入口框架（`argparse` 子命令模式）
- [x] `cli.py` - 子命令注册装饰器 `@subcommand`
- [x] `cli.py` - `bazi/luohou/shengxiao/convert` 子命令路由
- [x] `cli.py` - `cache-clear/cache-info` 缓存管理子命令
- [x] `cli.py` - `search` 命例检索子命令
- [x] `cli.py` - 通过 `subprocess` 调用原始模块，保持向后兼容
- [x] `test_bazi.py` - 单元测试覆盖（P2 相关测试）

### P3 实现清单
- [x] `sizi_parser.py` - `SiziEntry`/`SiziRef`/`SiziCase` 结构化数据模型
- [x] `sizi_parser.py` - `REF_PATTERN` / `CASE_PATTERN` 注释标签解析
- [x] `sizi_parser.py` - `SiziParser.build_index()` 全文索引构建
- [x] `sizi_parser.py` - `SiziParser.search()` 标签/五行/关键词检索
- [x] `cli.py` - `search` 子命令集成检索 API
- [x] `test_bazi.py` - 单元测试覆盖（P3 相关测试）

### 测试清单
- [x] 33 项单元测试全部通过
- [x] `test_bazi.py` 覆盖 data.py / cache.py / sizi_parser.py / cli.py
