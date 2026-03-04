from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class ParsedPaper:
    title: str
    sections: dict[str, str]


class PaperParser:
    """Heuristically segment paper text into common academic sections."""

    SECTION_ORDER = [
        "abstract",
        "introduction",
        "method",
        "experiments",
        "results",
        "discussion",
        "conclusion",
        "references",
    ]

    SECTION_PATTERNS = {
        "abstract": [r"\babstract\b"],
        "introduction": [r"\bintroduction\b"],
        "method": [r"\bmethod(?:ology)?\b", r"\bapproach\b"],
        "experiments": [r"\bexperiments?\b", r"\bsetup\b"],
        "results": [r"\bresults?\b", r"\bevaluation\b"],
        "discussion": [r"\bdiscussion\b", r"\banalysis\b"],
        "conclusion": [r"\bconclusion\b", r"\bfuture work\b"],
        "references": [r"\breferences\b", r"\bbibliography\b"],
    }

    def parse(self, title: str, raw_text: str) -> ParsedPaper:
        chunks = self._split_candidates(raw_text)
        sections: dict[str, str] = {k: "" for k in self.SECTION_ORDER}

        current = "introduction"
        for chunk in chunks:
            mapped = self._match_section(chunk)
            if mapped:
                current = mapped
                continue
            sections[current] = (sections[current] + " " + chunk).strip()

        if not sections["abstract"]:
            sections["abstract"] = self._first_n_sentences(raw_text, 4)

        return ParsedPaper(title=title, sections=sections)

    @staticmethod
    def _split_candidates(raw_text: str) -> list[str]:
        text = re.sub(r"\s+", " ", raw_text)
        split = re.split(r"(?:(?:\n\s*){2,}|(?<=\.)\s{2,})", text)
        return [s.strip() for s in split if s.strip()]

    def _match_section(self, chunk: str) -> str | None:
        lowered = chunk.lower().strip()
        for name, pats in self.SECTION_PATTERNS.items():
            for pat in pats:
                if re.fullmatch(r"\d*\.?\s*" + pat + r"\s*", lowered):
                    return name
        return None

    @staticmethod
    def _first_n_sentences(text: str, n: int) -> str:
        sents = re.split(r"(?<=[.!?])\s+", text)
        return " ".join(sents[:n])
