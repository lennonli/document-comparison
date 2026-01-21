# Document Comparison Skill / 智能文档比对技能

[English](#english) | [中文](#chinese)

---

<a name="english"></a>
## English

An intelligent document comparison tool designed for legal and financial professionals. It goes beyond simple text diffing to understand tables, dates, amounts, and structured data.

### Features

- **📊 Intelligent Table Comparison**: Automatically aligns rows even if the order is shuffled (e.g., by Patent No. or Contract Name), preventing false positives caused by sorting differences.
- **🧮 Logic & Data Verification**: 
  - **Vertical Sums**: Automatically verifies if the "Total" row equals the sum of its parts.
  - **Percentage Checks**: Verifies if percentage columns sum up to approx. 100%.
- **📑 Consistency Checks**: 
  - **Broken Links**: Detects references to non-existent sections (e.g., "see Section 5.1" where 5.1 doesn't exist).
  - **Definitions**: Identifies inconsistent definitions (e.g., defining a "Short Name" but continuing to use the "Full Name").
- **📝 Automated Proofreading**: Detects typos (e.g., missing characters in critical names like "Bank of China") and unbalanced brackets.
- **📂 Batch Mode**: Supports comparing entire folders of documents, automatically matching files by name.

### Installation

```bash
# Clone this repository to your skills directory
git clone https://github.com/lennonli/document-comparison.git ~/.gemini/antigravity/skills/document-comparison
```

### Usage

This skill is designed to be used with the Antigravity Agent.

**Single File Mode:**
```
@document-comparison /path/to/contract_v1.docx /path/to/contract_v2.docx
```

**Batch Mode:**
```
@document-comparison /path/to/folder_v1/ /path/to/folder_v2/
```

### Structure

- `SKILL.md`: Entry point and instructions for the AI Agent.
- `scripts/`: Python source code.
  - `compare_docs.py`: Main entry script.
  - `parsers/`: HTML/Table parsing logic.
  - `comparators/`: Comparison engines (Fuzzy, Logic, Consistency).
  - `reporters/`: Markdown report generation.

---

<a name="chinese"></a>
## 中文 (Chinese)

这就一款专为法律和投行专业人士设计的智能文档比对工具。它超越了简单的文本比对，能够理解表格、日期、金额和结构化数据。

### 核心功能

- **📊 智能表格对齐**：即使行序被打乱（例如按专利号或合同名称重新排序），也能自动识别并对齐进行比对，避免因排序不同导致的误报。
- **🧮 逻辑与数据验算**：
  - **合计行验算**：自动检查表格中的“合计”行是否等于上方分项之和。
  - **百分比验算**：检查百分比列的加总是否接近 100%。
- **📑 一致性检查**：
  - **断链检测**：检测文中引用的章节是否存在（例如引用了“见第 5.1 条”但文中没有 5.1 条）。
  - **定义一致性**：识别定义后未使用的简称（例如定义了“简称”，但后文仍大量使用全称）。
- **📝 自动校对**：检测低级错误（例如“中国银深圳分行”漏字）以及中英文括号不匹配等问题。
- **📂 批量模式**：支持直接传入两个文件夹，系统会自动按文件名相似度配对并批量生成报告。

### 安装方法

```bash
# 将此仓库克隆到您的 skills 目录
git clone https://github.com/lennonli/document-comparison.git ~/.gemini/antigravity/skills/document-comparison
```

### 使用方法

本技能旨在配合 Antigravity Agent 使用。

**单文件比对：**
```
比较文档 /path/to/contract_v1.docx /path/to/contract_v2.docx
```

**批量比对：**
```
比较文档 /path/to/folder_v1/ /path/to/folder_v2/
```

### 项目结构

- `SKILL.md`: AI Agent 的入口文件和指令。
- `scripts/`: Python 源代码。
  - `compare_docs.py`: 主程序入口。
  - `parsers/`: HTML/表格解析逻辑。
  - `comparators/`: 各类比对引擎（模糊匹配、逻辑校验、一致性校验）。
  - `reporters/`: Markdown 报告生成器。
