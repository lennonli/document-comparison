
import re
import jieba

class NLPUtils:
    def __init__(self):
        # Initialize dictionary if needed
        pass
        
    def get_similarity(self, s1, s2):
        """
        Computes Jaccard similarity based on tokens.
        Good for: "Tencent (Shenzhen) Co." vs "Tencent Shenzhen Company"
        """
        if not s1 or not s2: return 0.0
        
        # 1. Clean
        s1 = self.clean(s1)
        s2 = self.clean(s2)
        
        if s1 == s2: return 1.0
        
        # 2. Tokenize
        t1 = set(jieba.cut(s1))
        t2 = set(jieba.cut(s2))
        
        # 3. Jaccard
        intersection = len(t1 & t2)
        union = len(t1 | t2)
        
        if union == 0: return 0.0
        return intersection / union

    def clean(self, s):
        # Remove punctuation, bracket types, common corporation suffixes
        s = re.sub(r'[(),.（），。、]', '', s)
        # s = s.replace("有限公司", "").replace("有限合伙", "") # Optional: if too aggressive
        return s
