
import re

class SectionChunker:
    def __init__(self):
        # Patterns for headers: 
        # 1. "一、...", "二、..."
        # 2. "（一）...", "（二）..."
        # 3. "1、...", "2、..."
        # 4. "1.", "2." (if at start of line)
        self.header_patterns = [
            re.compile(r'^\s*[一二三四五六七八九十]+、.{1,50}$'),
            re.compile(r'^\s*（[一二三四五六七八九十]+）.{1,50}$'),
            re.compile(r'^\s*\d+、.{1,50}$'),
            re.compile(r'^\s*\d+\..{1,50}$'),
            # Specific section names often used in IPO docs
            re.compile(r'^\s*(关联方|关联交易|控股股东|实际控制人|基本情况|历史沿革).{0,20}$')
        ]

    def is_header(self, line):
        line = line.strip()
        if not line: return False
        if len(line) > 60: return False # Headers shouldn't be too long
        
        for p in self.header_patterns:
            if p.match(line):
                return True
        return False

    def chunk_text(self, text):
        """
        Splits text into a list of dicts: {'header': '...', 'content': '...'}
        """
        lines = text.split('\n')
        sections = []
        current_header = "Intro / Uncategorized"
        current_content = []
        
        for line in lines:
            if self.is_header(line):
                # Save previous section
                if current_content:
                    sections.append({
                        'header': current_header, 
                        'content': '\n'.join(current_content).strip()
                    })
                
                # Start new section
                current_header = line.strip()
                current_content = []
            else:
                current_content.append(line)
                
        # Append last section
        if current_content:
            sections.append({
                'header': current_header,
                'content': '\n'.join(current_content).strip()
            })
            
        return sections

    def align_sections(self, sections_a, sections_b):
        """
        Aligns sections from two docs based on header similarity.
        Returns: list of {'section': 'Name', 'text_a': '...', 'text_b': '...'}
        """
        aligned_map = {} # Header -> {a: ..., b: ...}
        
        # 1. Map A
        for s in sections_a:
            h = s['header']
            aligned_map[h] = {'section': h, 'text_a': s['content'], 'text_b': ''}
            
        # 2. Map B (Try to find fuzzy match in A, else new)
        import difflib
        
        for s in sections_b:
            h_b = s['header']
            # Find best match in existing keys
            best_match = None
            best_ratio = 0.0
            
            for h_a in aligned_map.keys():
                ratio = difflib.SequenceMatcher(None, h_a, h_b).ratio()
                if ratio > best_ratio:
                    best_ratio = ratio
                    best_match = h_a
            
            if best_ratio > 0.6: # Threshold for "Same Section"
                aligned_map[best_match]['text_b'] = s['content']
                # Append header to section name if different for clarity? No, keep A's name
            else:
                aligned_map[h_b] = {'section': h_b, 'text_a': '', 'text_b': s['content']}
                
        return list(aligned_map.values())
