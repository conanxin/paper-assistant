from __future__ import annotations

import traceback

import streamlit as st

from src.pipeline import PaperAssistantPipeline

st.set_page_config(page_title="Paper Assistant", layout="wide")
st.title("Paper Reading Assistant (Local)")

pipeline = PaperAssistantPipeline()

if "last_result" not in st.session_state:
    st.session_state.last_result = None

with st.sidebar:
    st.header("Input")
    url = st.text_input("Paper URL (arXiv or any page)", value="https://arxiv.org/abs/2601.03220v1")
    uploaded = st.file_uploader("Optional PDF upload", type=["pdf"])
    mode = st.selectbox("Mode", options=["deep", "standard"], index=0)

    st.header("Generation")
    output_language = st.selectbox("Output Language", options=["zh", "en"], index=0)
    use_llm = st.checkbox("Use LLM (OpenAI-compatible)", value=False)
    llm_model = st.text_input("Model", value="gpt-4o-mini", disabled=not use_llm)
    llm_api_base = st.text_input("API Base", value="https://api.openai.com/v1", disabled=not use_llm)
    llm_api_key = st.text_input("API Key", type="password", value="", disabled=not use_llm)

    run_clicked = st.button("Run", type="primary")

if run_clicked:
    status = st.status("Running pipeline...", expanded=True)
    try:
        status.write("Loading input...")
        pdf_bytes = uploaded.getvalue() if uploaded else None
        pdf_name = uploaded.name if uploaded else None

        status.write("Parsing and analyzing...")
        try:
            result = pipeline.run(
                mode=mode,
                url=url if not pdf_bytes else None,
                pdf_bytes=pdf_bytes,
                pdf_name=pdf_name,
                save_to_obsidian=False,
                output_language=output_language,
                use_llm=use_llm,
                llm_model=llm_model,
                llm_api_base=llm_api_base,
                llm_api_key=llm_api_key or None,
            )
        except Exception as llm_err:
            if use_llm:
                status.write(f"LLM failed ({llm_err}), fallback to rule-based...")
                result = pipeline.run(
                    mode=mode,
                    url=url if not pdf_bytes else None,
                    pdf_bytes=pdf_bytes,
                    pdf_name=pdf_name,
                    save_to_obsidian=False,
                    output_language=output_language,
                    use_llm=False,
                )
                st.warning(f"LLM 调用失败，已回退到规则模式：{llm_err}")
            else:
                raise

        status.write("Running citation audit...")
        st.session_state.last_result = result
        status.update(label="Completed", state="complete")
    except Exception as e:
        status.update(label=f"Failed: {e}", state="error")
        st.exception(traceback.format_exc())

result = st.session_state.last_result

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Output Markdown Preview")
    if result:
        st.caption(f"generation_mode={result.generation_mode} | model={result.model_used}")
        st.markdown(result.markdown)
    else:
        st.info("Run the pipeline to see output.")

with col2:
    st.subheader("Citation Audit")
    if result:
        st.json(result.audit)
        if result.audit.get("missing_tags"):
            st.warning("Some claims are missing source tags.")
        else:
            st.success("All extracted claim lines include source tags.")

        audit_ok = (not result.audit.get("missing_tags")) and result.audit.get("pass_rate", 0) >= 1.0
        if not audit_ok:
            st.error("引用审计未通过：存在未标注来源的要点，已禁止保存到 Obsidian。")

        if st.button("Save to Obsidian", disabled=not audit_ok):
            save_result = pipeline.sink.save(
                result.title,
                result.markdown,
                source=result.source,
                mode=mode,
            )
            st.success(f"Saved: {save_result.path}")
    else:
        st.info("Audit appears after running.")
