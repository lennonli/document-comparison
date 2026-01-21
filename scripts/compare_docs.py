
import sys
import os
import argparse
import subprocess
import shutil
import difflib

from parsers.table_parser import TableParser
from comparators.fuzzy_logic import DataComparator
from comparators.spell_check import SpellChecker
from comparators.logic_check import LogicChecker
from comparators.consistency_check import ConsistencyChecker
from reporters.md_reporter import MDReporter

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

def process_pair(f1, f2, reporter):
    print(f"Comparing: {os.path.basename(f1)} <-> {os.path.basename(f2)}")
    
    # 1. Convert
    h1 = convert_to_html(f1)
    h2 = convert_to_html(f2)
    
    if not h1 or not h2:
        return None
    
    # 2. Parse Tables
    tp = TableParser()
    d1 = tp.parse(h1)
    d2 = tp.parse(h2)
    
    # 3. Compare Data
    cmp = DataComparator()
    diffs = cmp.compare_datasets(d1, d2)
    
    # 4. Logic Checks (New)
    lc = LogicChecker()
    logic_issues1 = []
    logic_issues2 = []
    for t in d1: logic_issues1.extend(lc.check_table_logic(t))
    for t in d2: logic_issues2.extend(lc.check_table_logic(t))
    
    # 5. Consistency Checks (New)
    cc = ConsistencyChecker()
    consis_issues1 = cc.check_file(f1)
    consis_issues2 = cc.check_file(f2)
    
    # 6. Spell Check
    sc = SpellChecker()
    spell1 = sc.check_file(f1)
    spell2 = sc.check_file(f2)
    
    # 7. Generate Single Report
    # Merge issues
    issues1 = spell1 + logic_issues1 + consis_issues1
    issues2 = spell2 + logic_issues2 + consis_issues2
    
    return reporter.generate(diffs, issues1, issues2, f1, f2)

def find_best_match(target_file, candidate_files):
    # Use fuzzy string matching on filenames
    target_name = os.path.basename(target_file)
    best_match = None
    best_ratio = 0.0
    
    for c in candidate_files:
        c_name = os.path.basename(c)
        ratio = difflib.SequenceMatcher(None, target_name, c_name).ratio()
        if ratio > best_ratio:
            best_ratio = ratio
            best_match = c
            
    # Threshold? e.g. 0.4
    if best_ratio > 0.4:
        return best_match
    return None

def main():
    parser = argparse.ArgumentParser(description="Document Comparison Skill v2.0")
    parser.add_argument("path1", help="File or Folder 1")
    parser.add_argument("path2", help="File or Folder 2")
    args = parser.parse_args()
    
    p1 = os.path.abspath(args.path1)
    p2 = os.path.abspath(args.path2)
    
    reporter = MDReporter()
    
    # Mode Detection
    if os.path.isdir(p1) and os.path.isdir(p2):
        print("📂 Batch Mode Activated")
        # List files
        files1 = [os.path.join(p1, f) for f in os.listdir(p1) if f.endswith('.docx') or f.endswith('.doc')]
        files2_pool = [os.path.join(p2, f) for f in os.listdir(p2) if f.endswith('.docx') or f.endswith('.doc')]
        
        results = []
        
        for f1 in files1:
            match = find_best_match(f1, files2_pool)
            if match:
                print(f"✅ Matched: {os.path.basename(f1)} == {os.path.basename(match)}")
                r = process_pair(f1, match, reporter)
                results.append(r)
                # files2_pool.remove(match) # Optional: don't reuse
            else:
                print(f"⚠️ No match found for {os.path.basename(f1)}")
                
        print(f"\nBatch processing complete. Generated {len(results)} reports.")
        
    elif os.path.isfile(p1) and os.path.isfile(p2):
        print("📄 Single File Mode")
        r = process_pair(p1, p2, reporter)
        print(f"Report: {r}")
    else:
        print("Error: Please provide two files OR two directories.")

if __name__ == "__main__":
    main()
