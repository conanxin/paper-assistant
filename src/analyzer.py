from __future__ import annotations

import re
from dataclasses import dataclass

from .llm_client import LLMClient
from .parser import ParsedPaper


@dataclass
class AnalysisResult:
    markdown: str
    key_claims: list[str]


class Analyzer:
    """Deterministic summarizer with optional LLM generation."""

    def analyze(
        self,
        parsed: ParsedPaper,
        mode: str = "deep",
        target_language: str = "zh",
        llm_client: LLMClient | None = None,
    ) -> AnalysisResult:
        mode = mode.lower().strip()
        if mode not in {"standard", "deep"}:
            mode = "deep"

        if llm_client is not None:
            llm_markdown = llm_client.generate_markdown(parsed=parsed, mode=mode, language=target_language)
            llm_claims = [line for line in llm_markdown.splitlines() if line.startswith("- ")]
            return AnalysisResult(markdown=llm_markdown.strip() + "\n", key_claims=llm_claims)

        abstract = self._clean(parsed.sections.get("abstract", ""))
        intro = self._clean(parsed.sections.get("introduction", ""))
        method = self._clean(parsed.sections.get("method", ""))
        results = self._clean(parsed.sections.get("results", ""))
        conclusion = self._clean(parsed.sections.get("conclusion", ""))

        summary_len = 2 if mode == "standard" else 4
        method_len = 2 if mode == "standard" else 4
        result_len = 2 if mode == "standard" else 4

        overview = self._take_sentences(abstract or intro, summary_len)
        method_points = self._sentences_as_bullets(method or intro, method_len, tag="[论文原文]")
        result_points = self._sentences_as_bullets(results or conclusion or intro, result_len, tag="[论文原文]")
        limitations = self._build_limitations(parsed, mode, target_language=target_language)

        claims = []
        for line in (result_points + limitations):
            if line.startswith("- "):
                claims.append(line)

        if target_language == "zh":
            md = [
                f"# {parsed.title}",
                "",
                f"## 模式\n{mode}",
                "",
                "## 概览",
                (overview + " [论文原文]") if overview else "未能稳定提取概览。 [论文原文]",
                "",
                "## 方法要点",
                *(method_points or ["- 未能稳定提取方法细节。 [论文原文]"]),
                "",
                "## 核心结论",
                *(result_points or ["- 未能稳定提取结果细节。 [论文原文]"]),
                "",
                "## 局限与开放问题",
                *limitations,
                "",
                "## 证据规则",
                "- 来自论文原文的陈述标记为 `[论文原文]`。",
                "- 外部补充信息标记为 `[外部补充]`。",
                "- 当前为规则模式，若需高质量中文改写请启用 LLM。 [外部补充]",
            ]
        else:
            md = [
                f"# {parsed.title}",
                "",
                f"## Mode\n{mode}",
                "",
                "## Overview",
                overview or "No overview extracted. [论文原文]",
                "",
                "## Methods",
                *(method_points or ["- Method details not confidently extracted. [论文原文]"]),
                "",
                "## Key Conclusions",
                *(result_points or ["- Result details not confidently extracted. [论文原文]"]),
                "",
                "## Limitations & Open Questions",
                *limitations,
                "",
                "## Evidence Policy",
                "- Statements sourced from the paper are tagged `[论文原文]`.",
                "- Any non-paper background note must be tagged `[外部补充]`.",
            ]

        return AnalysisResult(markdown="\n".join(md).strip() + "\n", key_claims=claims)

    @staticmethod
    def _clean(text: str) -> str:
        return re.sub(r"\s+", " ", text).strip()

    @staticmethod
    def _take_sentences(text: str, n: int) -> str:
        sents = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
        return " ".join(sents[:n])

    def _sentences_as_bullets(self, text: str, n: int, tag: str) -> list[str]:
        sents = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if len(s.strip()) > 25]
        selected = sents[:n]
        return [f"- {self._truncate(s, 220)} {tag}" for s in selected]

    @staticmethod
    def _truncate(s: str, limit: int) -> str:
        if len(s) <= limit:
            return s
        return s[: limit - 3].rstrip() + "..."

    def _build_limitations(self, parsed: ParsedPaper, mode: str, target_language: str = "zh") -> list[str]:
        if target_language == "zh":
            lines = [
                "- 当前摘要由规则方法生成，可能遗漏细微论证链。 [外部补充]",
                "- 使用前请回看 PDF 中的公式、表格和附录结论。 [外部补充]",
            ]
        else:
            lines = [
                "- The summary is generated with deterministic heuristics and can miss nuanced claims. [外部补充]",
                "- Verify equations, tables, and appendix-only findings directly in the PDF before reuse. [外部补充]",
            ]
        if mode == "deep":
            refs = parsed.sections.get("references", "")
            ref_count = len(re.findall(r"\[[0-9]+\]", refs))
            if target_language == "zh":
                lines.append(f"- 提取文本中大约检测到 {ref_count} 条方括号引用。 [论文原文]")
            else:
                lines.append(f"- Detected approximately {ref_count} bracket-style references in extracted text. [论文原文]")
        return lines
