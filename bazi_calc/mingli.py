# -*- coding: utf-8 -*-
"""
bazi_calc.mingli - 命理分析模块
包含详细的八字分析逻辑：官杀分析、食伤分析、财分析、印分析、比劫分析等
从 bazi_calc.py 迁移而来
"""

from typing import List, Dict, Any, Optional, Tuple, Set
from collections import namedtuple

from .types import BaziResult, Dayun
from .bazi_data import BD


# ============================================================
# 命理分析器
# ============================================================

class MingliAnalyzer:
    """
    命理分析器
    
    用法:
        from bazi_calc import BaziCalculator
        from bazi_calc.mingli import MingliAnalyzer
        
        result = BaziCalculator().calculate(1990, 3, 15, 19)
        analyzer = MingliAnalyzer(result)
        for line in analyzer.analyze():
            print(line)
    """
    
    def __init__(self, result: BaziResult, female: bool = False):
        self.result = result
        self.female = female
        self.lines: List[str] = []
        
        # 预加载数据
        self.Gan = BD.Gan()
        self.Zhi = BD.Zhi()
        self.gan5 = BD.gan5()
        self.zhi5 = BD.zhi5()
        self.zhi5_list = BD.zhi5_list()
        self.ten_deities = BD.ten_deities()
        self.zhi_atts = BD.zhi_atts()
        self.temps = BD.temps()
        self.kus = BD.kus()
        self.gong_he = BD.gong_he()
        self.empties = BD.empties()
        self.siling = BD.siling()
        self.jins = BD.jins()
        self.ges = BD.ges()
        self.xiuqius = BD.xiuqius()
        self.zhi_hes = BD.zhi_hes()
        self.zhi_huis = BD.zhi_huis()
        self.nayins = BD.nayins()
        self.tianyis = BD.tianyis()
        self.yutangs = BD.yutangs()
        self.chens = BD.chens()
        self.zhi_6hes = BD.zhi_6hes()
        self.zhi_3hes = BD.zhi_3hes()
        self.zhengs = BD.zhengs()
        
        # 从结果提取常用变量
        self.gans = list(result.gans)
        self.zhis = list(result.zhis)
        self.gan_shens = result.gan_shens
        self.zhi_shens = result.zhi_shens
        self.zhi_shen3 = result.zhi_shen3
        self.me = result.me
        self.scores = result.scores
        self.weak = result.weak
        self.zhi_6he = result.zhi_6he
        self.zhi_6chong = result.zhi_6chong
        self.gan_he = result.gan_he
        self.zhi_xing = result.zhi_xing
        self.all_ges = list(result.all_ges)
        self.jus = list(result.jus)
        self.zhus = list(zip(self.gans, self.zhis))
        
        # 派生变量
        self.zhi_shens2 = self._get_zhi_shens2()
        self.shens2 = list(self.gan_shens) + self.zhi_shens2
        self.me_inv = self.ten_deities[self.me].inverse
        
        # 快捷变量
        self.guan = self.me_inv.get('官', '')
        self.sha = self.me_inv.get('杀', '')
        self.cai = self.me_inv.get('财', '')
        self.cai_di = self.me_inv.get('才', '')
        self.shi = self.me_inv.get('食', '')
        self.shang = self.me_inv.get('伤', '')
        self.me_jue = self.me_inv.get('绝', '')
        self.me_di = self.me_inv.get('帝', '')
        self.me_lu = self.me_inv.get('禄', '')
        self.yin = self.me_inv.get('印', '')
        self.xiao = self.me_inv.get('枭', '')
        
        # 查找禄位
        self.cai_lu = self._find_lu(self.cai)
        self.shi_lu = self._find_lu(self.shi)
        self.shi_di = self._find_di(self.shang)
        self.shang_lu = self._find_lu(self.shang)
        self.shang_di = self._find_di(self.shang)
        self.guan_lu = self._find_lu(self.guan)
        self.sha_lu = self._find_lu(self.sha)
        self.yin_lu = self._find_lu(self.yin)
        self.xiao_lu = self._find_lu(self.xiao)
    
    def _find_lu(self, gan: str) -> str:
        """根据天干找禄位"""
        if not gan:
            return ''
        for zhi in self.Zhi:
            if self.ten_deities[gan][zhi] == '禄':
                return zhi
        return ''
    
    def _find_di(self, gan: str) -> str:
        """根据天干找帝位"""
        if not gan:
            return ''
        for zhi in self.Zhi:
            if self.ten_deities[gan][zhi] == '帝':
                return zhi
        return ''
    
    def _get_zhi_shens2(self) -> List[str]:
        """获取地支所有十神(含余气)"""
        result = []
        for zhi in self.zhis:
            main = max(self.zhi5[zhi], key=self.zhi5[zhi].get)
            result.append(self.ten_deities[self.me][main])
        return result
    
    def _is_yang(self) -> bool:
        """判断是否阳干"""
        return self.Gan.index(self.me) % 2 == 0
    
    def _zhi_ku(self, zhi: str, items: Tuple) -> bool:
        """判断地支是否在库中且含指定天干"""
        return zhi in self.kus and min(self.zhi5[zhi], key=self.zhi5[zhi].get) in items
    
    def _get_empty(self, zhu: Tuple, zhi: str) -> str:
        """检查是否空亡"""
        key = (self.gan5[self.gans[0]], self.zhis[2])
        if key in self.empties and zhi in self.empties[key]:
            return '空'
        return ''
    
    def analyze(self) -> List[str]:
        """执行完整命理分析"""
        self.lines = []
        
        # 按顺序分析各模块
        self._analyze_guan()    # 正官
        self._analyze_sha()     # 七杀
        self._analyze_shi()     # 食神
        self._analyze_shang()   # 伤官
        self._analyze_cai()     # 财星
        self._analyze_yin()     # 印星
        self._analyze_bi()      # 比劫
        self._analyze_zhi()     # 地支
        
        # 输出格局和局
        if self.jus:
            self.lines.append(f"局: {', '.join(self.jus)}")
        if self.all_ges:
            self.lines.append(f"格: {', '.join(self.all_ges)}")
        
        return self.lines
    
    # ============================================================
    # 正官分析
    # ============================================================
    
    def _analyze_guan(self):
        """正官分析"""
        if '官' not in self.gan_shens:
            return
        
        self.lines.append("正官：比较传统保守，守规矩。重名誉，有责任心。")
        
        if self.gan_shens[3] == '官' and len(self.zhi5[self.zhis[3]]) == 1:
            self.lines.append("官专位时坐地支，男有得力子息。")
        
        if self.gan_shens[0] == '官':
            self.lines.append("年干为官，身强有可能出身书香门第。")
            if self.gan_shens[3] == '官':
                self.lines.append("男命年干、时干都为官，对后代和头胎不利。")
        
        if '财' not in self.gan_shens and '印' not in self.gan_shens:
            self.lines.append("官独透天干成格，四柱无财或印，为老实人。")
        
        if '伤' in self.gan_shens:
            self.lines.append("正官伤官通根透，又无其他格局，失策。尤其是女命，异地分居居多，婚姻不美满。")
        
        if '杀' in self.gan_shens:
            self.lines.append("官和杀同见天干不佳。女在年干月干，30以前婚姻不佳，或体弱多病。")
        
        # 官坐神煞分析
        for seq, gan_ in enumerate(self.gan_shens):
            if gan_ != '官':
                continue
            if self.zhi_shens[seq] in ('劫', '比'):
                self.lines.append("天干正官，地支比肩或劫财，亲友之间不适合合作，适合经营烂摊子。")
            if self.zhi_shens[seq] == '杀':
                self.lines.append("正官坐七杀，男命恐有诉讼之灾。女命婚姻不佳。月柱尤其麻烦。")
            if self.zhi_shens[seq] == '印':
                self.lines.append("官坐印，无刑冲合，吉。")
        
        if self.shens2.count('官') > 2 and '官' in self.gan_shens and '官' in self.zhi_shens2:
            self.lines.append("正官多者，虚名。为人性格温和，比较实在。做七杀看")
        
        if self.zhi_shens[2] == '官' or self.zhis[2] == self.guan_lu:
            self.lines.append("日坐正官专位，淑女。")
            if self._is_yang() and self.zhis[3] == self.me_di:
                self.lines.append("日坐正官，时支阳刃：先富后败，再东山再起。")
        
        if self.gan_shens.count('官') > 2:
            self.lines.append("天干2官，女下有弟妹要照顾，一生为情所困。")
        
        if self.zhi_shens[1] == '官' and '伤' in self.zhi_shens2:
            self.lines.append("月支正官，又成伤官格，难做真正夫妻。有实，无名。")
    
    # ============================================================
    # 七杀分析
    # ============================================================
    
    def _analyze_sha(self):
        """七杀分析"""
        if '杀' not in self.gan_shens:
            return
        
        self.lines.append("七杀是非多。但是对男人有时是贵格。成格基础85可杀生印或食制印、身杀两停、阳刃驾杀。")
        
        if '杀' in self.zhi_shens2:
            self.lines.append("杀格：喜食神制，要食在前，杀在后。阳刃驾杀：杀在前，刃在后。身杀两停：比如甲寅日庚申月。杀印相生，忌食同成格。")
            self.all_ges.append('杀')
            
            if '比' in self.gan_shens or '劫' in self.gan_shens:
                self.lines.append("杀格透比或劫：性急但还有分寸。")
            
            if '官' in self.gan_shens:
                self.lines.append("杀格透官：精明琐屑，不怕脏。")
            
            if '食' in self.gan_shens or '伤' in self.gan_shens:
                self.lines.append("杀格透食伤：外表宁静，内心刚毅。")
            
            if '印' in self.gan_shens:
                self.lines.append("杀格透印：圆润、精明干练。")
        
        if self.gan_shens[0] == '杀' and self.gan_shens[1] == '杀':
            self.lines.append("杀月干年干重叠：不是老大，出身平常，多灾，为人不稳重。")
        
        if self.gan_shens[1] == '杀' and '杀' in self.zhi_shen3[1]:
            self.lines.append("杀月重叠：女易离婚，其他格一生多病。")
        
        if self.gan_shens[0] == '杀':
            self.lines.append("年干七杀，早年不好。或家里穷或身体不好。")
            if self.gan_shens[1] == '杀':
                self.lines.append("年月天干七杀，家庭复杂。")
        
        if '官' in self.gan_shens:
            self.lines.append("官和杀同见天干不佳。女在年干月干，30以前婚姻不佳，或体弱多病。")
        
        if self.gan_shens[1] == '杀' and self.zhi_shens[1] == '杀':
            self.lines.append("月柱都是七杀，克得太过。有福不会享。六亲福薄。时柱没关系。")
            if '杀' not in self.zhi_shens2:
                self.lines.append("七杀年月浮现天干，性格好变，不容易定下来。30岁以前不行。")
        
        if '杀' in self.zhi_shens and '劫' in self.zhi_shens:
            self.lines.append("七杀地支有根时要有阳刃强为佳。杀身两停。")
        
        if self.gan_shens[1] == '杀' and self.gan_shens[3] == '杀':
            self.lines.append("月时天干为七杀：体弱多病。")
        
        if self.gan_shens[0] == '杀' and self.gan_shens[3] == '杀':
            self.lines.append("七杀年干时干：男头胎麻烦（概率），女婚姻有阻碍。")
        
        if self.gan_shens[3] == '杀':
            self.lines.append("七杀在时干，固执有毅力。")
        
        if '印' in self.gan_shens:
            self.lines.append("身弱杀生印，不少是精明练达的商人。")
        
        if '财' in self.gan_shens or '才' in self.gan_shens:
            self.lines.append("财生杀，如果不是身弱有印，不佳。")
        
        # 七杀坐神煞
        for seq, gan_ in enumerate(self.gan_shens):
            if gan_ != '杀' and self.zhi_shens[seq] != '杀':
                continue
            if gan_ == '杀' and '杀' in self.zhi_shen3[seq] and seq != 3:
                self.lines.append("七杀坐七杀，六亲福薄。")
            if self._get_empty(self.zhus[2], self.zhis[seq]) == '空':
                self.lines.append("七杀坐空亡，女命夫缘薄。")
            if self.zhis[seq] == self.shi:
                self.lines.append("七杀坐食：易有错误判断。")
            if self.zhi_xing[seq] or self.zhi_6chong[seq]:
                self.lines.append("七杀坐刑或对冲，夫妻不和。")
        
        if self.shens2.count('杀') > 2:
            self.lines.append("杀多者如果无制，性格刚强。打抱不平，不易听人劝。女的喜欢佩服的人。")
        
        if self.zhi_shens[2] == '杀' and len(self.zhi5[self.zhis[2]]) == 1:
            self.lines.append("天元坐杀：如无食神，阳刃，性急，聪明，对人不信任。如果七杀还透出月干无制，体弱多病。")
        
        if self.gan_shens.count('杀') > 2:
            self.lines.append("天干2杀，不是老大、性格浮躁不持久。")
    
    # ============================================================
    # 食神分析
    # ============================================================
    
    def _analyze_shi(self):
        """食神分析"""
        if '食' not in self.gan_shens:
            return
        
        if '食' in self.zhi_shens2:
            self.lines.append("食神成格的情况下，寿命比较好。食神和偏财格比较长寿。食神厚道，为人不慷慨。食神有口福。成格基础84，喜财忌偏印。")
            self.lines.append("食神无财一生衣食无忧，无大福。有印用比劫通关或财制。")
            self.all_ges.append('食')
            
            if (self.gan_shens[0] == '食' and self.gan_shens[1] == '食') or \
               (self.gan_shens[1] == '食' and '食' in self.zhi_shen3[1]):
                self.lines.append("食月重叠：生长安定环境，性格仁慈、无冲刑长寿。女早年得子。无冲刑偏印者是佳命。")
        
        if '枭' in self.gan_shens:
            self.lines.append("男的食神碰到偏印，身体不好。怕偏印，正印要好一点。四柱透出偏财可解。")
            if '劫' in self.gan_shens:
                self.lines.append("食神不宜与劫财、偏印齐出干。体弱多病。")
            if '杀' in self.gan_shens:
                self.lines.append("食神不宜与杀、偏印齐成格。体弱多病。")
        
        if '食' in self.zhi_shens:
            self.lines.append("食神天透地藏，女命阳日主适合社会性职业，阴日主适合上班族。")
        
        if '财' not in self.gan_shens and '才' not in self.gan_shens:
            self.lines.append("食神多，要食伤生财才好，无财难发。")
        
        if '伤' in self.gan_shens:
            self.lines.append("食伤混杂：食神和伤官同透天干：志大才疏。")
        
        if '杀' in self.gan_shens:
            self.lines.append("食神制杀，杀不是主格，施舍后后悔。")
        
        for seq, gan_ in enumerate(self.gan_shens):
            if gan_ != '食':
                continue
            if self.zhi_shens[seq] == '劫':
                self.lines.append("食神坐阳刃，辛劳。")
        
        if self.shens2.count('食') > 2:
            self.lines.append("食神四个及以上的为多，做伤官处理。食神多，要食伤生财才好，无财难发。")
            if '劫' in self.gan_shens or '比' in self.gan_shens:
                self.lines.append("食神带比劫，好施舍，乐于做社会服务。")
        
        if ('杀', '食') in self.zhus or ('食', '杀') in self.zhus:
            self.lines.append("食神与七杀同一柱，易怒。食神制杀，最好食在前。")
        
        if ('枭', '食') in self.zhus or ('食', '枭') in self.zhus:
            self.lines.append("女命最怕食神偏印同一柱。不利后代，时柱尤其重要。")
        
        if '食' in self.zhi_shen3[2] and self.zhis[2] in self.zhengs:
            self.lines.append("日支食神专位容易发胖，有福。只有2日：癸卯，己酉。男命有有助之妻。")
        
        if self.zhi_shens[2] == '食' and self.zhi_shens[2] == '杀':
            self.lines.append("自坐食神，时支杀专，二者不出天干，多成败，最后失局。")
        
        if self.zhi_shens[2] == '食':
            self.lines.append("自坐食神，相敬相助，即使透枭也无事，不过心思不定，做事毅力不足。专位容易发胖，有福。")
        
        if self.zhis[2] == self.shi_lu and self.zhis[3] == self.sha_lu and self.sha not in self.gan_shens:
            self.lines.append("自坐食，时支专杀不透干：多成败，终局失制。")
        
        if '食' in self.zhi_shen3[3] and '枭' in self.zhi_shen3[3] + [self.gan_shens[3]]:
            self.lines.append("时支食神逢偏印：体弱，慢性病，女的一婚不到头。")
        
        if self.zhis[2] in self.kus and self.zhi_shen3[2][2] in ('食', '伤'):
            self.lines.append("自坐食伤库：总觉得钱不够。")
        
        if '食' in (self.gan_shens[0], self.zhi_shens[0]):
            self.lines.append("年柱食：可三代同堂。")
        
        if self._zhi_ku(self.zhis[3], (self.shi, self.shang)) and \
           ('食' in self.zhi_shen3[1] or '伤' in self.zhi_shen3[1]):
            self.lines.append("时食库，月食当令，孤克。")
        
        if self._zhi_ku(self.zhis[2], (self.shi, self.shang)):
            if self.zhis[3] == self.guan_lu:
                self.lines.append("坐食伤库：时支官，发达时接近寿终。")
        
        if self._zhi_ku(self.zhis[3], (self.shi, self.shang)):
            if self.zhis[1] in (self.shi_di, self.shi_lu):
                self.lines.append("坐食伤库：月支食伤当令，吉命而孤克。")
    
    # ============================================================
    # 伤官分析
    # ============================================================
    
    def _analyze_shang(self):
        """伤官分析"""
        if '伤' not in self.gan_shens:
            return
        
        self.lines.append("伤官有才华，但是清高。要生财，或者印制。")
        
        if '伤' in self.zhi_shens2:
            self.lines.append("伤官成格基础87生财、配印。不考虑调候逆用比顺用好。伤官配印，如果透杀，透财不佳。")
            self.all_ges.append('伤')
        
        if (self.gan_shens[0] == '伤' and self.gan_shens[1] == '伤') or \
           (self.gan_shens[1] == '伤' and '伤' in self.zhi_shen3[1]):
            self.lines.append("父母兄弟均无缘。孤苦，性刚毅好掌权。30岁以前有严重感情苦重。")
        
        if '印' in self.gan_shens and '财' not in self.gan_shens:
            self.lines.append("伤官配印，无财，有手艺，但是不善于理财。有一定个性。")
        
        if self.gan_shens[0] == '伤' and self.gan_shens[1] == '伤' and '伤' not in self.zhi_shens2:
            self.lines.append("年月天干都浮现伤官，亲属少。")
        
        if self.zhi_shens[1] == '伤' and len(self.zhi5[self.zhis[1]]) == 1 and self.gan_shens[1] == '伤':
            self.lines.append("月柱：伤官坐专位伤官，夫缘不定。假夫妻。")
        
        for seq, gan_ in enumerate(self.gan_shens):
            if gan_ != '伤':
                continue
            if self.zhi_shens[seq] == '劫':
                self.lines.append("伤官地支坐阳刃，力不从心。背禄逐马，克官劫财。")
        
        if self.shens2.count('伤') > 2:
            if self.female:
                self.lines.append("女命伤官多，即使不入伤官格，也缘分浅，多有苦情。")
            if self.gan_shens.count('伤') > 2:
                self.lines.append("天干2伤官：性骄，六亲不靠。婚前诉说家人，婚后埋怨老公。30岁以前为婚姻危机期。")
        
        if self.zhi_shens[2] == '伤' and len(self.zhi5[self.zhis[2]]) == 1:
            self.lines.append("女命婚姻宫伤官：强势克夫。男的对妻子不利。")
        
        if self.gan_shens[3] == '伤' and self.me_lu == self.zhis[3]:
            self.lines.append("伤官坐时禄：六亲不靠，无冲刑晚年发，有冲刑不发。")
        
        if self.zhis[3] in (self.shang_lu, self.shang_di) and self.zhis[1] in (self.shang_lu, self.shang_di):
            self.lines.append("月支时支食伤当令：日主无根，泄尽日主，凶。")
    
    # ============================================================
    # 财星分析
    # ============================================================
    
    def _analyze_cai(self):
        """财星分析"""
        has_cai = '财' in self.gan_shens
        has_piancai = '才' in self.gan_shens
        
        if not has_cai and not has_piancai:
            return
        
        # 偏财分析
        if has_piancai:
            self.lines.append("偏财明现天干，不论是否有根:财富外人可见;实际财力不及外观一半。没钱别人都不相信。")
            self.lines.append("偏财透天干，讲究原则，不拘小节。喜奉承，善于享受。")
            
            if '才' in self.zhi_shens2:
                self.lines.append("财格基础80:比劫用食伤通关或官杀制；身弱有比劫仍然用食伤通关。")
                self.all_ges.append('才')
            
            if '比' in self.gan_shens or '劫' in self.gan_shens:
                if self.gan_shens[3] == '才':
                    self.lines.append("年月比劫，时干透出偏财。祖业凋零，再白手起家。有刑冲为千金散尽还复来。")
            
            if '杀' in self.gan_shens and '杀' in self.zhi_shens:
                self.lines.append("偏财和七杀并位，地支又有根，父子外合心不合。")
            
            if self.zhi_shens[0] == '才':
                self.lines.append("偏财根透年柱，家世良好，且能承受祖业。")
            
            for seq, gan_ in enumerate(self.gan_shens):
                if gan_ != '才':
                    continue
                if '劫' in self.zhi_shen3[seq] and self.zhis[seq] in self.zhengs:
                    self.lines.append("偏财坐阳刃劫财,可做父缘薄，也可幼年家贫。")
                if self._get_empty(self.zhus[2], self.zhis[seq]) == '空':
                    self.lines.append("偏财坐空亡，财官难求。")
        
        if self.shens2.count('才') > 2:
            self.lines.append("偏财多的人慷慨，得失看淡。花钱一般不会后悔。偏乐观，甚至是浮夸。")
            self.lines.append("乐善好施，有团队精神，女命偏财，听父亲的话。")
        
        if (self.zhi_shens[2] == '才' and len(self.zhi5[self.zhis[2]]) == 1) or \
           (self.zhi_shens[3] == '才' and len(self.zhi5[self.zhis[3]]) == 1):
            self.lines.append("日时地支坐专位偏财。不见刑冲，时干不是比劫，晚年发达。")
        
        # 正财分析
        if has_cai:
            if self._is_yang():
                self.lines.append("男日主合财星，夫妻恩爱。如果争合或天干有劫财，双妻。")
            
            if '财' in self.zhi_shens2:
                self.lines.append("财格基础80:比劫用食伤通关或官杀制。")
            
            if '官' in self.gan_shens:
                self.lines.append("正官正财并行透出，(身强)出身书香门第。")
            
            if '官' in self.gan_shens or '杀' in self.gan_shens:
                self.lines.append("官或杀与财并行透出，女压夫，财生官杀，老公压力大。")
            
            if self.gan_shens[0] == '财':
                self.lines.append("年干正财若为喜，富裕家庭，但不利母亲。")
        
        # 财月重叠
        if (self.gan_shens[0] in ('财', '才') and self.gan_shens[1] in ('财', '才')) or \
           (self.gan_shens[1] in ('财', '才') and ('财' in self.zhi_shen3[1] or '才' in self.zhi_shen3[1])):
            self.lines.append("财或偏财月重叠：女职业妇女，有理财办事能力。因自己理财能力而影响婚姻。一财得所，红颜失配。男的双妻。")
    
    # ============================================================
    # 印星分析
    # ============================================================
    
    def _analyze_yin(self):
        """印星分析"""
        has_yin = '印' in self.gan_shens
        has_xiao = '枭' in self.gan_shens
        
        if not has_yin and not has_xiao:
            return
        
        if has_yin:
            if (self.gan_shens[1] == '印' and '印' in self.zhi_shen3[1]):
                self.lines.append("印月重叠：女迟婚，月阳刃者离寡，能独立谋生，有修养的才女。")
            
            if self.gan_shens[0] == '印':
                self.lines.append("年干印为喜：出身于富贵之家。")
            
            if self.shens2.count('印') > 2:
                self.lines.append("正印多的：聪明有谋略，比较含蓄，不害人，识时务。正印不怕日主死绝，反而怕太强。")
            
            for seq, gan_ in enumerate(self.gan_shens):
                if gan_ != '印':
                    continue
                if self.ten_deities[self.gans[seq]][self.zhis[seq]] in ('绝', '死'):
                    if seq < 3:
                        self.lines.append("正印坐死绝，或天干正印地支有冲刑，不利母亲。时柱不算。")
                if self.zhi_shens[seq] == '财':
                    self.lines.append("男正印坐正财，夫妻不好。月柱正印坐正财专位，必离婚。")
                if self.zhi_shens[seq] == '印':
                    self.lines.append("正印坐正印，专位，过于自信。务实，拿得起放得下。女的话大多晚婚。")
                if self.zhi_shens[seq] == '枭' and len(self.zhi5[self.zhis[seq]]) == 1:
                    self.lines.append("正印坐偏印专位：有多种职业;家庭不吉。子息迟。")
                if self.zhi_shens[seq] == '伤':
                    self.lines.append("正印坐伤官：适合清高的职业。不适合追逐名利，女的婚姻不好。")
                if self.zhi_shens[seq] == '劫' and self.me in ('甲', '庚', '壬'):
                    self.lines.append("正印坐阳刃，身心多伤，心疲力竭。")
            
            if '杀' in self.gan_shens and '劫' in self.zhi_shens and self.me in ('甲', '庚', '壬'):
                self.lines.append("正印、七杀、阳刃全：女命宗教人，否则独身，清高。男小疾多，婚姻不佳。")
            
            if '官' in self.gan_shens or '杀' in self.gan_shens:
                self.lines.append("身弱官杀和印都透天干，格局佳。")
            else:
                self.lines.append("单独正印主秀气、艺术、文才。性格保守。")
            
            if '财' in self.gan_shens:
                self.lines.append("印和财都透天干，都有根，最好先财后印，一生吉祥。")
        
        # 印月重叠
        if self.gan_shens[1] == '印' and self.zhi_shens[1] == '印' and '比' in self.gan_shens:
            self.lines.append("月干支印格，透比，有冲亡。")
        
        # 自坐印
        if self.zhi_shens[2] == '印':
            if self.gan_shens[3] == '才' and '才' in self.zhi_shen3[3]:
                self.lines.append("坐印，时偏财格：他乡发迹，妻贤子孝。")
            if self.gan_shens[3] == '财' and ('财' in self.zhi_shen3[3] or self.zhis[3] == self.cai_lu):
                self.lines.append("坐印，时财正格：晚年发达，妻贤子不孝。")
        
        if self.zhi_shens[3] == '印' and self.zhis[3] in self.zhengs:
            self.lines.append("时支专位正印。男忙碌到老。女的子女各居一方。亲情淡薄。")
        
        if self.gan_shens[3] == '印' and '印' in self.zhi_shen3[3]:
            self.lines.append("时柱正印格，不论男女，老年辛苦。子女无缘。")
        
        if self.gan_shens.count('印') + self.gan_shens.count('枭') > 1:
            self.lines.append("印枭在年干月干，性格迂腐，故作清高，女子息迟，婚姻有阻碍。")
        
        # 坐印库
        if self._zhi_ku(self.zhis[2], (self.yin, self.xiao)):
            if self.shens2.count('印') > 2:
                self.lines.append("日坐印库，又成印格，意外伤残，凶终。过旺。")
            if self.zhi_shens[3] == '劫':
                self.lines.append("自坐印库，时阳刃。带比禄印者贫。")
        
        if self.zhis[1] == self.yin_lu:
            if '财' in self.gan_shens and '财' in self.zhi_shens:
                self.lines.append("自坐正印专旺，成财格，移他乡易宗，妻贤子孝。")
    
    # ============================================================
    # 比劫分析
    # ============================================================
    
    def _analyze_bi(self):
        """比劫分析"""
        has_bi = '比' in self.gan_shens
        has_jie = '劫' in self.gan_shens
        
        if not has_bi and not has_jie:
            return
        
        if has_bi and has_jie:
            self.lines.append("比劫帮身：适合合作做生意，财来财去，留不住。")
        elif has_bi:
            self.lines.append("比肩：同事、朋友、合作伙伴。")
        elif has_jie:
            self.lines.append("劫财：竞争、纠纷、克妻、破财。")
        
        if self.gan_shens.count('比') + self.gan_shens.count('劫') > 1:
            self.lines.append("比劫重叠，性格固执，人缘差。")
    
    # ============================================================
    # 地支分析
    # ============================================================
    
    def _analyze_zhi(self):
        """地支分析"""
        # 自坐绝
        if self.zhis[2] == self.me_jue:
            self.lines.append("自坐绝")
            
            if self.zhi_6he[2]:
                self.lines.append("自己坐绝（天元坐杀）：日支与它支合化、双妻，子息迟。")
            
            self.lines.append("自己坐绝支，绝支合会，先贫后富。")
            
            if self.zhis[3] == self.zhis[2]:
                self.lines.append("日主日时绝，旺达则有刑灾。")
            
            if self.zhis[3] == self.zhis[2] == self.zhis[1]:
                self.lines.append("日主月日时绝，旺达则有刑灾，平常人不要紧。")
            
            if self.zhi_shens.count('比') + self.zhi_shens.count('劫') > 1:
                self.lines.append("自坐绝，地支比劫大于1，旺衰巨变，凶。")
        
        # 自坐食伤库
        for i, zhi in enumerate(self.zhis):
            if zhi in self.kus and i > 0:
                for gan in self.zhi5_list[zhi]:
                    shen = self.ten_deities[self.me][gan]
                    if shen in ('食', '伤'):
                        self.lines.append("自坐食伤库：总觉得钱不够。")
                        break
        
        # 自坐杀禄
        if self.zhis[2] == self.sha_lu:
            if self._zhi_ku(self.zhis[3], (self.guan, self.sha)):
                self.lines.append("自坐七杀入墓：一生有疾，生计平常。")
        
        if self.zhis[3] == self.sha_lu:
            if self.zhi_xing[3] or self.zhi_6chong[3]:
                self.lines.append("时支杀禄带刑冲：纵然吉命也带疾不永寿。")
        
        if self.gan_shens[3] == '杀' and self.zhis[3] in (self.cai_di, self.cai_lu):
            self.lines.append("七杀时柱坐财禄旺：性格严肃。双妻，子息迟。")
        
        if self.zhis[3] == self.sha_lu:
            if self.zhi_6chong[3] or self.zhi_xing[3]:
                self.lines.append("七杀时禄旺：遇刑冲寿夭带疾。")
            if self.zhis[1] == self.sha_lu:
                self.lines.append("七杀时月禄旺：体疾。")
        
        if self._zhi_ku(self.zhis[2], (self.guan, self.sha)):
            if set(self.zhis).issubset(set('辰戌丑未')):
                self.lines.append("自坐七杀入墓：地支都为库，孤独艺术。")
        
        if '杀' in self.gan_shens and self.zhi_shens.count('杀') > 1:
            self.lines.append("七杀透干，地支双根，不论贫富，亲属离散。")


# ============================================================
# 便捷函数
# ============================================================

def analyze_mingli(result: BaziResult, female: bool = False) -> List[str]:
    """
    便捷命理分析函数
    
    用法:
        from bazi_calc import BaziCalculator
        from bazi_calc.mingli import analyze_mingli
        
        result = BaziCalculator().calculate(1990, 3, 15, 19)
        for line in analyze_mingli(result):
            print(line)
    """
    return MingliAnalyzer(result, female).analyze()