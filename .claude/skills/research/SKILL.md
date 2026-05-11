---
name: research
description: "Fuehre strukturierte Recherche zu Doku-Verarbeitungs-Themen durch. Nutzen wenn konkrete Recherche-Frage zu Use Cases, Technologien oder Kosten besteht. Argument: Modus (use-case | tech | cost) + Thema."
context: fork
model: claude-sonnet-4-5
---

# /research

Strukturierte Recherche fuer skadi-doku mit DSGVO-Kontext und Annahme-Markern.

## Schritt 0: Modus-Erkennung

Argument aus dem Aufruf extrahieren. Format: `/research [modus] [thema]`

Modi:
- `use-case` — Recherche zu Kanzlei-Workflows und Anforderungen
- `tech` — Technologie-Vergleich (OCR, NER, PDF-Extraktion, Modelle)
- `cost` — Kosten-Analyse (Compute, APIs, Infrastruktur)

Wenn Modus unklar: mit der Frage "Recherchiere ich Use Cases, Technologien oder Kosten?" beginnen.

## Schritt 1: Kontext laden

Lies immer:
- `knowledge/skadi-pipeline.md` (aktueller Stack)
- `knowledge/dsgvo-doku-verarbeitung.md` (Constraints)

Bei tech/cost zusaetzlich: relevante bestehende Knowledge-Files pruefen (vermeidet Doppelung).

## Schritt 2: Recherche durchfuehren

Nutze WebSearch + WebFetch fuer aktuelle Informationen.
Fokus immer auf: Deutsche Rechtssprache + lokale Deployment-Option + DSGVO-Kompatibilitaet.

## Schritt 3: Output-Template

```markdown
# Research: [Thema] ([Modus])
Datum: [YYYY-MM-DD]

## Zusammenfassung

[3-5 Saetze Kernaussage mit W/A/O-Markern]

## Ergebnisse

| Option | Capability [W/A/O] | DSGVO-Eignung [W/A/O] | Kosten-Indikator [W/A/O] | Quellen |
|--------|-------------------|----------------------|--------------------------|---------|

## Annahmen die noch geklaert werden muessen

- [O] ...

## Empfehlung / naechster Schritt

[Konkret — was tun wir als naechstes basierend auf diesen Ergebnissen?]
```

## Schritt 4: Ablage

Speichere Ergebnis in `knowledge/[thema-slug].md`.
Update `project-status.md` wenn neue Erkenntnisse offene Auftrags-Parameter beeinflussen.
