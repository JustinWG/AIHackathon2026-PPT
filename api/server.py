"""
FastAPI server bridging the React frontend to the Python content pipeline.

Endpoints:
  POST /api/intake    — validate intake state, return next question or ready
  POST /api/generate  — run full pipeline: LLM generate → build pptx + docs
  GET  /api/download/{filename} — serve generated files from output/
"""
import json
import sys
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Make project root importable
sys.path.insert(0, str(Path(__file__).parent.parent))

from content.intake import assess_intake
from content.generate import generate_spec, GenerateError
from engine.build_pptx import build_pptx, AssemblyError
from engine.build_docs import build_bites

MASTER_PATH = Path("master/maverx_master.pptx")
OUTPUT_DIR = Path("output")

app = FastAPI(title="Maverx Training Builder API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Models ──────────────────────────────────────────────────────

class IntakeRequest(BaseModel):
    state: dict


class GenerateRequest(BaseModel):
    meta: dict


# ── Endpoints ───────────────────────────────────────────────────

@app.post("/api/intake")
def intake(req: IntakeRequest):
    """Pass current intake state, get back next question or ready signal."""
    return assess_intake(req.state)


@app.post("/api/generate")
def generate(req: GenerateRequest):
    """Run the full pipeline: generate spec → build pptx → build docs."""
    meta = req.meta
    topic_slug = meta.get("topic", "training")[:30].replace(" ", "_").lower()
    topic_slug = "".join(c for c in topic_slug if c.isalnum() or c == "_")

    out_pptx = str(OUTPUT_DIR / f"{topic_slug}.pptx")
    out_dir = str(OUTPUT_DIR / topic_slug)

    try:
        spec = generate_spec(meta)
    except GenerateError as e:
        raise HTTPException(status_code=422, detail=f"Content generation failed: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected generation error: {e}")

    if not MASTER_PATH.exists():
        raise HTTPException(
            status_code=500,
            detail=f"Master template not found at {MASTER_PATH}",
        )

    try:
        pptx_path = build_pptx(spec, str(MASTER_PATH), out_pptx)
    except AssemblyError as e:
        raise HTTPException(status_code=500, detail=f"PPTX assembly failed: {e}")

    try:
        pre_path, post_path = build_bites(spec, out_dir)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Doc generation failed: {e}")

    return {
        "status": "done",
        "files": {
            "pptx": Path(pptx_path).name,
            "prebite": f"{topic_slug}/{Path(pre_path).name}",
            "postbite": f"{topic_slug}/{Path(post_path).name}",
        },
        "spec": spec,
    }


@app.get("/api/download/{path:path}")
def download(path: str):
    """Serve a generated file from output/."""
    file_path = OUTPUT_DIR / path
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    # Prevent path traversal
    if not file_path.resolve().is_relative_to(OUTPUT_DIR.resolve()):
        raise HTTPException(status_code=403, detail="Access denied")
    return FileResponse(file_path, filename=file_path.name)


# ── Serve frontend as static files ──────────────────────────────

frontend_dir = Path(__file__).parent.parent / "frontend" / "maverx"
if frontend_dir.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")
