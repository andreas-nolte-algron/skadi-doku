# Lessons

Akkumulierte Korrekturen und Erkenntnisse. Append-only.

## Routing & Delegation

(Wer macht was, welche Zuordnung war falsch/richtig)

## Technisch

<!-- Bekannte Pitfalls stehen in knowledge/skadi-pipeline.md — nicht duplizieren -->

- **Regex-Tuning von Hand regressioniert** (2026-05-12): Mehr Regex-Patterns + Blocklisten haben die Erkennung verschlechtert, nicht verbessert. Pattern-Interaktionen sind unvorhersehbar. Pivot zu Presidio war richtig — Framework mit Context-Scoring statt Hand-Tuning.

- **Presidio False Positives** (2026-05-12): Presidio mit score_threshold=0.3 erkennt zu viel. Besonders LOCATION und ORGANIZATION feuern auf Formular-Labels ("Amtl.", "KD-Berater", "Betriebs-Nr."). Tuning-Hebel: Score-Threshold hoeher, Entity-Typ-Whitelist, Post-Filter.

- **Starlette 1.0 API-Bruch** (2026-05-12): `TemplateResponse("name.html", {"request": req})` → `TemplateResponse(req, "name.html", {})`. Fehlermeldung: `TypeError: unhashable type: 'dict'`.

- **Ollama braucht GPU-VRAM, nicht RAM** (2026-05-12): Hetzner-Server hat keine GPU. LLM-Eval muss auf Andis Laptop (8GB VRAM) laufen. Reverse-SSH-Tunnel als Bruecke.

- **OCR-Zeilenumbrueche** (2026-05-12): PyMuPDF uebernimmt PDF-Layout-Spaltenumbrueche wortwortlich in den Text. Sieht im HTML seltsam aus. Braucht Post-Processing (Zeilen-Merge bei nicht-Satzende).

## Prozess

- **Automatisierter Eval-Loop vor manuellem Tuning** (2026-05-12): Andi hat nach 2 manuellen Test-Iterationen "STOP" gesagt. Ohne Messung ist jede Aenderung Stochern im Nebel. Erst Eval automatisieren, dann tunen.

- **Synthetische Tests taeuschen** (2026-05-12): 100% Recall auf synthetischen Daten, deutlich schlechter auf echten Kanzlei-Dokumenten. Immer gegen echte Daten validieren.
