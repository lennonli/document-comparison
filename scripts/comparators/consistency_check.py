
import re
import subprocess

class ConsistencyChecker:
    def check_file(self, file_path):
        issues = []
        
        # 1. Get Text Content
        try:
           # We need textutil for reliable extraction
           res = subprocess.run(['textutil', '-convert', 'txt', '-stdout', file_path], capture_output=True, text=True)
           text = res.stdout
        except:
            return ["无法读取文件进行一致性检查"]
            
        # 2. Extract Section Headers (e.g., "1.1", "第一条", "（一）")
        # Creating a set of existing sections for verification
        existing_sections = set()
        
        # Regex for common section headers
        # 1.1, 1.2.3
        sections_num = re.findall(r'^\s*(\d+(\.\d+)+)\s', text, re.MULTILINE)
        for s in sections_num: existing_sections.add(s[0])
        
        # 第一条，第二条
        sections_cn = re.findall(r'^\s*(第[一二三四五六七八九十百]+条)', text, re.MULTILINE)
        for s in sections_cn: existing_sections.add(s)

        # 3. Reference Check (Broken Links)
        # Find "见第X.X条", "根据第X条"
        # Supports "第1.2条", "第1.2款"
        refs = re.findall(r'(见|如|根据|遵照)(第\s*(\d+(\.\d+)+)\s*[条款])', text)
        for match in refs:
            full_ref = match[1]
            ref_num = match[2]
            
            # Verify if ref_num exists in headers
            # Fuzzy check: exact match or match with trailing dot?
            if ref_num not in existing_sections:
                # Might be false positive if section header format differs (e.g. "1.2 Title")
                # We do a second pass check: is "1.2" at the start of any line?
                if not re.search(fr'^\s*{re.escape(ref_num)}', text, re.MULTILINE):
                    issues.append(f"引用可能断链: 文中引用了 '{full_ref}'，但未找到对应的章节标题 '{ref_num}'")

        # 4. Definition Check
        # Pattern: “DefinedTerm”（以下简称“ShortTerm”）
        # Or: "Full Name" (the "Short Name")
        defs = re.findall(r'“([^”]+)”\s*[（(]以下简称[“"\'\s]*([^”"\'\)]+)[”"\'\s]*[)）]', text)
        
        defined_map = {}
        for full, short in defs:
            if short in defined_map:
                issues.append(f"重复定义: 简称 '{short}' 被多次定义")
            defined_map[short] = full
            
        # Check usage of Full Name where Short Name exists? (Efficiency check)
        # Or check if Short Name is used before definition? (Harder)
        # Let's check for "Undefind Term" look-alikes? 
        # Better: Check if user uses "Full Name" significantly after defining "Short Name".
        
        for short, full in defined_map.items():
            # Find definition index
            def_match = re.search(fr'以下简称[“"\'\s]*{re.escape(short)}', text)
            if not def_match: continue
            
            def_idx = def_match.end()
            remainder = text[def_idx:]
            
            # If Full Name appears in remainder, suggest using Short Name
            # Be careful of "Title" or specialized usage.
            if len(full) > 4 and full in remainder:
                 # count occurrences
                 count = remainder.count(full)
                 if count > 0:
                     issues.append(f"定义一致性建议: 已定义简称 '{short}'，但在后文仍使用了全称 '{full}' {count} 次")

        return issues
