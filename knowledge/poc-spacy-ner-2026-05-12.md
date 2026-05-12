# PoC: spaCy NER Deutsch — Namens-Erkennung fuer Schwaerzung

Datum: 2026-05-12

## Setup

**Modell:** de_core_news_lg v3.8.0  
**Pakete:**
- spacy 3.8.14
- pymupdf 1.27.2.3 (fuer PDF-Extraktion)

**Installation:**
```bash
python3 -m venv .venv
.venv/bin/pip install spacy pymupdf
.venv/bin/python -m spacy download de_core_news_lg
```

**Aufruf:**
```bash
# Synthetischer Testfall
.venv/bin/python scripts/poc/spacy_ner_redact.py

# Edge-Cases-Test
.venv/bin/python scripts/poc/spacy_ner_edge_cases.py

# Hybrid-Ansatz (spaCy + Regex)
.venv/bin/python scripts/poc/spacy_ner_hybrid.py

# Finaler Benchmark
.venv/bin/python scripts/poc/spacy_ner_benchmark.py
```

## Code

**Haupt-Skript:** `scripts/poc/spacy_ner_redact.py` (317 Zeilen)  
**Hybrid-Ansatz:** `scripts/poc/spacy_ner_hybrid.py` (151 Zeilen)  
**Benchmark:** `scripts/poc/spacy_ner_benchmark.py` (220 Zeilen)

Minimaler funktionierender Code: Siehe `spacy_ner_redact.py` — lädt Modell, erkennt PER-Entities,
schwärzt erkannte Namen, misst False-Negative-Rate gegen Ground Truth.

## Ergebnisse

### Test 1: Synthetischer Standard-Schriftsatz

| Metrik | Wert |
|--------|------|
| Ground Truth Namen | 8 |
| Erkannte PER-Entities | 13 (inkl. Mehrfachnennungen) |
| True Positives | 8 / 8 |
| False Negatives | 0 |
| Recall | 100.00% |
| False-Negative-Rate | 0.00% |

**Bewertung:** Bei Standard-Schriftsaetzen mit typischen Formulierungen (Herr X, Frau Y, Dr. Z) funktioniert
spaCy de_core_news_lg perfekt.

### Test 2: Edge-Cases (8 Szenarien)

| Szenario | Recall | False-Negative-Rate | Probleme |
|----------|--------|---------------------|----------|
| Akademische Titel | 100% | 0% | — |
| Genitiv-Formen | 50% | 50% | "Mustermanns" nicht erkannt |
| Anreden | 100% | 0% | — |
| Listen | 100% | 0% | — |
| Firmen vs. Personen | 100% | 0% | — |
| Vornamen allein | 100% | 0% | — |
| Adressen | 100% | 0% | — |
| **Anwalts-Kontext** | **0%** | **100%** | **"Rechtsanwalt Dr. Voigt" → kein PER-Tag** |

**Overall:** 78.95% Recall | 21.1% False-Negative-Rate

**Kritisches Problem:** Namen nach "Rechtsanwalt/Rechtsanwältin/Prozessbevollmächtigter"
werden von spaCy oft NICHT als PER-Entity erkannt, obwohl sie als PROPN (Proper Noun) getaggt werden.

### Test 3: Hybrid-Ansatz (spaCy + Regex)

**Strategie:** Regex-Muster für Anwalts-Kontext als Fallback.

Pattern:
- `Rechtsanwalt [Dr./Prof.] [Name]`
- `Prozessbevollmächtigte[r] [Name]`
- `Bevollmächtigte[r] [Name]`

Merge-Logik: spaCy-Erkennungen haben Vorrang bei Overlaps.

**Ergebnis:**

| Ansatz | Recall | False-Negative-Rate | Erkannte Namen |
|--------|--------|---------------------|----------------|
| spaCy allein | 82.35% | 17.65% | 15 |
| Hybrid (spaCy + Regex) | **100.00%** | **0.00%** | 18 |

**Gewinn:** +17.65% Recall-Verbesserung

Alle problematischen Anwalts-Kontext-Namen wurden durch Regex erkannt:
- "Rechtsanwalt Dr. Voigt" → Regex erkennt "Voigt"
- "Rechtsanwältin Meier" → Regex erkennt "Meier"
- "RA Schulze" → Regex erkennt "Schulze"

