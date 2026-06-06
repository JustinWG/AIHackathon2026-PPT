"""
FastAPI backend for the Maverx Training Builder (React UI integration).

Scope = Person B's content pipeline only. PPTX/.docx file rendering is Person A's
engine and is intentionally NOT done here yet — we return the structured spec
(including prebite/postbite markdown) for the UI to display. When A's engine is
ready, add a render step that calls engine.build_pptx / build_docs.

Endpoints:
  POST /api/assess    -> intake gate: next question / ready (content/intake.py)
  POST /api/generate  -> generate_spec(meta) -> full training spec JSON
  GET  /              -> serves the React frontend (frontend/maverx)

generate_spec uses OPENROUTER_API_KEY.
"""
import sys
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from content.intake import assess_intake
from content.generate import generate_spec, GenerateError

FRONTEND_DIR = ROOT / "frontend" / "maverx"

app = FastAPI(title="Maverx Training Builder")
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
)


class IntakeState(BaseModel):
    state: dict = {}


class Meta(BaseModel):
    topic: str
    audience: str
    level: str
    duration: str
    objective: str


@app.post("/api/assess")
def assess(payload: IntakeState):
    """Drive the intake one answer at a time (mirrors content/intake.py)."""
    return assess_intake(payload.state)


@app.post("/api/generate")
def generate(meta: Meta):
    """meta -> full training spec JSON (meta, slides, prebite, postbite).

    No file rendering here — Person A's engine turns this spec into .pptx/.docx.
    """
    try:
        spec = generate_spec(meta.model_dump())
    except GenerateError as e:
        raise HTTPException(status_code=502, detail=f"Content generation failed: {e}")
    return spec


@app.get("/api/health")
def health():
    return {"ok": True}


# Serve the React frontend at the root (index.html resolves automatically)
if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
