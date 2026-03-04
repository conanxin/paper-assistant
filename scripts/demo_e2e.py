from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from src.pipeline import PaperAssistantPipeline


def main() -> None:
    url = "https://arxiv.org/abs/2601.03220v1"
    out_dir = Path("/mnt/d/obsidian_nov/nov/paper-assistant/evidence")
    out_dir.mkdir(parents=True, exist_ok=True)

    pipeline = PaperAssistantPipeline()
    result = pipeline.run(mode="deep", url=url, save_to_obsidian=False)

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    md_path = out_dir / f"demo-{stamp}.md"
    audit_path = out_dir / f"demo-{stamp}.audit.json"

    md_path.write_text(result.markdown, encoding="utf-8")
    audit_path.write_text(
        json.dumps(
            {
                "title": result.title,
                "source": result.source,
                "source_type": result.source_type,
                "audit": result.audit,
                "markdown_path": str(md_path),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print("EVIDENCE_MARKDOWN_PATH=" + str(md_path))
    print("EVIDENCE_AUDIT_PATH=" + str(audit_path))


if __name__ == "__main__":
    main()