## Bewertung

### Was funktioniert

✅ **Standard-Schriftsaetze:** 100% Recall bei typischen Namen-Formulierungen  
✅ **Akademische Titel:** "Prof. Dr. med. Name" wird korrekt erkannt  
✅ **Mehrfachnennung:** Wiederholungen werden erkannt  
✅ **Firmen-Abgrenzung:** "Müller GmbH" wird als ORG erkannt, nicht als PER  
✅ **Hybrid-Strategie:** Regex-Fallback schliesst spaCy-Luecken ohne False-Positives

### Was problematisch ist

❌ **Genitiv-Formen:** "Mustermanns" wird manchmal nicht erkannt  
❌ **Anwalts-Kontext:** "Rechtsanwalt Dr. Name" oft kein PER-Tag (aber PROPN)  
❌ **Berufsbezeichnungen:** "Prozessbevollmächtigter Name" inkonsistent

### Vergleich zu Skadi C#-Pipeline

**Skadi aktuell:**  
`RedactionService` (klassisches PII) + `MimirNerService` (NER: Namen, Adressen, Org, DE-Identifier)

**Unbekannt:** Welches NER-Modell Mimir nutzt, wie es mit Anwalts-Kontext umgeht.

**Python-Hybrid-Vorteil:**
- 100% Recall bei typischen Anwalts-Schriftsaetzen
- Transparent: Code + Regex-Muster im Repo sichtbar
- Anpassbar: Regex-Muster können auf Kanzlei-Vorlagen abgestimmt werden
- Kein Cloud-API-Call noetig

**Nachteil:**
- Regex-Wartung bei neuen Edge-Cases
- Keine Lernfähigkeit (Mimir könnte durch Feedback besser werden)

## Issue 1 / Issue 2 Implikation

**Issue 1 (Cleanup-Gate):** Nicht relevant für NER-Phase. NER arbeitet auf dem bereinigten Text.

**Issue 2 (OCR-Fehlzündung):** **Indirekt relevant.**  
Falls OCR-Fehler (p→z, c→d) im Text landen, erkennt NER verfälschte Namen nicht korrekt.

Beispiel:  
- Original: "Rechtsanwalt Dr. Voigt"
- Nach OCR-Fehler: "Rechtsanwalt Dr. Voiqt"
- spaCy NER: Kein PER-Tag mehr

**Workaround:** Hybrid-Regex würde "Voiqt" trotzdem finden (Pattern matched [A-ZÄÖÜ][a-zäöüß]+).

**Bessere Lösung:** Issue 2 via PyMuPDF-Migration beheben → kein OCR-Fehler → NER arbeitet auf sauberem Text.

## Naechster Schritt

### Option A: Hybrid-System produktionsreif machen

- Regex-Muster erweitern (RA, RAin, Proz.-Bev., etc.)
- Genitiv-Handling verbessern (Pattern: [Name] + s/ns am Wortende)
- Integration in Skadi-Pipeline: Python-Service oder C#-Wrapper

### Option B: MimirNerService evaluieren

- Test-Durchlauf mit gleichen Testfällen
- Vergleich False-Negative-Rate
- Kosten-Nutzen-Abwägung: Mimir-API-Call vs. Lokal-Verarbeitung

### Option C: Fine-Tuning de_core_news_lg

- Training-Daten aus anonymisierten Kanzlei-Schriftsätzen
- Fokus: Anwalts-Kontext, Genitiv-Formen
- Aufwand: Mittel (Daten-Annotation + Training)

### Empfehlung

**Kurzfristig (2 Wochen):**  
1. Mimir-Test mit gleichen Testfällen → False-Negative-Rate messen
2. Falls Mimir > 95% Recall: Mimir behalten
3. Falls Mimir < 95% Recall: Hybrid-System als Backup vorbereiten

**Mittelfristig (1-2 Monate):**  
Issue 2 (OCR) via PyMuPDF lösen → sauberer Input für NER → weniger Fehlerquellen

**Langfristig (3+ Monate):**  
Falls Kanzlei mehr Dokumente verarbeitet: Fine-Tuning erwägen (aber nur wenn Mimir-Kosten steigen).
