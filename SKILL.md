---
name: document-comparison
description: Intelligent document comparison tool for analyzing substantive differences between contracts, patent lists, and other structured documents. Also performs automated proofreading for typos and formatting errors.
---

# Document Comparison Skill

Use this skill when the user asks to "compare documents", "contrast files", "check consistency", "find differences", "比较文档", "对比文档", "核对文件", or uses the command `document-comparison`.

## Usage

This skill takes two file paths as primary arguments. It is designed to handle Word (`.docx`) files but can also support text-based formats.

## Workflow

1.  **Preparation**:
    -   Identify the two absolute file paths provided by the user.
    -   If the files are `.docx`, convert them to HTML internally to preserve table structures using `textutil`.

2.  **Execution**:
    -   Run the Python script `scripts/compare_docs.py` with the two file paths.
    -   The script will:
        -   Parse tables and text.
        -   Align data based on intelligent key guessing (e.g., matching "Contract Name" or "Patent No").
        -   Compare fields using fuzzy logic (handling date formats, currency units).
        -   Check for common errors (typos, open brackets).

3.  **Reporting**:
    -   The script outputs a comprehensive Markdown report.
    -   Present this report to the user.
    -   Highlight critical "Substantive Differences" (Money, Dates, Missing Items) first.

## Quick Start Command

```bash
python3 ~/.gemini/antigravity/skills/document-comparison/scripts/compare_docs.py <file1_path> <file2_path>
```
