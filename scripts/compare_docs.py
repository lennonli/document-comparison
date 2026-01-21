
import sys
import os
import argparse
import subprocess
import difflib

from parsers.table_parser import TableParser
from comparators.fuzzy_logic import DataComparator
from comparators.spell_check import SpellChecker
from comparators.logic_check import LogicChecker
from comparators.consistency_check import ConsistencyChecker
from comparators.llm_client import LLMClient # New
from utils.nlp_utils import NLPUtils         # New
from parsers.section_chunker import SectionChunker # New
from reporters.md_reporter import MDReporter
import re
import json

# Initialize global NLP utils
nlp = NLPUtils()

def convert_to_html(file_path):
    base_name = os.path.basename(file_path)
    tmp_path = f"/tmp/{base_name}.html"
    if file_path.lower().endswith('.docx'):
        try:
            subprocess.run(['textutil', '-convert', 'html', '-stdout', file_path], stdout=open(tmp_path, 'w'), stderr=subprocess.DEVNULL, check=True)
            return tmp_path
        except:
            return None
    return file_path

def convert_to_text(file_path):
    try:
        res = subprocess.run(['textutil', '-convert', 'txt', '-stdout', file_path], capture_output=True, text=True)
        return res.stdout
    except:
        return ""

def process_pair(f1, f2, reporter):
    print(f"Comparing: {os.path.basename(f1)} <-> {os.path.basename(f2)}")
    
    # 1. Structure Analysis (Tables)
    h1 = convert_to_html(f1)
    h2 = convert_to_html(f2)
    
    # Save text for Agent Analysis
    t1 = convert_to_text(f1)
    t2 = convert_to_text(f2)
    
    tp = TableParser()
    d1 = tp.parse(h1) if h1 else []
    d2 = tp.parse(h2) if h2 else []
    
    # --- Section Aware Processing (New v3.5) ---
    chunker = SectionChunker()
    secs1 = chunker.chunk_text(t1)
    secs2 = chunker.chunk_text(t2)
    aligned_data = chunker.align_sections(secs1, secs2)
    
    # Save Aligned Data for Agent
    output_dir = os.path.dirname(f1)
    p1_name = os.path.basename(f1)
    json_path = os.path.join(output_dir, f"Comparison_Aligned_{p1_name}.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(aligned_data, f, ensure_ascii=False, indent=2)
        
    print(f"✅ Generated Aligned JSON: {json_path}")
    
    # --- End Section Aware Processing ---

    
    # 2. Table Data Comparison (With Semantic Matching in Fuzzy Logic)
    
    # ❌ FIX: Extract "Actual Controller" / "Controlling Shareholder" via Regex from Text
    # Because one file might have it in text paragraph, other in table.
    # We add a virtual table for this.
    
    def extract_key_personnel(text):
        info = {}
        # Pattern: "实际控制人[为|是][:：]?\s*([\u4e00-\u9fa5]+)"
        # Or in tables, captured by next line... but let's try text first.
        # This is a heuristic.
        m_ctrl = re.search(r'(?:实际控制人|实控人)[为|是|：|:]?\s*([\u4e00-\u9fa5]{2,10})', text)
        if m_ctrl: info['实际控制人'] = m_ctrl.group(1)
        
        m_share = re.search(r'(?:控股股东)[为|是|：|:]?\s*([\u4e00-\u9fa5]{2,10})', text)
        if m_share: info['控股股东'] = m_share.group(1)
        return info

    kp1 = extract_key_personnel(t1)
    kp2 = extract_key_personnel(t2)
    
    # If found in both, compare
    kp_issues = []
    for k in ['实际控制人', '控股股东']:
        v1 = kp1.get(k)
        v2 = kp2.get(k)
        if v1 and v2 and v1 != v2:
            # Simple fuzzy check
            if nlp.get_similarity(v1, v2) < 0.8:
                kp_issues.append(f"⚠️ {k} 不一致: {os.path.basename(f1)}='{v1}' vs {os.path.basename(f2)}='{v2}'")
            
    # Also inject these issues into the reporter later

    
    # 2. Table Data Comparison (With Semantic Matching in Fuzzy Logic)
    # We ideally update fuzzy_logic to use nlp.get_similarity() but for now keep structured logic
    cmp = DataComparator()
    diffs = cmp.compare_datasets(d1, d2)
    
    # 3. Logic & Consistency Checks
    lc = LogicChecker()
    cc = ConsistencyChecker()
    sc = SpellChecker()
    
    extra_issues1 = sc.check_file(f1) + cc.check_file(f1)
    extra_issues2 = sc.check_file(f2) + cc.check_file(f2)
    
    for t in d1: extra_issues1.extend(lc.check_table_logic(t))
    for t in d1: extra_issues1.extend(lc.check_table_logic(t))
    for t in d2: extra_issues2.extend(lc.check_table_logic(t))
    
    # Add Key Personnel Issues
    extra_issues1.extend(kp_issues)
    
    # 4. LLM Insight (The Real Intelligence)
    llm = LLMClient()
    llm_insights = []
    
    if llm.is_available():
        print("🤖 Invoking LLM for semantic analysis...")
        t1 = convert_to_text(f1)
        t2 = convert_to_text(f2)
        
        # Simple chunking: Compare first 4000 chars as summary? 
        # Or better: if small enough, compare whole. If large, compare specific keywords sections.
        # For this demo, we compare the first 8000 chars which usually contains the meat.
        insight = llm.compare_sections(t1[:8000], t2[:8000], section_name="全文核心内容")
        if insight and insight.get('has_diff'):
            llm_insights.append(insight)
    else:
        # Fallback: Just mentioning semantic similarity check passed via Jieba
        pass

    return reporter.generate(diffs, extra_issues1, extra_issues2, f1, f2, llm_insights)

def find_best_match(target_file, candidate_files):
    target_name = os.path.basename(target_file)
    best_match = None
    best_ratio = 0.0
    
    for c in candidate_files:
        c_name = os.path.basename(c)
        # Use Jieba/NLP similarity for filename matching too?
        # For now difflib is safer for filenames
        ratio = difflib.SequenceMatcher(None, target_name, c_name).ratio()
        if ratio > best_ratio:
            best_ratio = ratio
            best_match = c
            
    if best_ratio > 0.4:
        return best_match
    return None

def main():
    parser = argparse.ArgumentParser(description="Document Comparison Skill v3.0 (AI Powered)")
    parser.add_argument("path1", help="File or Folder 1")
    parser.add_argument("path2", help="File or Folder 2")
    args = parser.parse_args()
    
    p1 = os.path.abspath(args.path1)
    p2 = os.path.abspath(args.path2)
    
    reporter = MDReporter()
    
    if os.path.isdir(p1) and os.path.isdir(p2):
        print("📂 Batch Mode Activated")
        files1 = [os.path.join(p1, f) for f in os.listdir(p1) if f.endswith('.docx') or f.endswith('.doc')]
        files2_pool = [os.path.join(p2, f) for f in os.listdir(p2) if f.endswith('.docx') or f.endswith('.doc')]
        
        for f1 in files1:
            match = find_best_match(f1, files2_pool)
            if match:
                process_pair(f1, match, reporter)
            else:
                print(f"⚠️ No match for {os.path.basename(f1)}")
                
    elif os.path.isfile(p1) and os.path.isfile(p2):
        process_pair(p1, p2, reporter)
    else:
        print("Error: Invalid paths.")

if __name__ == "__main__":
    main()
