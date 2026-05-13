# Project Status: skadi-doku

## Aktueller Stand

- 2026-05-11: Phase 0 gestartet. Stakeholder-Kontext, Research, Henrik-Gespraech.
- 2026-05-12: Henrik-Gespraech gefuehrt. Auftrag und Deliverable geklaert.
- 2026-05-12: Erster PoC (spaCy + Regex). Lief auf synthetischen Daten.
- 2026-05-12: Test mit echten Kanzlei-Dokumenten: Regex-Ansatz regressioniert → STOP.
- 2026-05-12: Pivot zu **Presidio** (Microsoft, Open Source). Bessere Context-Scoring, Custom Recognizer.
- 2026-05-12: Web-Dashboard gebaut (FastAPI + Jinja2). Live unter http://77.42.39.93:8081/
- 2026-05-13: Auto-Evaluate via Ollama + Qwen3-8B implementiert. Laeuft ueber Reverse-SSH-Tunnel.
- 2026-05-13: **Iterations-Architektur** gebaut. FP-Audit laeuft jetzt auf aktuelle Iteration (6 Runs), nicht alle historischen. Vergleichstabelle auf /fp-audit. Altdaten archiviert (pdfs_legacy_v0/).
- 2026-05-13: Baseline gemessen: LOCATION 77%, ORGANIZATION 66%, PERSON 51% FP-Rate. Naechster Schritt: Presidio-Threshold-Tuning.

## Kernentscheidungen

**Deliverable:** Docker API-Service. Input: PDF (auch gescannt). Output: geschwaerzter Text, Claude-kompatibel. [W]
**PII-Engine:** Presidio + spaCy de_core_news_lg + 9 Custom Recognizer (Kanzlei-spezifisch). [W]
**Mimir:** Overkill fuer diesen Use-Case. Wird nicht benoetigt. [W]
**Kosten-Ziel:** Weg von ~1000 EUR/Monat GPU. Hetzner-Server (250 EUR/Monat oder weniger). [W]
**Fehlertoleranz:** Max 3%. [W]
**Deadline:** 1 Woche — 1 Kategorie integriert und ausprobierbar. [W]
**DSGVO-Constraint:** Echte Kanzlei-Daten bleiben auf Server. Claude darf sie nicht sehen. [W]

**Dokumenttypen (Prioritaet):**
- Schreiben der Versicherer
- Schriftsaetze aus Gerichtsverfahren
- Gutachten
- Reparatur- und andere Abrechnungen
- (Eigene Rechnungen NICHT im Fokus)
Kontext: Verkehrs-/Versicherungsrecht. [A]

## Tech-Stack (aktuell)

| Komponente | Technologie | Status |
|------------|------------|--------|
| PDF-Extraktion | PyMuPDF + Tesseract OCR | Laeuft [W] |
| PII-Erkennung | Presidio + spaCy de_core_news_lg | Laeuft, FP-Problem [W] |
| Web-Dashboard | FastAPI + Jinja2 + Vanilla JS | Laeuft [W] |
| Auto-Eval | Ollama + Qwen3-8B auf Andis Laptop | Gebaut, Test steht aus [W] |
| Persistence | JSON-Dateien (runs.json, evaluations.json) | Laeuft [W] |
| Server | Hetzner 8GB RAM, 4 CPU | Laeuft [W] |

## Bekannte Probleme

1. **False Positives**: Presidio erkennt zu viel als PII — Formular-Labels, Fachbegriffe. Hauptproblem. [W]
2. **OCR-Zeilenumbrueche**: PyMuPDF uebernimmt PDF-Layout-Umbrueche in den Text. Post-Processing fehlt. [W]
3. **Alte Runs ohne Rohdaten**: Vor 2026-05-13 erstellte Testlaeufe haben keine Text+Entity-Dateien. Neu testen noetig fuer Auto-Eval. [W]

## Offene Auftrags-Parameter

Geklaert:
- [x] Haupt-Use-Case: Schwaerzung als Docker API-Service. [W]
- [x] Fehlertoleranz: Max 3%. [W]
- [x] Dokumenttypen: Liste vom Kanzlei-Chef. [W]
- [x] Zeitrahmen: 1 Woche fuer erste Kategorie. [W]
- [x] Kostenmodell: An Kanzlei weitergereicht. [W]
- [x] Mimir: Overkill, nicht benoetigt. [W]
- [x] Deployment: Docker. [W]

Noch offen:
- [ ] Volumen (Dokumente pro Tag/Monat) — kein Blocker fuer PoC.
- [ ] Anteil gescannt vs. digital — finden wir beim Testen raus.
- [ ] Aktenzeichen-Format Voigt — brauchen wir fuer Regex-Tuning.

## Dashboard-Architektur

```
dashboard/
  app.py              # FastAPI Routes (~15 Endpoints)
  engine.py           # Wraps test_lokal.py, Analyzer-Singleton
  evaluator.py        # Auto-Eval: Prompt + Ollama-Call + Parsing (experimentell)
  fp_auditor.py       # FP-Audit: TP/FP-Klassifikation pro Entity via LLM
  store.py            # JSON-Persistence (PDF-zentriert + Iterationen)
  models.py           # Pydantic: TestRun, Iteration, FpAudit, Evaluation, DocumentType
  templates/          # 7 Jinja2-Templates
  static/             # CSS + JS
  data/
    index.json                    # Run-Index: id -> pdf_slug + Metadaten
    iterations.json               # Iteration-Metadaten inkl. fp_summary
    pdfs/
      {pdf-slug}/runs/{run-id}/   # run.json, text.txt, entities.json, *.html
    pdfs_legacy_v0/               # Archivierte Altdaten (vor Iterations-Umbau)
```

## Auto-Eval-Architektur

```
[Dashboard auf Hetzner] --localhost:11434--> [Reverse-SSH-Tunnel] --> [Andis Laptop: Ollama + Qwen3-8B]
```

Prompt schickt: Originaltext + Entity-Liste mit Kontext.
Qwen3 bewertet: TP/FP pro Entity, findet FN, fuellt Checkliste, gibt Verdict.
Ergebnis: Evaluation-Objekt (gleiche Struktur wie manuelle Bewertung).

## Naechste Schritte

1. **Server neu starten** (uvicorn) — Iterations-Architektur aktivieren
2. **Presidio Threshold-Tuning**: score_threshold in test_lokal.py von ~0.35 auf 0.5-0.6 anpassen
3. **Erste saubere Iteration**: Batch-Test mit Konfig-Notiz "threshold=0.6" starten, dann Batch-FP-Audit
4. **Baseline vergleichen**: Neue FP-Raten vs. alte Baseline (LOCATION 77%, ORG 66%, PERSON 51%)
5. **Iterieren** bis FP-Raten akzeptabel (Ziel: <25% fuer Haupt-Typen)

## Letzte Henrik-Sync-Punkte

- 2026-05-12: Henrik-Gespraech → Deliverable, Fehlertoleranz, Dokumenttypen, Deadline geklaert.

## Build-Notizen

- Team erstellt: 2026-05-11. Hetzner-Server: 8GB RAM, 4 Kerne.
- Dashboard: uvicorn auf Port 8081 (8080 war belegt)
- Presidio Analyzer: ~600MB RAM beim Start, ~5s Ladezeit
- Ollama auf Laptop: Qwen3-8B Q4_K_M, braucht ~5GB VRAM
