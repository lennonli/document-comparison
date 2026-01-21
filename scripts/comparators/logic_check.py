
import re

class LogicChecker:
    def check_table_logic(self, table_data):
        """
        Checks a parsed table for:
        1. Vertical sum integrity (if 'Total' row exists)
        2. Percentage sum integrity (if '%' columns exist)
        """
        issues = []
        
        headers = table_data.get('headers', [])
        rows = table_data.get('rows', [])
        
        if not rows: return []
        
        # 1. Identify Numeric Columns
        # We assume columns with "金额", "收入", "价格", "Number", "Amount" are numeric
        # Or simply try to parse meaningful numbers
        numeric_cols_indices = []
        percentage_cols_indices = []
        
        for idx, h in enumerate(headers):
            if "金额" in h or "小计" in h or "总价" in h or "收入" in h or "费用" in h:
                numeric_cols_indices.append(idx)
            if "%" in h or "占比" in h or "比例" in h:
                percentage_cols_indices.append(idx)

        # 2. Check Vertical Sums (Total Row)
        # Look for a row where the first column (or name column) says "合计" or "Total"
        total_row = None
        total_row_idx = -1
        
        # We gather "sum" of data rows
        calculated_sums = {idx: 0.0 for idx in numeric_cols_indices}
        
        data_rows_count = 0
        
        for r_idx, row in enumerate(rows):
            # Check if this is a Total row
            # Usually based on the primary text column
            is_total = False
            first_val = str(list(row.values())[0]) if row else ""
            if "合计" in first_val or "总计" in first_val or "Total" in first_val:
                is_total = True
                
            if is_total:
                total_row = row
                total_row_idx = r_idx
                continue # Don't add to sum
            
            # Add to calculated sums
            for col_idx in numeric_cols_indices:
                col_name = headers[col_idx]
                val = self.parse_num(row.get(col_name, ""))
                if val is not None:
                    calculated_sums[col_idx] += val
            
            data_rows_count += 1
            
        # Verify Total
        if total_row:
            for col_idx in numeric_cols_indices:
                col_name = headers[col_idx]
                declared_total = self.parse_num(total_row.get(col_name, ""))
                
                if declared_total is not None and declared_total > 0:
                    calc_total = calculated_sums[col_idx]
                    # Allow error margin (e.g. 1.0 for rounding issues in thousands)
                    # Usually 0.01 is tight, but sometimes large numbers have rounding. 
                    # If diff is exactly 0, great. If diff > 1% or abs > 1, warn.
                    diff = abs(declared_total - calc_total)
                    if diff > 1.0: # Loose tolerance for "万元" rounding
                        issues.append(f"合计行验算失败 (列: {col_name}): 表格显示 {declared_total}, 计算得出 {calc_total:.2f} (差 {diff:.2f})")

        # 3. Check Percentages (Sum to 100%)
        # Only if we have percentage columns
        for col_idx in percentage_cols_indices:
            col_name = headers[col_idx]
            col_sum = 0.0
            count = 0
            
            # Iterate all data rows (excluding total row if found)
            for r_idx, row in enumerate(rows):
                if r_idx == total_row_idx: continue
                
                val = self.parse_percent(row.get(col_name, ""))
                if val is not None:
                    col_sum += val
                    count += 1
            
            if count > 1:
                # Expect sum to be approx 100 or 1.0
                # Heuristic: if sum is around 100 (+- 0.5) or 1.0 (+- 0.01)
                if 99.0 <= col_sum <= 101.0:
                    pass # Good
                elif 0.99 <= col_sum <= 1.01:
                    pass # Good
                else:
                    if col_sum > 0: # Avoid empty cols
                        issues.append(f"百分比验算异常 (列: {col_name}): 总和为 {col_sum:.2f} (预期 100% 或 1)")

        return issues

    def parse_num(self, s):
        try:
            if not s: return None
            clean = s.replace(",", "").replace("，", "").replace("万元", "").replace("元", "")
            if clean == "-": return 0.0
            return float(clean)
        except:
            return None

    def parse_percent(self, s):
        try:
            if not s: return None
            clean = s.replace("%", "").replace(",", "").replace(" ", "")
            if clean == "-": return 0.0
            # Note: 50% could be 50 or 0.5 depending on context. 
            # We return raw number here, heuristic check later.
            return float(clean)
        except:
            return None
