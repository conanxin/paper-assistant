from __future__ import annotations

import io
import os
import re
import subprocess
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Optional


@dataclass
class InputPayload:
    source_type: str
    source: str
    title: str
    raw_text: str
    pdf_path: Optional[str]


class InputAdapter:
    """Loads paper content from URL or uploaded PDF using local tools only."""

    USER_AGENT = "paper-assistant/0.1"

    def load(self, url: str | None = None, pdf_bytes: bytes | None = None, pdf_name: str | None = None) -> InputPayload:
        if pdf_bytes:
            return self._load_pdf_upload(pdf_bytes=pdf_bytes, pdf_name=pdf_name or "uploaded.pdf")
        if not url:
            raise ValueError("Either URL or PDF upload is required.")
        return self._load_url(url)

    def _load_pdf_upload(self, pdf_bytes: bytes, pdf_name: str) -> InputPayload:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as f:
            f.write(pdf_bytes)
            pdf_path = f.name
        text = self._pdf_to_text(pdf_path)
        title = os.path.splitext(os.path.basename(pdf_name))[0]
        return InputPayload(
            source_type="pdf_upload",
            source=pdf_name,
            title=title,
            raw_text=text,
            pdf_path=pdf_path,
        )

    def _load_url(self, url: str) -> InputPayload:
        try:
            html = self._fetch_text(url)
            title = self._extract_title(html) or self._derive_title_from_url(url)
            raw_text = self._strip_html(html)
        except Exception as e:
            title = self._derive_title_from_url(url)
            raw_text = (
                f"Failed to fetch URL content directly due to: {type(e).__name__}. "
                "Only URL metadata is available."
            )

        pdf_path = None
        if "arxiv.org/abs/" in url:
            pdf_url = self._abs_to_pdf(url)
            try:
                pdf_bytes = self._fetch_bytes(pdf_url)
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as f:
                    f.write(pdf_bytes)
                    pdf_path = f.name
                pdf_text = self._pdf_to_text(pdf_path)
                if pdf_text.strip():
                    raw_text = f"{raw_text}\n\n[pdf_extracted]\n{pdf_text}"
            except Exception:
                pass

        return InputPayload(
            source_type="url",
            source=url,
            title=title,
            raw_text=raw_text,
            pdf_path=pdf_path,
        )

    def _fetch_text(self, url: str) -> str:
        req = urllib.request.Request(url, headers={"User-Agent": self.USER_AGENT})
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.read().decode("utf-8", errors="ignore")

    def _fetch_bytes(self, url: str) -> bytes:
        req = urllib.request.Request(url, headers={"User-Agent": self.USER_AGENT})
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.read()

    @staticmethod
    def _extract_title(html: str) -> Optional[str]:
        m = re.search(r"<title>(.*?)</title>", html, flags=re.IGNORECASE | re.DOTALL)
        if not m:
            return None
        return re.sub(r"\s+", " ", m.group(1)).strip()

    @staticmethod
    def _derive_title_from_url(url: str) -> str:
        parsed = urllib.parse.urlparse(url)
        tail = parsed.path.rstrip("/").split("/")[-1] or "paper"
        return tail

    @staticmethod
    def _strip_html(html: str) -> str:
        text = re.sub(r"<script.*?</script>", " ", html, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r"<style.*?</style>", " ", text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    @staticmethod
    def _abs_to_pdf(url: str) -> str:
        pdf_url = url.replace("/abs/", "/pdf/")
        if not pdf_url.endswith(".pdf"):
            pdf_url = f"{pdf_url}.pdf"
        return pdf_url

    @staticmethod
    def _pdf_to_text(pdf_path: str) -> str:
        if not shutil_which("pdftotext"):
            return ""

        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as out:
            out_path = out.name

        try:
            subprocess.run(
                ["pdftotext", "-layout", pdf_path, out_path],
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            with open(out_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        finally:
            if os.path.exists(out_path):
                os.unlink(out_path)


def shutil_which(cmd: str) -> Optional[str]:
    for path in os.environ.get("PATH", "").split(os.pathsep):
        candidate = os.path.join(path, cmd)
        if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
            return candidate
    return None
