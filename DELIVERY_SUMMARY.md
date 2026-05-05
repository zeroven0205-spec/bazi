# bazi 项目优化交付文档

> 文档版本: v1.0
> 交付时间: 2026-05-05
> 状态: 已完成

---

## 一、项目信息

| 项目 | 内容 |
|------|------|
| 项目名称 | bazi (八字) - 中国传统命理计算工具集 |
| 项目路径 | `/Users/zero_ven/Downloads/claude-code/bazi` |
| 原始模块 | `bazi_calc.py`, `luohou.py`, `shengxiao.py`, `convert.py`, `ganzhi.py`, `sizi.py`, `datas.py` |

---

## 二、新增文件清单

| 文件 | 类型 | 说明 |
|------|------|------|
| `BAZI_OPTIMIZATION.md` | 文档 | 完整优化方案文档（含问题诊断、实现方案、技术记录） |
| `data.py` | 模块 | `WuxingIndex`（五行索引）+ `ShenShaIndex`（神煞索引）+ 兼容层 |
| `cache.py` | 模块 | `LunarCache`（LRU缓存）+ `cached_solar_to_lunar()` + `cached_sxtwl_solar_to_ganzhi()` |
| `cli.py` | 模块 | 统一 CLI 入口（8个子命令：bazi/luohou/shengxiao/convert/dashi/search/cache-clear/cache-info） |
| `sizi_parser.py` | 模块 | 命理文本结构化解析器（`SiziEntry`/`SiziRef`/`SiziCase` + 标签检索） |
| `test_bazi.py` | 测试 | 33项单元测试，覆盖 data.py / cache.py / sizi_parser.py / cli.py |

---

## 三、重命名文件清单

| 原名称 | 新名称 | 原因 |
|--------|--------|------|
| `bazi.py` | `bazi_calc.py` | 避免与 `bazi` 包名冲突 |

---

## 四、修改文件清单

| 文件 | 修改内容 |
|------|---------|
| `README.md` | 新增统一 CLI 章节，更新命令格式（`$ python` → `python3`），更新依赖（增加 `sxtwl`） |

---

## 五、优化模块说明

### 5.1 data.py - 数据层重构

**`WuxingIndex` 类**
- 天干/地支 → 五行双向映射
- 五行 → 天干/地支集合查询
- 天干相合/相冲关系
- 地支合/冲/刑/害/破/三合/三会查询
- 通根强弱计算（替代原 `get_gen()`）

**`ShenShaIndex` 类**
- 神煞哈希索引构建（O(1) 查询）
- 年煞/月煞/日煞/时煞分离索引

**兼容层函数**
- `query_all_shens()` - 查询八字所有神煞
- `query_column_shens()` - 查询每柱神煞字符串
- `_build_shensha_index()` - 延迟加载 + 索引构建

### 5.2 cache.py - 缓存层

**`LunarCache` 类**
- 单例模式
- LRU 淘汰策略（最大 10000 条）
- 磁盘持久化（7 天 TTL）
- `clear()` 清空缓存

**缓存函数**
- `cached_solar_to_lunar()` - 带缓存的公历转农历
- `cached_sxtwl_solar_to_ganzhi()` - 带缓存的 sxtwl 干支计算
- `get_lunar_cache()` - 全局缓存实例获取

### 5.3 cli.py - 统一 CLI

**子命令**
| 子命令 | 功能 | 调用方式 |
|--------|------|---------|
| `bazi` | 八字排盘 | `python3 cli.py bazi 1990 3 15 19 -n` |
| `luohou` | 罗喉日时 | `python3 cli.py luohou -d "2024 1 1" -n 7` |
| `shengxiao` | 生肖合婚 | `python3 cli.py shengxiao 虎` |
| `convert` | 格式转换 | `python3 cli.py convert 甲 子` |
| `dashi` | 大运流年 | `python3 cli.py dashi ...` (开发中) |
| `search` | 命例检索 | `python3 cli.py search --wuhang 木 --tags 贵格 --limit 5` |
| `cache-clear` | 清空缓存 | `python3 cli.py cache-clear` |
| `cache-info` | 缓存状态 | `python3 cli.py cache-info` |

### 5.4 sizi_parser.py - 文本结构化

**数据模型**
- `SiziEntry` - 结构化命理条目（key/text/tags/refs/cases/wuhang/pattern）
- `SiziRef` - 文献引用（code/desc）
- `SiziCase` - 命例片段（ganzhi/desc）

**解析功能**
- 注释标签解析（`# 2-86` → `SiziRef`）
- 命例片段提取（`甲寅日甲子时，...` → `SiziCase`）
- 自动标签提取（贵格/富格/凶格/春/秋 等）
- 日主五行提取

**检索功能**
- `search(tags=, wuhang=, keyword=, limit=)` - 组合检索
- `list_tags()` - 所有标签列表
- `list_by_wuhang()` - 按五行筛选

---

## 六、单元测试

```bash
cd /Users/zero_ven/Downloads/claude-code/bazi
python3 test_bazi.py
```

**测试结果**: 33 项测试全部通过

| 测试类 | 测试数量 | 覆盖内容 |
|--------|---------|---------|
| `TestWuxingIndex` | 12 | 五行索引、天干相合/相冲、地支合/冲/刑/害/破、通根强弱 |
| `TestShenShaIndex` | 2 | 神煞索引构建 |
| `TestLunarCache` | 3 | 缓存存取/未命中/清空 |
| `TestSiziParser` | 9 | 文本解析、标签提取、索引构建、组合检索 |
| `TestCliSubcommands` | 2 | 子命令注册、CLI 帮助 |
| `TestDataModule` | 3 | 单例、兼容层函数 |

---

## 七、使用方式

### 统一 CLI（推荐）

```bash
cd /Users/zero_ven/Downloads/claude-code/bazi

# 八字排盘
python3 cli.py bazi 1990 3 15 19 -n

# 罗喉日时
python3 cli.py luohou -d "2024 1 1" -n 7

# 生肖合婚
python3 cli.py shengxiao 虎

# 命例检索
python3 cli.py search --wuhang 木 --tags 贵格 --limit 5

# 缓存管理
python3 cli.py cache-info
python3 cli.py cache-clear

# 帮助
python3 cli.py --help
python3 cli.py search --help
```

### 各模块独立使用

```bash
# 生肖合婚
python3 shengxiao.py 虎

# 罗喉日时
python3 luohou.py

# 八字排盘（原方式）
python3 bazi_calc.py 1990 3 15 19 -n
```

---

## 八、依赖

```bash
pip3 install bidict lunar_python colorama sxtwl
```

---

## 九、文件结构

```
bazi/
├── README.md                  # 更新：统一 CLI 用法
├── BAZI_OPTIMIZATION.md       # 优化方案文档
├── DELIVERY_SUMMARY.md        # 本文档
├── cli.py                     # 统一 CLI 入口
├── data.py                    # 五行索引 + 神煞索引
├── cache.py                   # 万年历缓存
├── sizi_parser.py             # 命理文本结构化
├── test_bazi.py               # 单元测试（33项）
├── bazi_calc.py               # 原 bazi.py（重命名）
├── luohou.py                  # 原罗喉日时
├── shengxiao.py               # 原生肖合婚
├── convert.py                 # 原格式转换
├── ganzhi.py                  # 核心数据定义
├── sizi.py                    # 命理文本
├── datas.py                   # 参考数据
├── yue.py                     # 月份数据
├── common.py                  # 工具函数
├── books/                     # 参考书籍
└── examples/                  # 命例
```
