---
name: Document Comparison
description: Intelligent comparison of legal/financial documents.
usage: |
  compare-docs <file1> <file2>
  compare-docs <dir1> <dir2>
---

# Document Comparison Skill

This skill helps users compare two documents (e.g., Lawyer's version vs Broker's version) to find substantive differences.

## Features
1.  **Strict Logic Check**: Python script validates numbers, totals, and cross-references.
2.  **Semantic Analysis**: **YOU (The Agent)** will read the text and identify semantic differences that the script might miss.

## Workflow

### Step 1: Run the Mechanical Comparison
Run the python script to generate the base report and extract text.
**IMPORTANT**: The script has been updated to output the *plain text* content of the documents to `.txt` files in the same directory as the report.

```bash
python3 ~/.gemini/antigravity/skills/document-comparison/scripts/compare_docs.py "/absolute/path/to/file1.docx" "/absolute/path/to/file2.docx"
```

### Step 2: Agent Intelligence (Crucial!)
The script is "dumb" but you are "smart".
1.  **Read the Aligned JSON**: Look for file `Comparison_Aligned_<filename>.json`.
2.  **Analyze Section by Section**: The JSON contains aligned sections from both documents. Loop through each item:
    - If `text_a` or `text_b` is empty, note the missing section.
    - Compare the content of `text_a` and `text_b`.
    - **Focus on Facts**: Dates, Amounts, Names of Entities, Key Personnel (Actual Controller), Responsibilities.
3.  **Update the Report**:
    - Open the generated `Report_*.md`.
    - Insert `## 🤖 Agent Insight` section.
    - Summarize differences found in each section. Be concise but specific.

### Step 3: Cleanup
Delete the temporary JSON files.

```bash
rm /path/to/Text_Extract_*.txt
```

### Step 4: Notify User
Present the final report to the user.
