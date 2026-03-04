from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class AuditResult:
    total_claims: int
    compliant_claims: int
    missing_tags: list[str]

    @property
    def pass_rate(self) -> float:
        if self.total_claims == 0:
            return 1.0
        return self.compliant_claims / self.total_claims


class CitationAuditor:
    """Ensure each claim line contains evidence tag: [论文原文] or [外部补充]."""

    ALLOWED_TAGS = ("[论文原文]", "[外部补充]")

    def audit(self, markdown: str) -> AuditResult:
        claim_lines = self._extract_claim_lines(markdown)
        missing = [line for line in claim_lines if not any(tag in line for tag in self.ALLOWED_TAGS)]
        return AuditResult(
            total_claims=len(claim_lines),
            compliant_claims=len(claim_lines) - len(missing),
            missing_tags=missing,
        )

    @staticmethod
    def _extract_claim_lines(markdown: str) -> list[str]:
        lines = markdown.splitlines()
        in_relevant_block = False
        claims: list[str] = []
        for line in lines:
            if re.match(r"^##\s+", line):
                heading = line.strip().lower()
                in_relevant_block = heading in {
                    "## methods",
                    "## key conclusions",
                    "## limitations & open questions",
                    "## 方法要点",
                    "## 核心结论",
                    "## 局限与开放问题",
                }
                continue
            if in_relevant_block and line.startswith("- "):
                claims.append(line)
        return claims
