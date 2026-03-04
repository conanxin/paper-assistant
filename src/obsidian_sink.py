from __future__ import annotations

import datetime as dt
import os
import re
from dataclasses import dataclass


@dataclass
class SaveResult:
    path: str
    appended: bool


class ObsidianSink:
    def __init__(self, target_dir: str = "/mnt/d/obsidian_nov/nov/Inbox/研究摘录") -> None:
        self.target_dir = target_dir

    def save(self, title: str, markdown: str, source: str = "", mode: str = "deep") -> SaveResult:
        os.makedirs(self.target_dir, exist_ok=True)
        date = dt.date.today().isoformat()
        safe_title = self._sanitize(title)
        filename = f"论文精读-{safe_title}-{date}.md"
        path = os.path.join(self.target_dir, filename)
        appended = os.path.exists(path)

        content = self._build_note(title=title, source=source, mode=mode, body=markdown)

        with open(path, "a", encoding="utf-8") as f:
            if appended:
                f.write("\n\n---\n\n")
            f.write(content)

        return SaveResult(path=path, appended=appended)

    @staticmethod
    def _build_note(title: str, source: str, mode: str, body: str) -> str:
        now = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        meta = [
            f"# 论文精读｜{title}",
            "",
            "## 元信息",
            f"- 生成时间：{now}",
            f"- 模式：{mode}",
            f"- 来源：{source or 'N/A'}",
            "- 引用规范：关键结论/关键数据均需来源标签（[论文原文] 或 [外部补充]）",
            "",
            "## 深度解读",
            body.strip(),
            "",
        ]
        return "\n".join(meta)

    @staticmethod
    def _sanitize(title: str) -> str:
        title = title.strip() or "paper-note"
        title = re.sub(r"\s+", "-", title)
        title = re.sub(r"[^\w\-\u4e00-\u9fff]", "", title)
        return title[:80] or "paper-note"
