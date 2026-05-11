---
name: council
description: "Hole Multi-Perspektiven-Beratung bei kritischen Synthese-Fragen ein. Nur bei explizitem Aufruf nutzen — nicht automatisch. Argument: Synthese-Frage (z.B. 'Koennen wir Mimir fuer NER ersetzen?')."
context: fork
model: claude-sonnet-4-5
---

# /council

Multi-Perspektiven-Beratung via 4 Sub-Agents. Nur bei explizitem Aufruf.
Erwartung: 3-5 Aufrufe in Phase 1 der gesamten Research-Phase.

## Schritt 0: Frage schaerfen

Formuliere die Synthese-Frage praezise bevor Agents aufgerufen werden.
Format: "Empfehlung: [konkrete Entscheidungsfrage]"

Lies dazu: `knowledge/skadi-pipeline.md` und relevante Research-Ergebnisse.

## Schritt 1: 4 Sub-Agent-Aufrufe (parallel)

Delegiere an alle vier Council-Mitglieder mit der gleichen Frage:

```
Frage fuer den Council: [Synthese-Frage]

Kontext:
- [Relevante Research-Ergebnisse, 3-5 Saetze]
- [Bekannte Constraints, 2-3 Saetze]

Deine Aufgabe: Analysiere aus deiner Perspektive und gib ein klares Votum ab.
```

Agents: tech-researcher, cost-risk-auditor, skadi-user-advocate, pragmatic-skeptic.

## Schritt 2: Voten sammeln

Fuer jeden Agent: Kernaussage + Votum (fuer / dagegen / mit Bedingungen) + 1-2 Kernargumente.

## Schritt 3: Konsolidierung + Synthese

```markdown
# Council-Ergebnis: [Frage]
Datum: [YYYY-MM-DD]

## Frage

[Praezise Synthese-Frage]

## Voten

| Agent | Votum | Kernargument |
|-------|-------|--------------|
| tech-researcher | [ja/nein/bedingt] | ... |
| cost-risk-auditor | [ja/nein/bedingt] | ... |
| skadi-user-advocate | [ja/nein/bedingt] | ... |
| pragmatic-skeptic | [ja/nein/bedingt] | ... |

## Meinungsverschiedenheiten

[Was ist strittig? Warum sind Agents unterschiedlicher Meinung?]

## Synthese-Empfehlung

**Empfehlung: [Klar formuliert]**

Begruendung: [Warum diese Empfehlung trotz ggf. gemischter Voten?]

Decision-Gate: Wenn [X], dann [A]. Wenn [Y], dann [B].

Annahmen die noch geklaert werden muessen: [O] ...

## Naechster Schritt

[Konkret: was tun wir jetzt?]
```

## Schritt 4: Ablage

Speichere in `knowledge/council-[datum]-[slug].md`.
