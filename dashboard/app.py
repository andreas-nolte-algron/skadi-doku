"""FastAPI Test-Dashboard fuer Schwaerzungs-Tool."""

import asyncio
import json
from datetime import datetime
from pathlib import Path

from fastapi import BackgroundTasks, FastAPI, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from . import engine, store, evaluator, fp_auditor
from .models import (
    DocumentType,
    DOC_TYPE_LABELS,
    DEFAULT_CHECKLIST,
    Evaluation,
    ChecklistItem,
    Iteration,
)

PROJECT_ROOT = Path(__file__).parent.parent
MANIFEST_FILE = PROJECT_ROOT / "test-files" / "manifest.json"

# Batch-Status (in-memory, reset bei Server-Neustart)
_batch: dict = {"running": False, "total": 0, "done": 0, "current": "", "errors": []}


def _load_manifest() -> list[dict]:
    if not MANIFEST_FILE.exists():
        return []
    with open(MANIFEST_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

app = FastAPI(title="Skadi-Doku Test-Dashboard")

DASHBOARD_DIR = Path(__file__).parent
app.mount("/static", StaticFiles(directory=DASHBOARD_DIR / "static"), name="static")
templates = Jinja2Templates(directory=DASHBOARD_DIR / "templates")


@app.on_event("startup")
async def startup():
    """Lade Analyzer-Singleton beim Start (dauert ~5s)."""
    print("Lade Presidio Analyzer (spaCy de_core_news_lg)...")
    engine.get_analyzer()
    print("Analyzer bereit.")


# ── Uebersicht ──

@app.get("/", response_class=HTMLResponse)
async def overview(request: Request):
    runs = store.load_runs()
    evals = store.load_evaluations()
    auto_evals = store.load_all_auto_evaluations()

    eval_by_run = {e.run_id: e for e in evals}
    # Fuer Uebersicht: Auto-Eval als Fallback wenn keine manuelle Eval
    auto_eval_by_run = {}
    for ae in auto_evals:
        if ae.run_id not in auto_eval_by_run or ae.timestamp > auto_eval_by_run[ae.run_id].timestamp:
            auto_eval_by_run[ae.run_id] = ae

    type_stats = {}
    for dt in DocumentType:
        dt_runs = [r for r in runs if r.doc_type == dt and r.status == "done"]

        ok = maengel = unbrauchbar = unevaluated = 0
        for r in dt_runs:
            if r.id in eval_by_run:
                v = eval_by_run[r.id].overall_verdict
            elif r.id in auto_eval_by_run:
                v = auto_eval_by_run[r.id].overall_verdict
            else:
                unevaluated += 1
                continue
            if v == "ok":
                ok += 1
            elif v == "maengel":
                maengel += 1
            elif v == "unbrauchbar":
                unbrauchbar += 1

        type_stats[dt] = {
            "label": DOC_TYPE_LABELS[dt],
            "total_runs": len(dt_runs),
            "ok": ok,
            "maengel": maengel,
            "unbrauchbar": unbrauchbar,
            "unevaluated": unevaluated,
        }

    return templates.TemplateResponse(request, "overview.html", {
        "type_stats": type_stats,
        "total_runs": len(runs),
    })


# ── Test starten ──

@app.get("/test", response_class=HTMLResponse)
async def test_page(request: Request):
    pdfs = engine.list_test_pdfs()
    return templates.TemplateResponse(request, "test_run.html", {
        "pdfs": pdfs,
        "doc_types": [(dt.value, DOC_TYPE_LABELS[dt]) for dt in DocumentType],
    })


@app.post("/test/run")
async def start_test(
    pdf_filename: str = Form(...),
    doc_type: str = Form(...),
):
    pdf_path = engine.resolve_pdf_path(pdf_filename)
    if not pdf_path:
        return JSONResponse({"error": "PDF nicht gefunden"}, status_code=404)

    run_id = await engine.run_test(str(pdf_path), DocumentType(doc_type))
    return RedirectResponse(url=f"/result/{run_id}", status_code=303)


@app.get("/test/status/{run_id}")
async def test_status(run_id: str):
    run = store.get_run(run_id)
    if not run:
        return JSONResponse({"error": "Run nicht gefunden"}, status_code=404)
    return JSONResponse({
        "status": run.status,
        "entity_count": run.entity_count,
        "duration_seconds": run.duration_seconds,
        "error_message": run.error_message,
    })


# ── Ergebnis ansehen ──

@app.get("/result/{run_id}", response_class=HTMLResponse)
async def result_page(request: Request, run_id: str):
    run = store.get_run(run_id)
    if not run:
        return HTMLResponse("Run nicht gefunden", status_code=404)

    evaluation = store.get_evaluation(run_id)
    auto_evals = store.load_auto_evaluations(run_id)
    auto_evals.sort(key=lambda e: e.timestamp, reverse=True)
    latest_auto = auto_evals[0] if auto_evals else None

    return templates.TemplateResponse(request, "result.html", {
        "run": run,
        "evaluation": evaluation,
        "latest_auto": latest_auto,
        "auto_eval_count": len(auto_evals),
    })


@app.get("/result/{run_id}/extraction", response_class=HTMLResponse)
async def result_extraction(run_id: str):
    html = store.load_result_html(run_id, "extraction")
    if not html:
        return HTMLResponse("Extraktion nicht gefunden", status_code=404)
    return HTMLResponse(html)


@app.get("/result/{run_id}/redaction", response_class=HTMLResponse)
async def result_redaction(run_id: str):
    html = store.load_result_html(run_id, "redaction")
    if not html:
        return HTMLResponse("Schwaerzung nicht gefunden", status_code=404)
    return HTMLResponse(html)


# ── Manuelle Evaluation ──

@app.get("/evaluate/{run_id}", response_class=HTMLResponse)
async def evaluate_page(request: Request, run_id: str):
    run = store.get_run(run_id)
    if not run:
        return HTMLResponse("Run nicht gefunden", status_code=404)

    existing = store.get_evaluation(run_id)
    if existing:
        checklist = existing.checklist
        evaluation = existing
    else:
        checklist = [ChecklistItem(label=label) for label in DEFAULT_CHECKLIST]
        evaluation = None

    # Auto-Evals fuer Anzeige
    auto_evals = store.load_auto_evaluations(run_id)
    auto_evals.sort(key=lambda e: e.timestamp, reverse=True)

    return templates.TemplateResponse(request, "evaluate.html", {
        "run": run,
        "checklist": checklist,
        "evaluation": evaluation,
        "auto_evals": auto_evals,
    })


@app.post("/evaluate/{run_id}")
async def save_evaluation(request: Request, run_id: str):
    form = await request.form()

    checklist = []
    for i, label in enumerate(DEFAULT_CHECKLIST):
        checked = form.get(f"check_{i}") == "on"
        comment = form.get(f"comment_{i}", "")
        checklist.append(ChecklistItem(label=label, checked=checked, comment=comment))

    evaluation = Evaluation(
        run_id=run_id,
        timestamp=datetime.now(),
        checklist=checklist,
        false_negatives_noted=int(form.get("false_negatives", 0) or 0),
        false_positives_noted=int(form.get("false_positives", 0) or 0),
        overall_verdict=form.get("verdict", ""),
        notes=form.get("notes", ""),
    )
    store.save_evaluation(evaluation)

    return RedirectResponse(url=f"/result/{run_id}", status_code=303)


# ── Auto-Evaluate (LLM) ──

@app.get("/ollama/status")
async def ollama_status():
    result = await evaluator.check_ollama()
    return JSONResponse(result)


@app.post("/auto-evaluate/{run_id}")
async def auto_evaluate(run_id: str):
    run = store.get_run(run_id)
    if not run:
        return JSONResponse({"ok": False, "error": "Run nicht gefunden"}, status_code=404)
    if run.status != "done":
        return JSONResponse({"ok": False, "error": "Run nicht abgeschlossen"}, status_code=400)

    result = await evaluator.auto_evaluate(run_id)
    if result["ok"]:
        return JSONResponse({"ok": True, "redirect": f"/result/{run_id}"})
    else:
        return JSONResponse(result, status_code=500)


@app.get("/auto-evals/{run_id}")
async def get_auto_evals(run_id: str):
    """Alle Auto-Evaluations fuer einen Run (fuer Dropdown/Vergleich)."""
    auto_evals = store.load_auto_evaluations(run_id)
    auto_evals.sort(key=lambda e: e.timestamp, reverse=True)
    return JSONResponse([
        {
            "id": ae.id,
            "timestamp": ae.timestamp.isoformat(),
            "verdict": ae.overall_verdict,
            "fp": ae.false_positives_noted,
            "fn": ae.false_negatives_noted,
            "findings": ae.ai_findings,
        }
        for ae in auto_evals
    ])


# ── Historie ──

@app.get("/history", response_class=HTMLResponse)
async def history_page(request: Request, doc_type: str = ""):
    runs = store.load_runs()
    evals = store.load_evaluations()
    auto_evals = store.load_all_auto_evaluations()

    eval_by_run = {e.run_id: e for e in evals}
    auto_eval_by_run = {}
    for ae in auto_evals:
        if ae.run_id not in auto_eval_by_run or ae.timestamp > auto_eval_by_run[ae.run_id].timestamp:
            auto_eval_by_run[ae.run_id] = ae

    if doc_type:
        runs = [r for r in runs if r.doc_type.value == doc_type]

    runs.sort(key=lambda r: r.timestamp, reverse=True)

    run_data = []
    for r in runs:
        run_data.append({
            "run": r,
            "evaluation": eval_by_run.get(r.id),
            "auto_eval": auto_eval_by_run.get(r.id),
            "doc_type_label": DOC_TYPE_LABELS.get(r.doc_type, r.doc_type),
        })

    return templates.TemplateResponse(request, "history.html", {
        "run_data": run_data,
        "doc_types": [(dt.value, DOC_TYPE_LABELS[dt]) for dt in DocumentType],
        "active_filter": doc_type,
    })


# ── Batch-Test ──

@app.get("/batch", response_class=HTMLResponse)
async def batch_page(request: Request):
    manifest = _load_manifest()
    iterations = store.load_iterations()
    iterations.sort(key=lambda i: i.started_at, reverse=True)
    return templates.TemplateResponse(request, "batch.html", {
        "manifest": manifest,
        "doc_types": [(dt.value, DOC_TYPE_LABELS[dt]) for dt in DocumentType],
        "active_nav": "batch",
        "manifest_exists": MANIFEST_FILE.exists(),
        "iterations": iterations,
    })


@app.post("/batch/run")
async def start_batch(background_tasks: BackgroundTasks, request: Request):
    global _batch
    if _batch["running"]:
        return JSONResponse({"ok": False, "error": "Batch laeuft bereits"})
    manifest = _load_manifest()
    if not manifest:
        return JSONResponse({"ok": False, "error": "Manifest nicht gefunden oder leer"})

    # Konfig-Notiz aus Form-Body (optional)
    try:
        form = await request.form()
        config_note = str(form.get("config_note", "")).strip()
    except Exception:
        config_note = ""

    # Neue Iteration anlegen
    iter_id = __import__("uuid").uuid4().hex[:12]
    iteration = Iteration(
        id=iter_id,
        started_at=datetime.now(),
        config_note=config_note,
    )
    store.save_iteration(iteration)

    _batch = {"running": True, "total": len(manifest), "done": 0, "current": "", "errors": [],
              "iter_id": iter_id}
    background_tasks.add_task(_run_batch_task, manifest, iter_id)
    return JSONResponse({"ok": True, "total": len(manifest), "iter_id": iter_id})


@app.get("/batch/status")
async def batch_status():
    return JSONResponse(_batch)


async def _run_batch_task(manifest: list[dict], iter_id: str):
    global _batch
    run_ids = []
    for entry in manifest:
        filename = Path(entry["file"]).name
        _batch["current"] = filename
        try:
            pdf_path = engine.resolve_pdf_path(entry["file"])
            if not pdf_path:
                pdf_path = engine.resolve_pdf_path(filename)
            if not pdf_path:
                _batch["errors"].append(f"{filename}: PDF nicht gefunden")
                _batch["done"] += 1
                continue

            doc_type = DocumentType(entry["doc_type"])
            run_id = await engine.run_test(str(pdf_path), doc_type, iteration_id=iter_id)
            run_ids.append(run_id)

            # Warten bis Verarbeitung abgeschlossen (max. 120s)
            for _ in range(60):
                await asyncio.sleep(2)
                run = store.get_run(run_id)
                if run and run.status != "running":
                    break

            run = store.get_run(run_id)
            if run and run.status == "error":
                _batch["errors"].append(
                    f"{filename}: Verarbeitung fehlgeschlagen: {run.error_message}"
                )
        except Exception as e:
            _batch["errors"].append(f"{filename}: {e}")

        _batch["done"] += 1

    store.update_iteration(iter_id, status="done", completed_at=datetime.now(), run_ids=run_ids)
    _batch["running"] = False
    _batch["current"] = ""


# ── FP-Audit ──

@app.post("/fp-audit/{run_id}")
async def run_fp_audit(run_id: str):
    run = store.get_run(run_id)
    if not run:
        return JSONResponse({"ok": False, "error": "Run nicht gefunden"}, status_code=404)
    if run.status != "done":
        return JSONResponse({"ok": False, "error": "Run nicht abgeschlossen"}, status_code=400)
    result = await fp_auditor.fp_audit(run_id)
    if result["ok"]:
        return JSONResponse({"ok": True, "redirect": f"/result/{run_id}"})
    return JSONResponse(result, status_code=500)


@app.post("/batch/fp-audit")
async def start_batch_fp_audit(background_tasks: BackgroundTasks):
    latest = store.get_latest_iteration()
    if not latest:
        return JSONResponse({"ok": False, "error": "Keine Iteration vorhanden. Zuerst Batch-Test starten."})
    if latest.status == "running":
        return JSONResponse({"ok": False, "error": "Batch-Test laeuft noch."})

    runs = store.load_runs_for_iteration(latest.id)
    pending = [r for r in runs if r.status == "done"
               and store.load_raw_entities(r.id)
               and not store.load_fp_audit(r.id)]
    if not pending:
        return JSONResponse({"ok": False, "error": f"Iteration {latest.id}: Alle Runs haben bereits einen FP-Audit."})

    background_tasks.add_task(_run_batch_fp_audit_task, pending, latest.id)
    return JSONResponse({"ok": True, "count": len(pending), "iter_id": latest.id})


async def _run_batch_fp_audit_task(runs, iter_id: str):
    global _batch
    _batch = {"running": True, "total": len(runs), "done": 0, "current": "", "errors": [],
              "iter_id": iter_id}
    for run in runs:
        _batch["current"] = run.pdf_filename
        try:
            result = await fp_auditor.fp_audit(run.id)
            if not result["ok"]:
                _batch["errors"].append(f"{run.pdf_filename}: {result.get('error', '?')}")
        except Exception as e:
            _batch["errors"].append(f"{run.pdf_filename}: {e}")
        _batch["done"] += 1

    # FP-Summary aggregieren und in Iteration speichern
    all_audits = [store.load_fp_audit(r.id) for r in runs]
    all_audits = [a for a in all_audits if a]
    if all_audits:
        global_by_type: dict = {}
        total_entities = total_fp = 0
        for audit in all_audits:
            total_entities += audit.total_entities
            total_fp += audit.total_fp
            for etype, counts in audit.fp_by_type.items():
                if etype not in global_by_type:
                    global_by_type[etype] = {"total": 0, "fp": 0, "tp": 0}
                global_by_type[etype]["total"] += counts.get("total", 0)
                global_by_type[etype]["fp"] += counts.get("fp", 0)
                global_by_type[etype]["tp"] += counts.get("tp", 0)
        by_type_with_rate = {
            t: {**c, "fp_rate_pct": round(c["fp"] / c["total"] * 100) if c["total"] else 0}
            for t, c in global_by_type.items()
        }
        fp_summary = {
            "total_entities": total_entities,
            "total_fp": total_fp,
            "fp_rate_pct": round(total_fp / total_entities * 100) if total_entities else 0,
            "by_type": by_type_with_rate,
        }
        store.update_iteration(iter_id, fp_summary=fp_summary)

    _batch["running"] = False
    _batch["current"] = ""


@app.get("/fp-audit", response_class=HTMLResponse)
async def fp_audit_page(request: Request):
    iterations = store.load_iterations()
    iterations.sort(key=lambda i: i.started_at)

    # Alle Entity-Typen sammeln (fuer Spalten-Header)
    all_types: set[str] = set()
    for it in iterations:
        if it.fp_summary:
            all_types.update(it.fp_summary.get("by_type", {}).keys())
    # Wichtigste Typen vorne
    priority = ["LOCATION", "ORGANIZATION", "PERSON", "PHONE_NUMBER", "DATE_TIME",
                "ADRESSE", "PLZ_ORT", "KFZ_KENNZEICHEN", "AKTENZEICHEN",
                "VERSICHERUNGSNR", "REFERENZNR", "URL"]
    sorted_types = [t for t in priority if t in all_types] + sorted(all_types - set(priority))

    return templates.TemplateResponse(request, "fp_audit.html", {
        "iterations": iterations,
        "sorted_types": sorted_types,
        "active_nav": "fp-audit",
    })


# ── Threshold-Konfig ──

@app.get("/config/threshold")
async def get_threshold():
    return {"score_threshold": engine.get_threshold()}


@app.post("/config/threshold")
async def set_threshold(request: Request):
    body = await request.json()
    value = float(body.get("score_threshold", engine.DEFAULT_THRESHOLD))
    value = round(max(0.1, min(0.95, value)), 2)
    engine.set_threshold(value)
    return {"ok": True, "score_threshold": value}
