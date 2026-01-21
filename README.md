# Document Comparison Skill

An intelligent document comparison tool designed for legal and financial professionals. It goes beyond simple text diffing to understand tables, dates, amounts, and structured data.

## Features

- **📊 Intelligent Table Comparison**: Automatically aligns rows even if the order is shuffled (e.g., by Patent No. or Contract Name).
- **🧮 Logic & Data Verification**: 
  - Validates "Total" rows against the sum of their parts.
  - Checks if percentage columns sum to 100%.
- **📑 Consistency Checks**: 
  - Detects broken references (e.g., "see Section 5.1" where 5.1 doesn't exist).
  - Identifies inconsistent definitions (e.g., defining a Short Name but continuing to use the Full Name).
- **📝 Automated Proofreading**: Detects typos (e.g., missing characters in bank names) and unbalanced brackets.
- **📂 Batch Mode**: Compare entire folders of documents automatically.

## Installation

```bash
# Clone this repository to your skills directory
git clone https://github.com/<your-username>/document-comparison.git ~/.gemini/antigravity/skills/document-comparison
```

## Usage

This skill is designed to be used with the Antigravity Agent.

**Un-batch Mode:**
```
@document-comparison /path/to/contract_v1.docx /path/to/contract_v2.docx
```

**Batch Mode:**
```
@document-comparison /path/to/folder_v1/ /path/to/folder_v2/
```

## Structure

- `SKILL.md`: Entry point and instructions for the AI Agent.
- `scripts/`: Python source code.
  - `compare_docs.py`: Main entry script.
  - `parsers/`: HTML/Table parsing logic.
  - `comparators/`: Comparison engines (Fuzzy, Logic, Consistency).
  - `reporters/`: Markdown report generation.
