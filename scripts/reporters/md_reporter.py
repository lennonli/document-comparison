
import os
import datetime

class MDReporter:
    def generate(self, diff_report, issues1, issues2, f1_path, f2_path, llm_insights=None):
        lines = []
        name1 = os.path.basename(f1_path)
        name2 = os.path.basename(f2_path)
        
        lines.append(f"# 📊 文档比对报告: {name1} vs {name2}")
        lines.append(f"> 生成时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"")
        
        # 0. AI Insight (New)
        if llm_insights:
            lines.append("## 🤖 AI 智能洞察 (LLM Insights)")
            for insight in llm_insights:
                lines.append(f"**总体评价**: {insight.get('summary', '发现差异')}")
                lines.append(f"")
                lines.append(f"| 差异点 | {name1} | {name2} | 潜在风险 |")
                lines.append(f"| :--- | :--- | :--- | :--- |")
                for d in insight.get('details', []):
                    lines.append(f"| {d.get('item')} | {d.get('doc_a')} | {d.get('doc_b')} | {d.get('risk')} |")
            lines.append(f"")
            lines.append(f"---")
            lines.append(f"")

        # 1. Substantive Diffs
        lines.append("## 1. ⚠️ 实质性差异 (表格数据)")
        
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

        # 2. Logic Checks
        lines.append("## 2. 🧠 深度逻辑与合规性检查")
        
        lines.append(f"### 📄 文件 1: {name1}")
        if issues1:
            for i in issues1:
                icon = "📝"
                if "逻辑" in i or "验算" in i: icon = "🧮"
                elif "引用" in i or "定义" in i: icon = "🔗"
                lines.append(f"- {icon} {i}")
        else:
            lines.append("- ✅ 检查通过。")
            
        lines.append(f"")
        lines.append(f"### 📄 文件 2: {name2}")
        if issues2:
            for i in issues2:
                icon = "📝"
                if "逻辑" in i or "验算" in i: icon = "🧮"
                elif "引用" in i or "定义" in i: icon = "🔗"
                lines.append(f"- {icon} {i}")
        else:
            lines.append("- ✅ 检查通过。")
            
        output_dir = os.path.dirname(f1_path)
        report_filename = f"Report_{name1}_vs_{name2}.md"
        output_path = os.path.join(output_dir, report_filename)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(lines))
            
        return output_path
