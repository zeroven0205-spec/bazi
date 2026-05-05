#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
bazi tests - 单元测试
测试 data.py, cache.py, sizi_parser.py, cli.py
"""

import unittest
import os
import sys
import tempfile
import pickle
from pathlib import Path

# 确保 bazi 目录在路径中
_bazi_dir = os.path.dirname(os.path.abspath(__file__))
if _bazi_dir not in sys.path:
    sys.path.insert(0, _bazi_dir)


class TestWuxingIndex(unittest.TestCase):
    """测试 WuxingIndex 五行索引"""

    def setUp(self):
        from data import WuxingIndex
        self.wuxing = WuxingIndex()

    def test_stem_wuhang(self):
        """测试天干→五行映射"""
        self.assertEqual(self.wuxing.stem_wuhang["甲"], "木")
        self.assertEqual(self.wuxing.stem_wuhang["庚"], "金")
        self.assertEqual(self.wuxing.stem_wuhang["壬"], "水")

    def test_wuhang_stems(self):
        """测试五行→天干集合"""
        stems = self.wuxing.get_stems_by_wuhang("木")
        self.assertIn("甲", stems)
        self.assertIn("乙", stems)
        self.assertNotIn("丙", stems)

    def test_wuhang_branches(self):
        """测试五行→地支集合"""
        branches = self.wuxing.get_branches_by_wuhang("金")
        self.assertIn("申", branches)
        self.assertIn("酉", branches)

    def test_gan_he(self):
        """测试天干相合"""
        self.assertTrue(self.wuxing.check_gan_he("甲", "己"))
        self.assertTrue(self.wuxing.check_gan_he("己", "甲"))
        self.assertFalse(self.wuxing.check_gan_he("甲", "庚"))

    def test_gan_chong(self):
        """测试天干相冲"""
        self.assertTrue(self.wuxing.check_gan_chong("甲", "庚"))
        self.assertTrue(self.wuxing.check_gan_chong("庚", "甲"))
        self.assertFalse(self.wuxing.check_gan_chong("甲", "己"))

    def test_zhi_he(self):
        """测试地支相合"""
        self.assertEqual(self.wuxing.check_zhi_he("子", "丑"), "土")
        self.assertEqual(self.wuxing.check_zhi_he("丑", "子"), "土")

    def test_zhi_chong(self):
        """测试地支相冲"""
        self.assertTrue(self.wuxing.check_zhi_chong("子", "午"))
        self.assertTrue(self.wuxing.check_zhi_chong("午", "子"))
        self.assertFalse(self.wuxing.check_zhi_chong("子", "丑"))

    def test_zhi_xing(self):
        """测试地支相刑"""
        self.assertTrue(self.wuxing.check_zhi_xing("寅", "巳"))
        self.assertTrue(self.wuxing.check_zhi_xing("巳", "申"))
        self.assertFalse(self.wuxing.check_zhi_xing("子", "丑"))

    def test_zhi_hai(self):
        """测试地支相害"""
        self.assertTrue(self.wuxing.check_zhi_hai("子", "未"))
        self.assertFalse(self.wuxing.check_zhi_hai("子", "午"))

    def test_zhi_po(self):
        """测试地支相破"""
        self.assertTrue(self.wuxing.check_zhi_po("子", "酉"))
        self.assertTrue(self.wuxing.check_zhi_po("午", "卯"))
        self.assertFalse(self.wuxing.check_zhi_po("子", "丑"))

    def test_calc_root_strength(self):
        """测试通根强弱计算"""
        # 甲日主，在寅卯辰亥四支中，寅藏甲丙戊，甲为本气有强根
        result = self.wuxing.calc_root_strength("甲", ["寅", "卯", "辰", "亥"])
        # 寅为甲的帝旺之地，应有强根；亥有中气根；卯无根；辰无根
        self.assertIn("强", result)
        self.assertIn("寅", result["强"])

    def test_calc_root_strength_no_root(self):
        """测试无根情况"""
        result = self.wuxing.calc_root_strength("丙", ["子", "卯", "午", "亥"])
        # 丙火在子卯午亥中均无通根，结果中"强"应为空列表或不存在
        self.assertTrue(len(result.get("强", [])) == 0)

    def test_query_zhi_all_relations(self):
        """测试地支全关系查询"""
        relations = self.wuxing.query_zhi_all_relations("子")
        self.assertIn("冲", relations)
        self.assertIn("刑", relations)
        self.assertIn("合", relations)

    def test_query_gan_relations(self):
        """测试天干关系查询"""
        relations = self.wuxing.query_gan_relations("甲")
        self.assertEqual(relations["合"], "己")
        self.assertEqual(relations["冲"], "庚")


class TestShenShaIndex(unittest.TestCase):
    """测试 ShenShaIndex 神煞索引"""

    def setUp(self):
        from data import ShenShaIndex
        self.shensha = ShenShaIndex()

    def test_build_year_index(self):
        """测试年煞索引构建"""
        year_shens = {
            "驿马": {"子": ["午"], "寅": ["申"], "卯": ["亥"]},
        }
        self.shensha.build_year_index(year_shens)
        result = self.shensha.query_year_shens("子")
        self.assertIn("驿马", result)

    def test_build_day_index(self):
        """测试日煞索引构建"""
        day_shens = {
            "天乙": {"子": ["丑"], "午": ["未"]},
        }
        self.shensha.build_day_index(day_shens)
        result = self.shensha.query_day_shens("子")
        self.assertIn("天乙", result)


class TestLunarCache(unittest.TestCase):
    """测试 LunarCache 万年历缓存"""

    def setUp(self):
        from cache import LunarCache
        # 创建临时缓存文件
        self.temp_dir = tempfile.mkdtemp()
        self.cache_file = os.path.join(self.temp_dir, ".bazi_lunar_cache.pkl")

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_cache_set_get(self):
        """测试缓存存取"""
        from cache import LunarCache
        cache = LunarCache()

        test_data = {"lunar_year": 1990, "lunar_month": 3, "lunar_day": 15}
        cache.set((1990, 3, 15), test_data)

        result = cache.get((1990, 3, 15))
        self.assertEqual(result, test_data)

    def test_cache_miss(self):
        """测试缓存未命中"""
        from cache import LunarCache
        cache = LunarCache()

        result = cache.get((9999, 1, 1))
        self.assertIsNone(result)

    def test_cache_clear(self):
        """测试缓存清空"""
        from cache import LunarCache
        cache = LunarCache()

        cache.set((1990, 3, 15), {"test": True})
        cache.clear()

        result = cache.get((1990, 3, 15))
        self.assertIsNone(result)


class TestSiziParser(unittest.TestCase):
    """测试 SiziParser 四柱命理文本解析器"""

    def setUp(self):
        from sizi_parser import SiziParser
        self.parser = SiziParser()

        # 加载测试数据
        self.test_summarys = {
            "甲日甲子": '''
            六甲日生甲子时，败中印绶官生至；月通木气不寻常，反此而言虚名利。
            甲子日甲子时，子遥巳格，年月无庚辛申酉，丑绊午冲，离祖自立，贵。
            # 2-86有天月德贵人、通根于月、有权。
            # 1-155正印旺，女不靠子女
            ''',
            "甲日乙丑": '''
            六甲日生时乙丑,劫财羊刃不宜有; 柱中逢火带辛金,制伏和平贵亦久。
            甲子日乙丑时,连珠得合妻贤子贵。春月身旺,财帛破散。夏月甲衰,金神有制,贵。
            ''',
        }
        self.parser.build_index(self.test_summarys)

    def test_parse_text_extracts_wuhang(self):
        """测试解析提取日主五行"""
        entry = self.parser.get_by_key("甲日甲子")
        self.assertEqual(entry.wuhang, "木")

    def test_parse_text_extracts_refs(self):
        """测试解析提取文献引用"""
        entry = self.parser.get_by_key("甲日甲子")
        self.assertTrue(len(entry.refs) >= 1)
        ref_codes = [r.code for r in entry.refs]
        self.assertIn("2-86", ref_codes)

    def test_build_index(self):
        """测试索引构建"""
        self.assertEqual(len(self.parser.entries), 2)
        self.assertIn("甲日甲子", self.parser.entries)

    def test_search_by_tags(self):
        """测试标签检索"""
        results = self.parser.search(tags=["贵格"])
        self.assertGreaterEqual(len(results), 1)

    def test_search_by_wuhang(self):
        """测试五行检索"""
        results = self.parser.search(wuhang="木")
        self.assertGreaterEqual(len(results), 1)
        for entry in results:
            self.assertEqual(entry.wuhang, "木")

    def test_search_combined(self):
        """测试组合检索"""
        results = self.parser.search(wuhang="木", tags=["贵格"])
        for entry in results:
            self.assertEqual(entry.wuhang, "木")
            self.assertIn("贵格", entry.tags)

    def test_search_keyword(self):
        """测试关键词检索"""
        results = self.parser.search(keyword="甲子")
        self.assertGreaterEqual(len(results), 1)

    def test_list_tags(self):
        """测试标签列表"""
        tags = self.parser.list_tags()
        self.assertIsInstance(tags, list)

    def test_tags_extraction(self):
        """测试标签自动提取"""
        entry = self.parser.get_by_key("甲日甲子")
        self.assertIsInstance(entry.tags, list)


class TestCliSubcommands(unittest.TestCase):
    """测试 CLI 子命令注册"""

    def test_subcommands_registered(self):
        """测试子命令是否已注册"""
        from cli import SUBCOMMANDS

        expected = ["bazi", "luohou", "shengxiao", "convert", "dashi", "search", "cache-clear", "cache-info"]
        for cmd in expected:
            self.assertIn(cmd, SUBCOMMANDS)

    def test_cli_help(self):
        """测试 CLI 帮助信息"""
        import subprocess
        result = subprocess.run(
            ["python3", "cli.py", "--help"],
            capture_output=True,
            text=True
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("bazi", result.stdout)


class TestDataModule(unittest.TestCase):
    """测试 data.py 兼容层"""

    def test_wuxing_singleton(self):
        """测试 wuxing 单例"""
        from data import wuxing
        self.assertIsNotNone(wuxing)

    def test_shensha_singleton(self):
        """测试 shensha 单例"""
        from data import shensha
        self.assertIsNotNone(shensha)

    def test_query_all_shens_function(self):
        """测试 query_all_shens 兼容函数"""
        from data import query_all_shens
        # 无数据时返回空列表
        result = query_all_shens(("甲", "乙", "丙", "丁"), ("子", "丑", "寅", "卯"), "丙")
        self.assertIsInstance(result, list)


def run_tests():
    """运行所有测试"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # 添加测试类
    suite.addTests(loader.loadTestsFromTestCase(TestWuxingIndex))
    suite.addTests(loader.loadTestsFromTestCase(TestShenShaIndex))
    suite.addTests(loader.loadTestsFromTestCase(TestLunarCache))
    suite.addTests(loader.loadTestsFromTestCase(TestSiziParser))
    suite.addTests(loader.loadTestsFromTestCase(TestCliSubcommands))
    suite.addTests(loader.loadTestsFromTestCase(TestDataModule))

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
