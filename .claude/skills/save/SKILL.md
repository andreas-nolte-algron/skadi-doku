---
name: save
description: "Speichere Session: /track ausfuehren, dann committen. Aufrufen bei Sessionende."
context: inline
---

# /save

Session sichern. Reihenfolge:

## Schritt 1: /track ausfuehren

project-status.md aktualisieren (Erkenntnisse, offene Punkte).

## Schritt 2: Commit

```bash
cd ~/workspace/teams/skadi-doku
git add -A
git commit -m "Session [DATUM]: [1-Satz was gemacht wurde]"
```

**Kein Push** — User pusht selbst (block-foreign-commits gilt fuer alle Repos).

## Schritt 3: Bestaetigung

Kurze Zusammenfassung: was committed, welche Dateien geaendert.
