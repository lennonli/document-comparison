
import os
import datetime

class MDReporter:
    def generate(self, diff_report, issues1, issues2, f1_path, f2_path):
        lines = []
        name1 = os.path.basename(f1_path)
        name2 = os.path.basename(f2_path)
        
        lines.append(f"# 📊 文档比对报告: {name1} vs {name2}")
        lines.append(f"> 生成时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"")
        
        # High Level Summary
        total_substantive = 0
        for t in diff_report:
            if t['row_diffs'] or t['missing_in_file1'] or t['missing_in_file2']:
                total_substantive += 1
                
        lines.append(f"## 概览")
        if total_substantive == 0 and not issues1 and not issues2:
             lines.append("🎉 **完美匹配**：两份文档未发现实质性差异或逻辑错误。")
        else:
             lines.append(f"- 实质性差异表格数: **{total_substantive}**")
             lines.append(f"- 文件1 风险/提示数: **{len(issues1)}**")
             lines.append(f"- 文件2 风险/提示数: **{len(issues2)}**")
        
        lines.append(f"")
        lines.append("## 1. ⚠️ 实质性差异")
        
        has_table_diff = False
        for table_diff in diff_report:
            if not table_diff['row_diffs'] and not table_diff['missing_in_file1'] and not table_diff['missing_in_file2']:
                continue
            has_table_diff = True
            lines.append(f"### {table_diff['title']}")
            
            if table_diff['missing_in_file1']:
                lines.append(f"**🔴 仅在 {name2} 中存在:**")
                for m in table_diff['missing_in_file1']: lines.append(f"- {m}")
            
            if table_diff['missing_in_file2']:
                lines.append(f"**🔴 仅在 {name1} 中存在:**")
                for m in table_diff['missing_in_file2']: lines.append(f"- {m}")
                    
            if table_diff['row_diffs']:
                lines.append(f"**⚠️ 内容不一致:**")
                lines.append(f"| 关键对象 | 字段 | {name1} | {name2} |")
                lines.append(f"| :--- | :--- | :--- | :--- |")
                for r in table_diff['row_diffs']:
                    key = r['key']
                    for d in r['diffs']:
                        lines.append(f"| {key} | {d['field']} | {d['v1']} | {d['v2']} |")
            lines.append("")
        
        if not has_table_diff:
            lines.append("✅ 表格数据一致。")

        lines.append("## 2. 🧠 深度逻辑与合规性检查")
        
        lines.append(f"### 📄 文件 1: {name1}")
        if issues1:
            for i in issues1:
                # Add icons based on error type
                icon = "📝"
                if "逻辑" in i or "验算" in i: icon = "🧮"
                elif "引用" in i or "定义" in i: icon = "🔗"
                lines.append(f"- {icon} {i}")
        else:
            lines.append("- ✅ 检查通过，无明显异常。")
            
        lines.append(f"")
        lines.append(f"### 📄 文件 2: {name2}")
        if issues2:
            for i in issues2:
                icon = "📝"
                if "逻辑" in i or "验算" in i: icon = "🧮"
                elif "引用" in i or "定义" in i: icon = "🔗"
                lines.append(f"- {icon} {i}")
        else:
            lines.append("- ✅ 检查通过，无明显异常。")
            
        # Save
        report_filename = f"Report_{name1}_vs_{name2}.md"
        # Avoid slashes in filename if names have them, usually fine
        
        # If batch mode, maybe save in a 'reports' folder? 
        # For now save alongside file1
        output_dir = os.path.dirname(f1_path)
        output_path = os.path.join(output_dir, report_filename)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(lines))
            
        return output_path
