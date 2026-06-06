"""
C1 — Streamlit app (Person C).

Flow:
  1. Chat loop → assess_intake(state) until status == "ready"
  2. [Generate Training] button
  3. generate_spec(meta) → build_pptx() + build_bites()
  4. Download buttons for .pptx, prebite.docx, postbite.docx
"""
import json
import sys
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, str(Path(__file__).parent.parent))

from content.intake import assess_intake
from content.generate import generate_spec, GenerateError
from engine.build_pptx import build_pptx, AssemblyError
from engine.build_docs import build_bites

MASTER_PATH = "master/maverx_master.pptx"
OUTPUT_DIR  = "output"

# ---------------------------------------------------------------------------
# Stubs — remove once A's engine is ready (expected ~hour 3)
# ---------------------------------------------------------------------------

def _stub_generate_spec(meta: dict) -> dict:
    return json.loads(Path("schema/sample_spec.json").read_text())

def _stub_build_pptx(spec, master_path, out_path):
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    Path(out_path).write_bytes(b"STUB_PPTX")
    return out_path

def _stub_build_bites(spec, out_dir):
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    pre  = str(Path(out_dir) / "prebite.docx")
    post = str(Path(out_dir) / "postbite.docx")
    Path(pre).write_bytes(b"STUB_PREBITE")
    Path(post).write_bytes(b"STUB_POSTBITE")
    return pre, post

USE_STUBS = not Path(MASTER_PATH).exists()

# ---------------------------------------------------------------------------
# Page setup
# ---------------------------------------------------------------------------

st.set_page_config(page_title="Maverx Training Builder", page_icon="🎓", layout="centered")
st.title("🎓 Maverx AI Training Builder")
st.caption("From a one-sentence idea to a complete, editable PowerPoint deck.")

if not Path(MASTER_PATH).exists():
    st.warning(
        f"⚠️ Master template not found at `{MASTER_PATH}`. "
        "Drop `maverx_master.pptx` in the `master/` folder. Running in stub mode."
    )

# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------

if "intake_state" not in st.session_state:
    st.session_state.intake_state = {}
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "intake_complete" not in st.session_state:
    st.session_state.intake_complete = False
if "meta" not in st.session_state:
    st.session_state.meta = {}

# ---------------------------------------------------------------------------
# Chat history display
# ---------------------------------------------------------------------------

for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.write(msg["text"])

# ---------------------------------------------------------------------------
# Intake chat loop
# ---------------------------------------------------------------------------

if not st.session_state.intake_complete:
    if not st.session_state.chat_history:
        result = assess_intake(st.session_state.intake_state)
        opening = "Welcome! I'll ask you a few questions before generating your training.\n\n" + result["text"]
        st.session_state.chat_history.append({"role": "assistant", "text": opening})
        st.session_state["_last_field"] = result.get("field")
        st.rerun()

    user_input = st.chat_input("Your answer...")
    if user_input:
        st.session_state.chat_history.append({"role": "user", "text": user_input})
        field = st.session_state.get("_last_field")
        if field:
            st.session_state.intake_state[field] = user_input

        result = assess_intake(st.session_state.intake_state)

        if result["status"] == "ready":
            st.session_state.intake_complete = True
            st.session_state.meta = result["meta"]
            st.session_state.chat_history.append({
                "role": "assistant",
                "text": "✅ All set! Here's what I have:\n\n"
                        + "\n".join(f"**{k.capitalize()}:** {v}" for k, v in result["meta"].items())
                        + "\n\nClick **Generate Training** when ready.",
            })
            st.session_state["_last_field"] = None
        else:
            st.session_state.chat_history.append({"role": "assistant", "text": result["text"]})
            st.session_state["_last_field"] = result.get("field")

        st.rerun()

# ---------------------------------------------------------------------------
# Generation
# ---------------------------------------------------------------------------

else:
    meta = st.session_state.meta
    st.success("Intake complete. Ready to generate.")
    for k, v in meta.items():
        st.write(f"**{k.capitalize()}:** {v}")

    if st.button("🚀 Generate Training", type="primary"):
        topic_slug = meta["topic"][:30].replace(" ", "_").lower()
        out_pptx = str(Path(OUTPUT_DIR) / f"{topic_slug}.pptx")
        out_dir  = str(Path(OUTPUT_DIR) / topic_slug)

        with st.spinner("Generating training content…"):
            try:
                _gen   = _stub_generate_spec if USE_STUBS else generate_spec
                _build = _stub_build_pptx    if USE_STUBS else build_pptx
                _docs  = _stub_build_bites   if USE_STUBS else build_bites

                spec = _gen(meta)
                pptx_path = _build(spec, MASTER_PATH, out_pptx)
                pre_path, post_path = _docs(spec, out_dir)
                st.success("Done! Download your files below.")

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.download_button(
                        "📥 Download .pptx",
                        data=Path(pptx_path).read_bytes(),
                        file_name=Path(pptx_path).name,
                        mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                    )
                with col2:
                    st.download_button(
                        "📄 Pre-bite (.docx)",
                        data=Path(pre_path).read_bytes(),
                        file_name="prebite.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    )
                with col3:
                    st.download_button(
                        "📄 Post-bite (.docx)",
                        data=Path(post_path).read_bytes(),
                        file_name="postbite.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    )

            except GenerateError as e:
                st.error(f"Generation failed: {e}")
            except AssemblyError as e:
                st.error(f"Assembly failed: {e}")
            except Exception as e:
                st.error(f"Unexpected error: {e}")

    if st.button("↩ Start over"):
        for key in ["intake_state", "chat_history", "intake_complete", "meta", "_last_field"]:
            st.session_state.pop(key, None)
        st.rerun()
