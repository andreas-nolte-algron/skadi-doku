---
name: poc
description: "Erstelle Python-Prototypen gegen Skadi-Test-PDFs. Nutzen wenn technische Option praktisch getestet werden soll. Argument: Technologie + Ziel (z.B. 'PyMuPDF Textextraktion', 'spaCy NER Deutsch')."
context: fork
model: claude-sonnet-4-5
---

# /poc

Iteratives Code-Schreiben + Messung gegen die Skadi-Test-PDFs.

## Schritt 0: Argument-Check

Argument aus Aufruf extrahieren: Technologie + Ziel.
Wenn keins angegeben: Rueckfrage "Welche Technologie soll getestet werden, gegen welches Ziel?"

## Schritt 1: Kontext laden

Lies `knowledge/skadi-pipeline.md` — insbesondere die Decision-Gates und bekannten Issues.
Verstehe was die C#-Pipeline macht, damit der Python-PoC vergleichbar testet.

## Schritt 2: Setup-Check

Pruefe ob Test-PDFs verfuegbar sind. Wenn nicht: klar kommunizieren, Pfad erfragen.
Pruefe ob benoetigte Python-Pakete installiert sind (pip list oder import-Test).

## Schritt 3: PoC entwickeln

Iterativ:
1. Minimaler Code der das Ziel adressiert
2. Gegen 1 Test-PDF laufen lassen
3. Output beurteilen — funktioniert es, was fehlt?
4. Iterieren bis aussagekraeftiges Ergebnis

Code-Qualitaet: functional beats elegant. Kein Produktions-Code.
Jeder Schritt soll messbare Aussage liefern.

## Schritt 4: Output-Dokument

```markdown
# PoC: [Technologie] — [Ziel]
Datum: [YYYY-MM-DD]

## Setup

[Pakete, Versionen, Aufruf-Kommando]

## Code

```python
[Minimaler funktionierender Code]
```

## Ergebnisse

| PDF | C#-Baseline | Python-Output | Delta |
|-----|-------------|---------------|-------|
| [Dateiname] | [Qualitaet/Zeichen] | [Qualitaet/Zeichen] | [besser/schlechter/gleich] |

## Bewertung

[Was haben wir gelernt? W/A/O-Marker]

## Issue 1 / Issue 2 Implikation (falls relevant)

[Beantwortet der PoC eine der bekannten Issues?]

## Naechster Schritt

[Was brauchen wir noch um eine Entscheidung zu treffen?]
```

## Schritt 5: Ablage

Speichere Code + Ergebnis-Doc in `knowledge/poc-[technologie]-[datum].md`.
Code-Artefakte wenn sinnvoll in `scripts/poc/` ablegen.
