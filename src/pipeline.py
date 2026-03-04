from __future__ import annotations

from dataclasses import asdict, dataclass

from .analyzer import Analyzer
from .citation_auditor import CitationAuditor
from .input_adapter import InputAdapter
from .llm_client import LLMClient
from .obsidian_sink import ObsidianSink
from .parser import PaperParser


@dataclass
class PipelineResult:
    title: str
    source: str
    source_type: str
    markdown: str
    audit: dict
    note_path: str | None
    model_used: str
    generation_mode: str


class PaperAssistantPipeline:
    def __init__(self) -> None:
        self.input_adapter = InputAdapter()
        self.parser = PaperParser()
        self.analyzer = Analyzer()
        self.auditor = CitationAuditor()
        self.sink = ObsidianSink()

    def run(
        self,
        mode: str = "deep",
        url: str | None = None,
        pdf_bytes: bytes | None = None,
        pdf_name: str | None = None,
        save_to_obsidian: bool = False,
        output_language: str = "zh",
        use_llm: bool = False,
        llm_api_base: str | None = None,
        llm_api_key: str | None = None,
        llm_model: str | None = None,
    ) -> PipelineResult:
        payload = self.input_adapter.load(url=url, pdf_bytes=pdf_bytes, pdf_name=pdf_name)
        parsed = self.parser.parse(title=payload.title, raw_text=payload.raw_text)

        llm_client = None
        generation_mode = "rule-based"
        model_used = "deterministic-template"

        if use_llm:
            llm_client = LLMClient.from_params(api_base=llm_api_base, api_key=llm_api_key, model=llm_model)
            generation_mode = "llm"
            model_used = llm_client.config.model

        analysis = self.analyzer.analyze(
            parsed=parsed,
            mode=mode,
            target_language=output_language,
            llm_client=llm_client,
        )
        audit = self.auditor.audit(analysis.markdown)

        note_path = None
        if save_to_obsidian:
            note_path = self.sink.save(payload.title, analysis.markdown, source=payload.source, mode=mode).path

        return PipelineResult(
            title=payload.title,
            source=payload.source,
            source_type=payload.source_type,
            markdown=analysis.markdown,
            audit={
                "total_claims": audit.total_claims,
                "compliant_claims": audit.compliant_claims,
                "pass_rate": round(audit.pass_rate, 4),
                "missing_tags": audit.missing_tags,
            },
            note_path=note_path,
            model_used=model_used,
            generation_mode=generation_mode,
        )
