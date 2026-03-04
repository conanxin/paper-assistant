# Paper Assistant

[![CI](https://github.com/conanxin/paper-assistant/actions/workflows/ci.yml/badge.svg)](https://github.com/conanxin/paper-assistant/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

本地运行的论文精读助手（Web GUI）。支持输入论文链接或上传 PDF，输出结构化解读、引用审计，并可一键保存到 Obsidian。

## Screenshots / Demo

> 你可以把界面截图或演示 GIF 放到 `docs/assets/`，README 会自动展示。

### UI Preview（占位）

- 首页输入区：`docs/assets/ui-home.png`
- 输出与审计区：`docs/assets/ui-result.png`
- 保存成功状态：`docs/assets/ui-save.png`

### GIF Demo（占位）

![Demo](docs/assets/demo.gif)

> 如果 `demo.gif` 尚未添加，GitHub 上会显示为 broken image，这是正常占位行为。

## Features

- URL 输入（arXiv / 其他可访问论文页）
- PDF 上传解析（`pdftotext` 可用时效果更好）
- 输出语言：中文 / 英文
- 两种生成模式：
  - **Rule-based**（默认，无模型调用）
  - **LLM 模式**（OpenAI-compatible API，可选）
- 引用审计（每条要点需带 `[论文原文]` 或 `[外部补充]`）
- 审计不通过时禁止保存到 Obsidian
- 一键启动脚本 `run.sh`（端口冲突自动回退）

## Tech Stack

- Python 3.12+
- Streamlit
- OpenAI-compatible HTTP API（可选）

## Project Structure

```text
paper-assistant/
  app.py
  run.sh
  requirements.txt
  src/
    input_adapter.py
    parser.py
    analyzer.py
    llm_client.py
    citation_auditor.py
    obsidian_sink.py
    pipeline.py
  scripts/
    demo_e2e.py
```

## Quick Start

### 1) 安装依赖

```bash
cd paper-assistant
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

> 如果你的系统缺少 `python3-venv`，请先安装对应系统包。

### 2) 启动

```bash
./run.sh
```

默认端口 `8511`，若被占用会自动尝试 `8512`。

### 3) 使用

- 输入论文 URL 或上传 PDF
- 选择输出语言（`zh` / `en`）
- 可选开启 LLM 模式并填写：
  - API Base（如 `https://api.openai.com/v1`）
  - API Key
  - Model（如 `gpt-4o-mini`）

页面会显示：
- `generation_mode`（`rule-based` / `llm`）
- `model`（实际使用模型名）

## LLM Notes

- 不启用 LLM 时：完全本地规则生成（`deterministic-template`）
- 启用 LLM 时：调用 OpenAI-compatible `/chat/completions`
- LLM 调用失败会自动回退到 rule-based，并提示错误

## End-to-End Demo

```bash
PYTHONPATH=. python3 scripts/demo_e2e.py
```

会输出证据文件路径（Markdown + 审计 JSON）。

## Obsidian Output

默认保存目录：

`/mnt/d/obsidian_nov/nov/Inbox/研究摘录/`

可在 `src/obsidian_sink.py` 修改。

## Limitations

- Rule-based 模式对复杂公式/表格理解有限
- 链接抓取受目标站点反爬策略影响
- 非结构化 PDF 可能需要 OCR 预处理

## License

MIT
