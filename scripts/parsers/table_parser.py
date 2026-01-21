
import re
from html.parser import HTMLParser
import html

class HTMLTableParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tables = []
        self.current_table = []
        self.current_row = []
        self.current_cell = []
        self.in_cell = False
    
    def handle_starttag(self, tag, attrs):
        if tag == 'table':
            self.current_table = []
        elif tag == 'tr':
            self.current_row = []
        elif tag == 'td' or tag == 'th':
            self.in_cell = True
            self.current_cell = []
            
    def handle_endtag(self, tag):
        if tag == 'table':
            if self.current_table: self.tables.append(self.current_table)
        elif tag == 'tr':
            if self.current_row: self.current_table.append(self.current_row)
        elif tag == 'td' or tag == 'th':
            self.in_cell = False
            self.current_row.append("".join(self.current_cell).strip())
            
    def handle_data(self, data):
        if self.in_cell:
            self.current_cell.append(data)

class TableParser:
    def parse(self, html_path):
        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        parser = HTMLTableParser()
        parser.feed(content)
        
        # Process tables into keyed dictionaries
        processed_tables = []
        
        for table in parser.tables:
            if not table: continue
            
            # Identify headers
            # Heuristic: First row that has meaningful columns
            header_idx = -1
            headers = []
            
            for i, row in enumerate(table[:5]):
                # Only text
                clean_row = [self.normalize(c) for c in row]
                # If row has keywords
                s = "".join(clean_row)
                if len(s) > 5 and ("名称" in s or "号" in s or "金额" in s or "日期" in s or "人" in s):
                    header_idx = i
                    headers = clean_row
                    break
            
            if header_idx == -1:
                # Treat as generic list? Skip for now validation
                continue
                
            # Convert rows to dicts
            rows_data = []
            last_valid_row = {} # For merging support
            
            for row in table[header_idx+1:]:
                if not any(row): continue
                
                item = {}
                # Map by header name (approx) or index
                # We store both index-based and header-key based
                for k, cell in enumerate(row):
                    if k < len(headers):
                        h_name = headers[k]
                        item[h_name] = self.normalize(cell)
                        item[f"__col_{k}"] = self.normalize(cell)
                
                rows_data.append(item)
            
            # Detect primary key for this table
            pk = self.detect_primary_key(headers, rows_data)
            
            processed_tables.append({
                "headers": headers,
                "rows": rows_data,
                "pk": pk
            })
            
        return processed_tables

    def normalize(self, text):
        if not text: return ""
        text = html.unescape(text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def detect_primary_key(self, headers, rows):
        # Prefer: Patent No, Contract No, or Combined (Party + Name)
        possible_pks = []
        
        for h in headers:
            if "专利号" in h or "合同编号" in h or "证书号" in h:
                return [h]
        
        # If no explicit ID, look for Name/Party
        name_col = None
        party_col = None
        
        for h in headers:
            if "名称" in h and "客户" not in h and "供应商" not in h: name_col = h
            if "客户" in h or "供应商" in h or "当事人" in h or "对象" in h: party_col = h
            
        if name_col and party_col:
            return [party_col, name_col]
        if name_col:
            return [name_col]
            
        return ["__col_0"] # Fallback to first column
