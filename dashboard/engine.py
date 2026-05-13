"""Engine: Wraps test_lokal.py-Funktionen + Analyzer-Singleton."""

import sys
import asyncio
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

# test_lokal.py importierbar machen
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from test_lokal import (
    create_analyzer,
    extract_text_from_pdf,
    detect_pii,
    generate_html,
    generate_html_extraction,
)

from . import store
from .models import TestRun, DocumentType

# Erlaubte Verzeichnisse fuer PDF-Zugriff (Sicherheit)
PROJECT_ROOT = Path(__file__).parent.parent
CONFIG_FILE = Path(__file__).parent / "data" / "config.json"

DEFAULT_THRESHOLD = 0.5


def get_threshold() -> float:
    """Liest Score-Threshold aus config.json (Fallback: DEFAULT_THRESHOLD)."""
    if CONFIG_FILE.exists():
        try:
            import json
            data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
            return float(data.get("score_threshold", DEFAULT_THRESHOLD))
        except Exception:
            pass
    return DEFAULT_THRESHOLD


def set_threshold(value: float):
    """Schreibt Score-Threshold in config.json."""
    import json
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(
        json.dumps({"score_threshold": round(value, 2)}, indent=2),
        encoding="utf-8"
    )
ALLOWED_PDF_DIRS = [
    PROJECT_ROOT / "test-files",
    PROJECT_ROOT / "test-files" / "real-use-cases",
]

# Analyzer-Singleton
_analyzer = None


def get_analyzer():
    global _analyzer
    if _analyzer is None:
        _analyzer = create_analyzer()
    return _analyzer


def list_test_pdfs() -> list[dict]:
    """Findet alle PDFs in erlaubten Verzeichnissen."""
    pdfs = []
    for d in ALLOWED_PDF_DIRS:
        if not d.exists():
            continue
        for f in sorted(d.glob("*.pdf")):
            pdfs.append({
                "filename": f.name,
                "path": str(f.resolve()),
                "folder": d.name,
                "size_kb": f.stat().st_size // 1024,
            })
    return pdfs


def resolve_pdf_path(filename: str) -> Path | None:
    """Loest Dateiname zu Pfad auf — nur aus erlaubten Verzeichnissen."""
    for d in ALLOWED_PDF_DIRS:
        candidate = d / filename
        if candidate.exists() and candidate.resolve().parent in [dd.resolve() for dd in ALLOWED_PDF_DIRS]:
            return candidate
    return None


def _process_pdf(pdf_path: str, run_id: str) -> dict:
    """Synchrone PDF-Verarbeitung (laeuft in Thread)."""
    start = time.time()
    analyzer = get_analyzer()

    text, pages_info = extract_text_from_pdf(pdf_path)
    entities = detect_pii(text, analyzer, score_threshold=get_threshold())

    pdf_name = Path(pdf_path).name
    extraction_html = generate_html_extraction(text, pages_info, pdf_name)
    redaction_html = generate_html(text, entities, pages_info, pdf_name)

    # HTML + Rohdaten speichern (Rohdaten fuer Auto-Eval)
    store.save_result_html(run_id, extraction_html, redaction_html)
    store.save_raw_data(run_id, text, [dict(e) for e in entities])

    # Entity-Typ-Zaehlung
    type_counts = {}
    for ent in entities:
        type_counts[ent["typ"]] = type_counts.get(ent["typ"], 0) + 1

    duration = time.time() - start

    return {
        "page_count": len(pages_info),
        "ocr_page_count": sum(1 for p in pages_info if p["ocr"]),
        "entity_count": len(entities),
        "entity_type_counts": type_counts,
        "duration_seconds": round(duration, 1),
    }


async def run_test(pdf_path: str, doc_type: DocumentType,
                   iteration_id: Optional[str] = None) -> str:
    """Startet Testlauf. Gibt run_id zurueck."""
    run_id = uuid.uuid4().hex[:12]
    pdf_name = Path(pdf_path).name

    run = TestRun(
        id=run_id,
        pdf_filename=pdf_name,
        doc_type=doc_type,
        timestamp=datetime.now(),
        status="running",
        iteration_id=iteration_id,
    )
    store.save_run(run)

    # PDF-Verarbeitung im Thread-Pool (blockiert Event-Loop nicht)
    async def _background():
        try:
            result = await asyncio.to_thread(_process_pdf, pdf_path, run_id)
            store.update_run(run_id, status="done", **result)
        except Exception as e:
            store.update_run(run_id, status="error", error_message=str(e))

    asyncio.create_task(_background())
    return run_id
