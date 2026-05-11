# skadi-doku

DSGVO-konforme Doku-Verarbeitung fuer eine Anwaltskanzlei — Research-Phase.
Klaert Auftrags-Parameter, baut Capability-Cost-Map, entwickelt PoCs.

## Wissensquellen

`knowledge/skadi-pipeline.md` — C#-Pipeline-Architektur, Decision-Gates, bekannte Issues.
`knowledge/dsgvo-doku-verarbeitung.md` — Grundregeln lokal vs. cloud, Anwaltsgeheimnis.
`lessons.md` — Methodische Erkenntnisse. Bei Sessionstart lesen.

## Projektstruktur

```
skadi-doku/
  CLAUDE.md                        # Diese Datei
  main-agent.md                    # System Prompt
  project-status.md                # Arbeitsgedaechtnis
  lessons.md                       # Erkenntnisse
  knowledge/                       # On-Demand-Referenz
  scripts/                         # Starter + Starter-Prompts
  specs/eval.md                    # Golden-Path-Tests
  .claude/agents/                  # Council Sub-Agents
  .claude/skills/                  # Skills
```

## Skills

| Skill | Aufgabe | Kontext |
|-------|---------|---------|
| /research | Strukturierte Recherche (use-case/tech/cost) mit DSGVO-Spalte | fork |
| /poc | Python-Prototypen gegen Test-PDFs, Code + Vergleichs-Doc | fork |
| /council | Multi-Perspektiven-Synthese via 4 Sub-Agents | fork |
| /strategie-sync | Andi-Henrik-Gespraeche vorbereiten | inline |
| /track | project-status.md aktualisieren | inline |
| /save | Session-Commit: /track + commit | inline |

## Konventionen

- Sprache intern: Deutsch, ae/oe/ue in technischen Dateien
- Endnutzer-Doc (Henrik-Mails, Kanzlei-Kommunikation): Deutsch, ae/oe/ue, anwaltlich nuechtern
- Code: Englisch
- Anti-GPTism: keine Floskeln, direkt zur Sache
- **Rueckwaerts-Suche bei Umbau:** `grep -r` nach Konsumenten vor strukturellen Aenderungen
- **Skadi-Repo:** nur lesen/editieren, kein Push — User pusht selbst

## Deployment

Lokal gebaut. Andi uebertraegt auf Algron-Server (`~/claude-projects/skadi-doku/`
mit Symlink `~/workspace/teams/skadi-doku/`). Beim ersten Run auf Algron: `.env`
mit ANTHROPIC_API_KEY + ggf. Mimir-API-Konfig anlegen.

## Sessionende

Zwischenergebnisse in Projektdateien sichern. `/save` ausfuehren.
