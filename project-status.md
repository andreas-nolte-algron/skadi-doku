# Project Status: skadi-doku

## Aktueller Stand

- 2026-05-11: Phase 0 gestartet. Stakeholder-Kontext, Research, Henrik-Gespraech.
- 2026-05-12: Henrik-Gespraech gefuehrt. Auftrag und Deliverable geklaert.

**Deliverable:** Docker API-Service. Input: PDF (auch gescannt). Output: geschwaerzter Text, Claude-kompatibel. [W]
**Tech-Richtung:** Open Source, kein eigenes LLM noetig. Regex + spaCy + Tesseract auf CPU reicht. [W]
**Mimir:** Overkill fuer diesen Use-Case (Gemma 4, RTX 6000, 96GB). Wird nicht benoetigt. [W]
**Kosten-Ziel:** Weg von ~1000 EUR/Monat GPU. Hetzner-Server (250 EUR/Monat oder weniger). Kanzlei-Chef vergleicht mit 20 EUR/User/Jahr SaaS (Halbwissen). [W]
**Fehlertoleranz:** Max 3%. [W]
**Deadline:** 1 Woche — 1 Kategorie integriert und ausprobierbar. [W]

**Dokumenttypen vom Kanzlei-Chef (Prioritaet):**
- Schreiben der Versicherer
- Schriftsaetze aus Gerichtsverfahren
- Gutachten
- Reparatur- und andere Abrechnungen
- (Eigene Rechnungen NICHT im Fokus)
Kontext: Vermutlich Verkehrs-/Versicherungsrecht. [A]

**PII-Kategorien (abgeleitet):**
Namen, Adressen, Aktenzeichen, Gesundheitsdaten (Gutachten!), Versicherungsnummern, Finanzdaten. [A]

**DSGVO-Constraint:** Test-Dokumente von Kanzlei enthalten sensitive Daten — duerfen nicht von Claude gelesen werden. PoC wird mit synthetischen Daten gebaut, Validierung gegen echte Daten erfolgt lokal durch Andi. [W]

**Infrastruktur:** Hetzner-Server (8GB RAM, 4 CPU-Kerne) — reicht fuer PoC-Stack. [W]

**Research abgeschlossen:** Regex+NER-Pipeline → `knowledge/regex-ner-pii-deutsch.md`. Presidio + spaCy/Flair als Optionen identifiziert. [W]

## Offene Auftrags-Parameter

Geklaert:
- [x] Haupt-Use-Case: Schwaerzung als Docker API-Service. [W]
- [x] Fehlertoleranz: Max 3%. [W]
- [x] Dokumenttypen: Liste vom Kanzlei-Chef (siehe oben). [W]
- [x] Zeitrahmen: 1 Woche fuer erste Kategorie, dann inkrementell. [W]
- [x] Kostenmodell: An Kanzlei weitergereicht, muss begruendbar sein. [W]
- [x] Mimir: Overkill, wird nicht benoetigt. [W]
- [x] Deployment: Docker. [W]

Noch offen:
- [ ] Volumen (Dokumente pro Tag/Monat) — noch nicht geklaert, kein Blocker fuer PoC.
- [ ] Anteil gescannt vs. digital — finden wir beim Testen raus.
- [ ] Aktenzeichen-Format Voigt — brauchen wir fuer Regex, aber nicht fuer erste Kategorie.
- [ ] Tabellen/Rechnungen konkreter Zweck — kein Blocker, erstmal Standard-PDFs.

## Letzte Henrik-Sync-Punkte

- 2026-05-11: Erstes Scoping vorbereitet → `strategie-sync-2026-05-11.md`
- 2026-05-12: Henrik-Gespraech gefuehrt → `henrik-prep-2026-05-11.md` (mit Antworten)
  Geklaert: Deliverable, Fehlertoleranz, Dokumenttypen, Deadline, Mimir-Richtung.

## PoC-Ergebnisse

- **PyMuPDF Textextraktion:** Funktioniert. OCR-Issue 2 (Fehlzuendung bei Vektor-PDFs) tritt nicht auf. → `knowledge/poc-pymupdf-2026-05-12.md`
- **spaCy NER Deutsch (Hybrid):** spaCy allein hat Luecke bei Anwalts-Kontext (~21% FN-Rate). Mit Regex-Fallback: **100% Recall, 0% False Negatives** auf synthetischen Schriftsaetzen. → `knowledge/poc-spacy-ner-2026-05-12.md`
- Code: `scripts/poc/pymupdf_extract.py`, `batch_test.py`, `spacy_ner_*.py`

## Naechste Schritte

1. FastAPI-Endpoint + Docker — Service zusammenbauen
2. Andi validiert lokal gegen echte Kanzlei-Dokumente
3. Messen gegen 3%-Schwelle
4. Weitere PII-Kategorien (Adressen, IBAN, Aktenzeichen)

## Build-Notizen

Team erstellt: 2026-05-11. Hetzner-Server: 8GB RAM, 4 Kerne.
PoC-Stack: PyMuPDF + Tesseract + spaCy + FastAPI + Docker. Kein LLM noetig.
