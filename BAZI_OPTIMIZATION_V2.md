# bazi 项目优化迭代方案 v2.0

> 文档版本: v2.0
> 创建时间: 2026-05-17
> 状态: 规划中

---

## 一、项目现状评估

### 1.1 已完成的优化（v1.0）

根据 `BAZI_OPTIMIZATION.md` 和 `DELIVERY_SUMMARY.md`，上一轮已完成：

| 模块 | 完成情况 | 说明 |
|------|---------|------|
| `data.py` | ✅ | `WuxingIndex` + `ShenShaIndex` + 兼容层 |
| `cache.py` | ✅ | `LunarCache` LRU + 磁盘持久化 |
| `cli.py` | ✅ | 统一 CLI（8个子命令） |
| `sizi_parser.py` | ✅ | 命理文本结构化 + 检索 API |
| `bazi.py` → `bazi_calc.py` | ✅ | 重命名避免冲突 |

### 1.2 核心问题诊断（v2.0）

**bazi_calc.py 的问题：**

1. **单文件过大** - 2500+ 行，所有逻辑堆在一个文件里，修改成本高，容易改出 bug
2. **未复用优化成果** - `data.py` 和 `cache.py` 已完成，但 `bazi_calc.py` 仍在直接调用 `datas.py` 和原始库
3. **输出强依赖终端** - 大量 `\033[1;36;40m` 颜色转义码，无法输出到文件/Web/API
4. **神煞信息硬编码** - `shens_infos` 等字典直接硬编码在文件中
5. **十神系统未复用** - 原 `ganzhi.py` 中 `ten_deities` 10 个 bidict 未被 `data.py` 的 `WuxingIndex` 替代
6. **命理解读文本缺失结构化** - `sizi.py` 的 `summarys` 约 3000 行文本没有接入 `sizi_parser.py`

---

## 二、优化迭代方案

### P0：bazi_calc.py 重构 - 拆分为模块化架构

**目标：** 把 2500+ 行的 `bazi_calc.py` 拆成多个可维护的模块

```
bazi_calc/
├── __init__.py           # 模块导出
├── calculator.py         # 核心计算引擎（八字排盘逻辑）
├── wuxing.py             # 五行分数计算
├── dayun.py              # 大运计算
├── shensha.py            # 神煞系统（使用 data.py 的索引）
├── mingli.py             # 命理分析（比肩/劫财/偏印等）
├── formatter.py          # 输出格式化（终端/JSON/HTML）
└── main.py               # CLI 入口（调用 calculator.py）
```

**优先级说明：**
- `calculator.py` 是重构的核心，其他模块依赖它
- `formatter.py` 分离后，可以同时支持终端颜色输出和 JSON/API 输出
- 完成后，`bazi_calc.py` 可以删除或降级为兼容层

---

### P1：接入已有优化模块

**1.1 接入 data.py**

现状：`bazi_calc.py` 直接从 `datas.py` 导入数据

目标：使用 `data.py` 的索引层

```python
# 现状
from datas import ten_deities, zhi5, zhi_atts, ...

# 目标
from data import wuxing, shensha, query_all_shens
```

**1.2 接入 cache.py**

现状：每次调用 `lunar_python` 实时计算

目标：使用 `cached_solar_to_lunar()` 缓存

---

### P2：输出格式化分离

**现状：** 终端颜色代码散落在各处

```python
# 现状
print('\033[1;36;40m' + ' '.join(list(gans)) + '\033[0m')
```

**目标：** formatter.py 统一处理

```python
from formatter import TerminalFormatter, JsonFormatter

formatter = TerminalFormatter()
print(formatter.format_gans(gans, gan_shens))

formatter = JsonFormatter()
print(formatter.format_gans(gans, gan_shens))
```

支持多种输出格式：
- `terminal` - 终端颜色输出（默认）
- `json` - JSON 格式（API 用）
- `html` - HTML 格式（Web 用）
- `plain` - 无颜色纯文本

---

### P3：十神系统重构

**现状：** `ganzhi.py` 中 `ten_deities` 是 10 个独立 bidict

```python
ten_deities = {
    '甲': bidict({'本': '木', '克': '金', ...}),
    '乙': bidict({'本': '木', '克': '金', ...}),
    ...
}
```

**目标：** 统一 `WuxingIndex.ten_deities`，并迁移到 `data.py`

