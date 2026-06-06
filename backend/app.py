"""
FastAPI backend for the Maverx Training Builder (React UI integration).

Endpoints:
  POST /api/assess        -> intake gate: next question / ready (content/intake.py)
  POST /api/generate      -> generate_spec(meta); if render=true also builds the
                             .pptx + pre/post-bite .docx via engine/ and returns file names
  GET  /api/download/{n}  -> serves a generated file from output/
  GET  /api/health
  GET  /                  -> serves the React frontend (frontend/maverx)

generate_spec uses OPENROUTER_API_KEY. The .pptx/.docx rendering uses python-pptx /
python-docx (engine/, Person A) and needs no extra key.
"""
import sys
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from content.intake import assess_intake
from content.generate import generate_spec, GenerateError
from engine.build_pptx import build_pptx, AssemblyError
from engine.build_docs import build_bites

MASTER_PATH = str(ROOT / "master" / "maverx_master.pptx")
OUTPUT_DIR = ROOT / "output"
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
    render: bool = False  # when true, also build the .pptx + .docx files


def _slug(text: str) -> str:
    return "".join(c if c.isalnum() else "_" for c in text.lower()).strip("_")[:40] or "training"


@app.post("/api/assess")
def assess(payload: IntakeState):
    """Drive the intake one answer at a time (mirrors content/intake.py)."""
    return assess_intake(payload.state)


@app.post("/api/generate")
def generate(meta: Meta):
    """meta -> full training spec JSON. If meta.render, also build .pptx + .docx."""
    data = meta.model_dump()
    render = data.pop("render", False)
    try:
        spec = generate_spec(data)
    except GenerateError as e:
        raise HTTPException(status_code=502, detail=f"Content generation failed: {e}")

    result = dict(spec)  # meta, slides, prebite, postbite

    if render:
        OUTPUT_DIR.mkdir(exist_ok=True)
        slug = _slug(meta.topic)
        try:
            pptx_path = build_pptx(spec, MASTER_PATH, str(OUTPUT_DIR / f"{slug}.pptx"))
            pre, post = build_bites(spec, str(OUTPUT_DIR))
        except AssemblyError as e:
            raise HTTPException(status_code=500, detail=f"Deck assembly failed: {e}")
        result["files"] = {
            "pptx": Path(pptx_path).name,
            "prebite": Path(pre).name,
            "postbite": Path(post).name,
        }

    return result


@app.get("/api/download/{name}")
def download(name: str):
    path = (OUTPUT_DIR / name).resolve()
    if OUTPUT_DIR.resolve() not in path.parents or not path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(str(path), filename=name)


@app.get("/api/health")
def health():
    return {"ok": True}


# Serve the React frontend at the root (index.html resolves automatically)
if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
