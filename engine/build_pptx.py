"""
A3 — PPTX assembler (Person A).

Public API (do not change signatures without team sync):
    build_pptx(spec, master_path, out_path) -> str
"""
import json
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt


NOTES_TEMPLATE = """\
Aim: {aim}

Time: {time}

Instructions: {instructions}

Reflective question: {reflective_q}

Debrief: {debrief}"""


class AssemblyError(Exception):
    pass


def _load_layout_map(layouts_path: str = "schema/layouts.json") -> dict:
    data = json.loads(Path(layouts_path).read_text())
    block_map = data.get("block_to_layout", {})
    if not block_map or any("FILL_ME" in v for v in block_map.values()):
        raise AssemblyError(
            "schema/layouts.json block_to_layout is not filled in yet. "
            "Run engine/layouts_report.py first."
        )
    return block_map


def _get_layout(prs: Presentation, layout_name: str):
    for layout in prs.slide_layouts:
        if layout.name == layout_name:
            return layout
    raise AssemblyError(
        f"Layout '{layout_name}' not found in master. "
        f"Available: {[l.name for l in prs.slide_layouts]}"
    )


def _fill_placeholders(slide, title: str, bullets: list[str]) -> None:
    for ph in slide.placeholders:
        idx = ph.placeholder_format.idx
        if idx == 0:
            ph.text = title
        elif idx == 1 and bullets:
            tf = ph.text_frame
            tf.clear()
            for i, bullet in enumerate(bullets):
                if i == 0:
                    tf.paragraphs[0].text = bullet
                else:
                    p = tf.add_paragraph()
                    p.text = bullet
                    p.level = 0


def _add_table(slide, table_data: dict) -> None:
    headers = table_data["headers"]
    rows = table_data["rows"]
    cols = len(headers)
    total_rows = len(rows) + 1

    left   = Inches(0.5)
    top    = Inches(3.0)
    width  = Inches(9.0)
    height = Inches(0.4 * total_rows)

    table_shape = slide.shapes.add_table(total_rows, cols, left, top, width, height)
    tbl = table_shape.table

    for col_idx, header in enumerate(headers):
        tbl.cell(0, col_idx).text = header

    for row_idx, row in enumerate(rows):
        for col_idx, cell_val in enumerate(row):
            tbl.cell(row_idx + 1, col_idx).text = str(cell_val)


def _write_notes(slide, notes: dict) -> None:
    text = NOTES_TEMPLATE.format(**notes)
    notes_slide = slide.notes_slide
    tf = notes_slide.notes_text_frame
    tf.text = text


def build_pptx(spec: dict, master_path: str, out_path: str) -> str:
    """
    Fills the master's layouts from spec, writes speaker notes, returns out_path.
    Raises AssemblyError on bad layout name or malformed spec.
    """
    block_map = _load_layout_map()
    prs = Presentation(master_path)

    # Remove any placeholder slides that come with the template
    # (keep slide_layouts intact — only remove slides from slide list)
    xml_slides = prs.slides._sldIdLst
    for _ in range(len(prs.slides)):
        xml_slides.remove(xml_slides[0])

    for slide_spec in spec["slides"]:
        block = slide_spec["block"]
        layout_name = slide_spec.get("layout") or block_map.get(block)
        if not layout_name or layout_name == "FILL_AFTER_LAYOUT_REPORT":
            layout_name = block_map.get(block)
        if not layout_name:
            raise AssemblyError(f"No layout for block '{block}'")

        layout = _get_layout(prs, layout_name)
        slide = prs.slides.add_slide(layout)

        _fill_placeholders(slide, slide_spec["title"], slide_spec.get("bullets") or [])

        if slide_spec.get("table"):
            _add_table(slide, slide_spec["table"])

        _write_notes(slide, slide_spec["notes"])

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    prs.save(out_path)
    return out_path


if __name__ == "__main__":
    import sys
    spec_path   = sys.argv[1] if len(sys.argv) > 1 else "schema/sample_spec.json"
    master_path = sys.argv[2] if len(sys.argv) > 2 else "master/maverx_master.pptx"
    out_path    = sys.argv[3] if len(sys.argv) > 3 else "output/test.pptx"

    spec = json.loads(Path(spec_path).read_text())
    result = build_pptx(spec, master_path, out_path)
    print(f"Written: {result}")
