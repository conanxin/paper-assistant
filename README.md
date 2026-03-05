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

## Open-Source Project Scope（论文 → 图像叙事）

本项目已从“论文精读助手”扩展为一个可演进的 **Research-to-Visual-Narrative Pipeline**：

- 输入论文链接/PDF
- 自动生成研究卡片（问题/方法/结论/限制）
- 自动生成 10~15 页图像叙事分镜与文案
- 提供页级证据映射（每页主张可追溯到原文）
- 连接免费出图后端生成视觉草图
- 合成初版 PDF，支持人工审校后发布

### Why this project

学术内容往往“有价值但难传播”。本项目希望在 **可读性、可信度、可追溯性** 三者间取得平衡，让研究更高效地走向公众。

---

## Current Progress（截至 2026-03-05）

### ✅ 已完成

1. **Context FS 治理基础设施**（可追溯、可评估、可巡检）
   - `context_manifest.json`
   - `analysis.md`
   - `evaluation.json`
   - `memory_delta.md`
   - `run_log.md`

2. **自动化脚本（M1-M4）**
   - `scripts/context_constructor.py`
   - `scripts/context_updater.py`
   - `scripts/context_evaluator.py`
   - `scripts/context_healthcheck.py`

3. **流程验收通过**
   - 3 个真实任务样本跑通
   - 结构与质量巡检通过

4. **图像叙事方法资产**
   - 12 页分镜骨架
   - 逐页可发布文案模板
   - 证据映射表
   - 线框坐标与页面 JSON 模板

### 🚧 进行中

- Web MVP（输入页 / 任务进度页 / 结果审校页）
- 免费后端出图接入与容错

---

## Vision

打造一个开源的“论文传播编译器”：

> 研究者提交论文 → 系统生成可发布图像叙事 → 社会公众更快理解研究价值。

长期目标：

- 多语言（中英双语）
- 多体裁输出（漫画、图解长文、课程讲义）
- 协作审校（研究者 + 编辑 + 设计师）
- 模板生态（叙事模板、视觉风格包、证据评估器）

---

## Roadmap

### v0.1 (MVP)
- Web 三页闭环：输入→进度→结果
- 自动生成研究卡片、分镜脚本、证据映射
- 草图出图 + 初版 PDF 合成

### v0.2
- 页级编辑与单页重绘
- QA 报告（事实一致性/可读性/视觉一致性）

### v0.3
- 多后端渲染（免费优先 + fallback）
- 团队协作审校与发布归档

---

## Contributing Focus

欢迎贡献以下模块：

- 论文解析器（parser）
- 叙事模板（story templates）
- 视觉提示词包（prompt packs）
- 事实校验器（evidence validators）
- 排版主题（layout themes）

## License

MIT
