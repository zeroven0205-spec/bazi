# -*- coding: utf-8 -*-
"""
bazi.cache - 万年历二次缓存
基于 LRU 和文件持久化的 Solar/Lunar 转换缓存
"""

import os
import pickle
import time
import threading
from typing import Optional, Tuple, Dict, Any
from functools import lru_cache

# 缓存配置
CACHE_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_FILE = os.path.join(CACHE_DIR, ".bazi_lunar_cache.pkl")
CACHE_MAX_SIZE = 10000  # 最大缓存条目数
CACHE_TTL_SECONDS = 7 * 24 * 3600  # 缓存有效期 7 天


class LunarCache:
    """万年历缓存 - Solar/Lunar 转换的二次缓存"""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        """单例模式，保证全局只有一个缓存实例"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._cache: Dict[Tuple, Dict[str, Any]] = {}
        self._access_times: Dict[Tuple, float] = {}
        self._load_from_disk()

    def _load_from_disk(self):
        """从磁盘加载缓存"""
        if not os.path.exists(CACHE_FILE):
            return

        try:
            mtime = os.path.getmtime(CACHE_FILE)
            if time.time() - mtime > CACHE_TTL_SECONDS:
                # 缓存过期，删除
                os.remove(CACHE_FILE)
                return

            with open(CACHE_FILE, "rb") as f:
                data = pickle.load(f)
                self._cache = data.get("cache", {})
                self._access_times = data.get("access_times", {})
        except (OSError, pickle.PickleError):
            pass

    def _save_to_disk(self):
        """持久化缓存到磁盘"""
        try:
            with open(CACHE_FILE, "wb") as f:
                pickle.dump({
                    "cache": self._cache,
                    "access_times": self._access_times,
                }, f)
        except OSError:
            pass

    def _evict_if_needed(self):
        """LRU 淘汰超出容量的条目"""
        if len(self._cache) <= CACHE_MAX_SIZE:
            return

        # 按访问时间排序，淘汰最老的 20%
        sorted_items = sorted(self._access_times.items(), key=lambda x: x[1])
        evict_count = CACHE_MAX_SIZE // 5
        for key, _ in sorted_items[:evict_count]:
            del self._cache[key]
            del self._access_times[key]

    def get(self, key: Tuple) -> Optional[Dict[str, Any]]:
        """
        获取缓存

        Args:
            key: (year, month, day) 元组

        Returns:
            缓存的数据，或 None
        """
        if key in self._cache:
            self._access_times[key] = time.time()
            return self._cache[key]
        return None

    def set(self, key: Tuple, value: Dict[str, Any]):
        """
        设置缓存

        Args:
            key: (year, month, day) 元组
            value: 缓存的数据
        """
        self._evict_if_needed()
        self._cache[key] = value
        self._access_times[key] = time.time()

    def clear(self):
        """清空缓存"""
        self._cache.clear()
        self._access_times.clear()
        if os.path.exists(CACHE_FILE):
            os.remove(CACHE_FILE)


# ============================================================
# 缓存感知的天干地支计算
# ============================================================

def cached_solar_to_lunar(year: int, month: int, day: int) -> Dict[str, Any]:
    """
    带缓存的公历转农历计算

    Args:
        year: 公历年
        month: 公历月
        day: 公历日

    Returns:
        dict: {
            'lunar_year': int,
            'lunar_month': int,
            'lunar_day': int,
            'is_leap': bool,
            'jieqi': str or None,
        }
    """
    cache = LunarCache()
    key = (year, month, day)

    cached = cache.get(key)
    if cached is not None:
        return cached

    # 未命中，执行真实计算
    try:
        from lunar_python import Solar, Lunar

        solar = Solar.fromYmd(year, month, day)
        lunar = solar.getLunar()

        result = {
            "lunar_year": lunar.getYear(),
            "lunar_month": lunar.getMonth(),
            "lunar_day": lunar.getDay(),
            "is_leap": lunar.isLunarLeap(),
            "jieqi": None,  # 按需计算
        }

        # 检查节气（如果需要）
        try:
            if solar.hasJieQi():
                result["jieqi"] = solar.getJieQi()
        except Exception:
            pass

        cache.set(key, result)
        return result

    except Exception as e:
        return {"error": str(e)}


def cached_sxtwl_solar_to_ganzhi(year: int, month: int, day: int, hour: int = None) -> Dict[str, Any]:
    """
    带缓存的 sxtwl 公历转干支计算

    Args:
        year: 公历年
        month: 公历月
        day: 公历日
        hour: 小时（可选，0-23）

    Returns:
        dict: 包含 year/month/day/hour 干支的字典
    """
    try:
        import sxtwl

        key = (year, month, day, hour or 0)
        cache = LunarCache()

        cached = cache.get(key)
        if cached is not None:
            return cached

        day_obj = sxtwl.fromSolar(year, month, day)

        result = {
            "year_gz": sxtwl.GZ(day_obj.getYearGZ().tg, day_obj.getYearGZ().dz) if day_obj.getYearGZ() else None,
            "month_gz": sxtwl.GZ(day_obj.getMonthGZ().tg, day_obj.getMonthGZ().dz) if day_obj.getMonthGZ() else None,
            "day_gz": sxtwl.GZ(day_obj.getDayGZ().tg, day_obj.getDayGZ().dz) if day_obj.getDayGZ() else None,
            "hour_gz": sxtwl.GZ(day_obj.getHourGZ(hour or 10).tg, day_obj.getHourGZ(hour or 10).dz) if hour is not None else None,
        }

        cache.set(key, result)
        return result

    except Exception as e:
        return {"error": str(e)}


# ============================================================
# 全局缓存实例
# ============================================================

_lunar_cache = None


def get_lunar_cache() -> LunarCache:
    """获取全局 LunarCache 实例"""
    global _lunar_cache
    if _lunar_cache is None:
        _lunar_cache = LunarCache()
    return _lunar_cache
