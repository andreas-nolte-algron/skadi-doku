---
name: strategie-sync
description: "Bereite Andi-Henrik-Gespraeche zu auftrags-bezogenen Strategie-Entscheidungen vor. Nutzen wenn ein Gespraech mit Henrik ansteht oder vorbereitet werden soll. NICHT fuer allgemeine Kanzlei-Kommunikation."
context: inline
---

# /strategie-sync

Vorbereitung von Strategie-Gespraechen zwischen Andi und Henrik.
Scope: Auftrags-Parameter, Entscheidungspunkte, offene Fragen — kein Stakeholder-Management.

## Schritt 1: Kontext laden

Lies:
- `project-status.md` (offene Auftrags-Parameter, letzte Sync-Punkte)
- Relevante Research-Ergebnisse aus `knowledge/` (falls vorhanden)

## Schritt 2: Sync-Doc erstellen

Format (anwaltlich nuechtern, keine Floskeln):

```markdown
# Strategie-Sync: [Thema/Anlass]
Datum: [YYYY-MM-DD]
Fuer: Andi-Henrik-Gespraech

## Ausgangslage

[2-3 Saetze: Wo stehen wir, warum brauchen wir diesen Sync]

## Optionen / Entscheidungspunkte

### Option A: [Kurzname]
- Was: ...
- Voraussetzung: ...
- Implikation: ...

### Option B: [Kurzname]
- Was: ...
- Voraussetzung: ...
- Implikation: ...

## Offene Punkte die Henrik klaeren muss

1. [Konkrete Frage] — brauchen wir fuer [Entscheidung X]
2. [Konkrete Frage] — ...

## Empfohlene naechste Schritte

[Was sollte nach dem Gespraech passieren? Wer macht was?]

## Was wir NICHT besprechen muessen

[Scope-Grenze explizit machen — was ist bereits entschieden / ausserhalb des Auftrags]
```

## Schritt 3: In project-status.md verlinken

Notiere unter "Letzte Henrik-Sync-Punkte" das Datum + Thema.

## Ton-Regel

Anwaltlich nuechtern: keine "spannenden Moeglichkeiten", keine Hochglanz-Praesentation.
Fakten, Optionen, Fragen. Henrik ist kein Tech-Konsument — er ist Mit-Entscheider.
