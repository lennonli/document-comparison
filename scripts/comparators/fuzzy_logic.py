
import re

class DataComparator:
    def compare_datasets(self, data1, data2):
        # We need to match tables. 
        # Heuristic: Compare headers intersect.
        
        report = []
        
        # Match tables
        # Ideally, we greedily match tables that look similar
        used_indices_2 = set()
        
        for t1_idx, t1 in enumerate(data1):
            best_t2_idx = -1
            best_header_score = -1
            
            h1_set = set(t1['headers'])
            
            for t2_idx, t2 in enumerate(data2):
                if t2_idx in used_indices_2: continue
                
                h2_set = set(t2['headers'])
                # Intersection score
                inter = h1_set.intersection(h2_set)
                score = len(inter)
                
                if score > best_header_score and score > 0:
                    best_header_score = score
                    best_t2_idx = t2_idx
            
            if best_t2_idx != -1:
                used_indices_2.add(best_t2_idx)
                # Compare these two tables
                t_diff = self.compare_table(t1, data2[best_t2_idx])
                if t_diff:
                    report.append(t_diff)
            else:
                pass # Unmatched table in file 1
                
        return report

    def compare_table(self, t1, t2):
        # Use Primary Key to align rows
        # PKs might be slightly different key names, so we need to map headers first?
        # Assuming header names are relatively consistent or using first matching ones.
        
        # Create map of rows by PK
        rows1_map = {}
        for r in t1['rows']:
            key = self.get_key_val(r, t1['pk'])
            rows1_map[key] = r
            
        rows2_map = {}
        for r in t2['rows']:
            key = self.get_key_val(r, t2['pk'])
            rows2_map[key] = r
            
        all_keys = set(rows1_map.keys()) | set(rows2_map.keys())
        table_diffs = {
            "title": f"Table comparison (Key: {t1['pk']})",
            "missing_in_file2": [],
            "missing_in_file1": [],
            "row_diffs": []
        }
        
        for k in all_keys:
            if not k: continue # Skip empty keys
            
            r1 = rows1_map.get(k)
            r2 = rows2_map.get(k)
            
            if not r1:
                table_diffs["missing_in_file1"].append(f"Row {k}")
                continue
            if not r2:
                table_diffs["missing_in_file2"].append(f"Row {k}")
                continue
                
            # Compare fields
            # We iterate over headers of t1
            row_field_diffs = []
            
            for h in t1['headers']:
                val1 = r1.get(h, "")
                # Find corresponding header in t2
                # Simple exact match for now
                val2 = r2.get(h, "")
                
                # Check for equivalence
                if not self.is_equivalent(val1, val2, h):
                    row_field_diffs.append({
                        "field": h,
                        "v1": val1,
                        "v2": val2
                    })
            
            if row_field_diffs:
                table_diffs["row_diffs"].append({
                    "key": k,
                    "diffs": row_field_diffs
                })
                
        return table_diffs

    def get_key_val(self, row, pk_cols):
        vals = []
        for c in pk_cols:
            vals.append(row.get(c, row.get(c.replace('Mini', 'Mini '), ""))) # HACK for specific case
        return "|".join(vals)

    def is_equivalent(self, v1, v2, field_name):
        if v1 == v2: return True
        
        # Check numeric
        if "金额" in field_name or "价格" in field_name or "收入" in field_name:
             n1 = self.parse_num(v1)
             n2 = self.parse_num(v2)
             if n1 is not None and n2 is not None:
                 return abs(n1 - n2) < 0.01
                 
        # Check date
        if "日期" in field_name or "时间" in field_name:
            d1 = self.normalize_date(v1)
            d2 = self.normalize_date(v2)
            if d1 and d2 and d1 == d2: return True
            
        # Check string loose
        s1 = v1.replace(" ", "").replace("（", "(").replace("）", ")")
        s2 = v2.replace(" ", "").replace("（", "(").replace("）", ")")
        if s1 == s2: return True
        
        return False

    def parse_num(self, s):
        try:
            clean = s.replace(",", "").replace("，", "").replace("万元", "").replace("元", "")
            return float(clean)
        except:
            return None

    def normalize_date(self, s):
        # Copy logic from previous task
        m1 = re.search(r'(\d{4})年(\d{1,2})月(\d{1,2})日', s)
        if m1: return f"{m1.group(1)}-{m1.group(2).zfill(2)}-{m1.group(3).zfill(2)}"
        m2 = re.search(r'(\d{4})\.(\d{1,2})\.(\d{1,2})', s)
        if m2: return f"{m2.group(1)}-{m2.group(2).zfill(2)}-{m2.group(3).zfill(2)}"
        return s
