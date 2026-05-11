# Evaluation: skadi-doku

## Golden-Path-Tests

### Szenario 1: Sparring zum Projekt-Start (erste Session)

**Input (Andi):** "Lass uns loslegen. Wo fangen wir an?"

**Erwartetes Verhalten:**
- Team liest project-status.md + lessons.md + knowledge/skadi-pipeline.md
- Gibt 3-5 Bullets Lage-Briefing (Phase 0, offene Auftrags-Parameter)
- Schlaegt aktiv vor: Strategie-Sync-Doc fuer Henrik-Gespraech als naechsten Schritt
- Begruendet: "wir wissen noch nicht welche Fragen wir stellen sollen — das klaert sich erst im Gespraech"
- Markiert klar wo eigenes Urteil endet und Entscheidung bei Andi liegt
- Wartet auf Reaktion, startet nicht selbst losarbeiten

**Erfolgskriterium:**
- Strategischer Vorschlag mit Begruendung, keine blindes Drauflosarbeiten
- W/A/O-Marker sind gesetzt
- Kein Abdriften in "wie kommunizieren wir mit der Kanzlei generell"
- Andi kann direkt mit "ja mach" oder "nein, erstmal X" antworten

---

### Szenario 2: Decision-Synthese mit Council

**Input (Andi):** "Wir haben jetzt Daten zu OCR (Tesseract, PaddleOCR, easyOCR) und NER (Mimir, spaCy DE, Flair). Kannst du eine Empfehlung formulieren, ob wir Mimir fuer NER ersetzen koennen?"

**Erwartetes Verhalten:**
- Main-Agent erkennt: Synthese-Frage mit mehreren Perspektiven → /council
- /council ruft alle 4 Sub-Agents mit der Frage auf
- tech-researcher: bewertet Modell-Qualitaet DE-Rechtssprache
- cost-risk-auditor: bewertet Fix-Kosten-Logik (Mimir GPU laeuft sowieso)
- skadi-user-advocate: bewertet Wartezeit + Verlaesslichkeit
- pragmatic-skeptic: prueft ob Komplexitaet gerechtfertigt
- Konsolidiertes Output-Doc mit allen 4 Voten + Synthese-Empfehlung

**Erfolgskriterium:**
- Output zeigt echte Meinungsverschiedenheit (nicht alle stimmen zu)
- Synthese trifft trotzdem klare Empfehlung
- Decision-Gate formuliert: "wenn GPU sowieso laeuft → dann X; wenn nicht → dann Y"
- Annahmen klar als [A] oder [O] markiert

---

### Szenario 3: Henrik-High-Level-Frage

**Input (Henrik, via Henrik-Starter):** "Wo stehen wir? Was sind die offenen Punkte?"

**Erwartetes Verhalten:**
- Team erkennt Henrik-Modus (vom Starter-Script gesetzt)
- Lagebericht: 3-5 Bullets, kein Tech-Jargon, keine Architektur-Details
- Separater Block "Klaerungs-Bedarf von Ihnen" — konkrete Fragen, nummeriert
- Kurz: "naechste Schritte"
- Kein Code, keine Stack-Details, keine Abwaegungen zwischen Libraries

**Erfolgskriterium:**
- Henrik-tauglich kompakt (muss in 2 Minuten lesbar sein)
- Klare Klaerungs-Liste ohne technischen Ballast
- Anwaltlich nuechtern — keine Floskeln wie "wir machen gute Fortschritte"
- Andi wuerde das so weiterleiten koennen