```python
class TenDeities:
    """十神系统 - 基于日主计算十神"""

    def __init__(self, me: str):
        self.me = me
        self.ten_deities = self._build_deities()

    def get(self, gan_or_zhi: str, attr: str) -> str:
        """查某干支的十神属性"""
        ...

    def get_shens(self, gan: str, zhi: str) -> str:
        """查某柱的神（天干神 + 地支主气神）"""
        ...
```

---

### P4：命理文本结构化接入

**现状：** `sizi.py` 的 `summarys` 是静态文本，`sizi_parser.py` 已完成但未在 `bazi_calc.py` 中使用

**目标：** 在八字分析中实时调用

```python
from sizi_parser import get_sizi_parser, init_sizi_index
from sizi import summarys

# 初始化索引
init_sizi_index(summarys)

# 查询日柱命理解读
parser = get_sizi_parser()
entry = parser.get_by_key('甲日甲子')
if entry:
    print(entry.text)
    print(f"标签: {entry.tags}")
    print(f"文献引用: {entry.refs}")
```

---

### P5：大运流年模块开发

**现状：** `cli.py` 中 `dashi` 子命令提示"开发中"

**目标：** 完成大运流年分析功能

```
dashi/
├── dayun.py              # 大运计算（已部分在 bazi_calc.py）
├── liunian.py            # 流年分析
├── mingli_analysis.py     # 命理综合分析
└── main.py               # CLI 入口
```

---

## 三、技术债务清理

### 3.1 代码重复

`luohou.py` 中定义了 `Gans`/`Zhis` namedtuple，与 `bazi_calc.py` 中相同：

```python
# luohou.py
Gans = collections.namedtuple("Gans", "year month day")
Zhis = collections.namedtuple("Zhis", "year month day")

# bazi_calc.py
Gans = collections.namedtuple("Gans", "year month day time")
Zhis = collections.namedtuple("Zhis", "year month day time")
```

**建议：** 统一迁移到 `data.py`

```python
# data.py
Gans = namedtuple("Gans", "year month day time")
Gans3 = namedtuple("Gans3", "year month day")  # 三字版本（luohou 用）
Zhis = namedtuple("Zhis", "year month day time")
Zhis3 = namedtuple("Zhis3", "year month day")
```

### 3.2 神煞信息硬编码

`shens_infos` 等字典应该迁移到 `datas.py`：

```python
# 现状：硬编码在 bazi_calc.py 某行附近
shens_infos = {
    '驿马': '多迁移、水准与命格相关...',
    '天乙': '后天解难、女命不适合多',
    ...
}
```

**目标：** 迁移到 `datas.py` 统一管理

### 3.3 硬编码常量

多处硬编码的索引/映射应该集中管理：

```python
# 现状：散落在文件中
Gan = ["甲", "乙", ...]
Zhi = ["子", "丑", ...]
gan5 = {...}
```

**目标：** 全部迁移到 `data.py`，其他模块只从 `data.py` 导入

---

## 四、优先级与时间估算

| 优先级 | 优化项 | 预期收益 | 难度 | 工作量 |
|--------|-------|---------|------|--------|
| **P0** | bazi_calc.py 模块化拆分 | 可维护性大幅提升 | 高 | 3-4 天 |
| **P1** | 接入 data.py + cache.py | 复用已有优化成果 | 中 | 1-2 天 |
| **P2** | 输出格式化分离 | 支持多端输出 | 中 | 1 天 |
| **P3** | 十神系统重构 | 代码复用 | 中 | 1 天 |
| **P4** | 命理文本接入 | 智能检索能力落地 | 低 | 0.5 天 |
| **P5** | 大运流年模块 | 功能完整性 | 高 | 2-3 天 |
| **Tech Debt** | 技术债务清理 | 长期可维护性 | 低 | 0.5 天 |

---

## 五、关键约束

1. **向后兼容** - CLI 接口不变（`python3 cli.py bazi ...` 格式不变）
2. **测试覆盖** - 每一步重构后运行 `test_bazi.py` 确保不破坏功能
3. **渐进式** - 每次只重构一个小模块，验证通过后再继续

---

## 六、可选增强方向（超出 v2.0 范围）

| 方向 | 说明 |
|------|------|
| **Web API** | 基于 Flask/FastAPI 提供 HTTP 接口 |
| **GUI 界面** | 使用 PyQt/Tkinter 提供桌面客户端 |
| **命例数据库** | SQLite 存储命例，支持批量分析和统计 |
| **多语言支持** | 输出英文/日文命理解读 |
| **PDF 报告** | 生成格式化的命理分析报告 PDF |