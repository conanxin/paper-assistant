from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Optional
from urllib import request

from .parser import ParsedPaper


@dataclass
class LLMConfig:
    api_base: str
    api_key: str
    model: str
    timeout: int = 60


class LLMClient:
    """OpenAI-compatible client for Chinese paper interpretation."""

    def __init__(self, config: LLMConfig):
        self.config = config

    @staticmethod
    def from_params(api_base: str | None, api_key: str | None, model: str | None) -> "LLMClient":
        base = (api_base or os.getenv("OPENAI_API_BASE") or "https://api.openai.com/v1").rstrip("/")
        key = api_key or os.getenv("OPENAI_API_KEY") or ""
        mdl = model or os.getenv("OPENAI_MODEL") or "gpt-4o-mini"
        if not key:
            raise ValueError("LLM enabled but API key is missing. Please set OPENAI_API_KEY or fill key in UI.")
        return LLMClient(LLMConfig(api_base=base, api_key=key, model=mdl))

    def generate_markdown(self, parsed: ParsedPaper, mode: str = "deep", language: str = "zh") -> str:
        language_label = "简体中文" if language == "zh" else "English"
        prompt = self._build_prompt(parsed=parsed, mode=mode, language_label=language_label)

        payload = {
            "model": self.config.model,
            "temperature": 0.2,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are an academic paper analyst. Output STRICT markdown only. "
                        "Every bullet claim must end with [论文原文] or [外部补充]."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
        }

        req = request.Request(
            url=f"{self.config.api_base}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        with request.urlopen(req, timeout=self.config.timeout) as resp:
            body = json.loads(resp.read().decode("utf-8", errors="ignore"))

        content = body["choices"][0]["message"]["content"].strip()
        return content

    @staticmethod
    def _build_prompt(parsed: ParsedPaper, mode: str, language_label: str) -> str:
        max_len = 12000 if mode == "deep" else 6000
        text = "\n\n".join(
            [
                f"[ABSTRACT]\n{parsed.sections.get('abstract', '')}",
                f"[INTRODUCTION]\n{parsed.sections.get('introduction', '')}",
                f"[METHOD]\n{parsed.sections.get('method', '')}",
                f"[EXPERIMENTS]\n{parsed.sections.get('experiments', '')}",
                f"[RESULTS]\n{parsed.sections.get('results', '')}",
                f"[CONCLUSION]\n{parsed.sections.get('conclusion', '')}",
            ]
        )
        text = text[:max_len]

        return f"""
请用{language_label}输出论文解读，保持如下 Markdown 结构：

# {parsed.title}
## Mode
{mode}
## Overview
（1段）
## Methods
- 要点1 [论文原文]
- 要点2 [论文原文]
## Key Conclusions
- 结论1 [论文原文]
- 结论2 [论文原文]
## Limitations & Open Questions
- 局限1 [论文原文]
- 风险提示 [外部补充]
## Evidence Policy
- 来自原文事实都标记 [论文原文]
- 你补充的外部常识标记 [外部补充]

要求：
1) 禁止输出 JSON。
2) 每条 bullet 必须带一个标签：[论文原文] 或 [外部补充]。
3) 深度模式尽量详细，标准模式简洁。

论文内容如下：
{text}
""".strip()
