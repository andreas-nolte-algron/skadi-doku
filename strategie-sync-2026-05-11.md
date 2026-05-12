# Strategie-Sync: Erstes Scoping skadi-doku
Datum: 2026-05-11
Fuer: Andi-Henrik-Gespraech

## Ausgangslage

Aus dem Kurzgespraech mit Henrik ist der Kernauftrag geklaert:

**Die Kanzlei will Claude DSGVO-konform nutzen. Schwaerzung reicht dafuer vollkommen.**

Das definiert den Use-Case: Dokumente so aufbereiten, dass sie nach Schwaerzung
bedenkenlos an Claude gehen koennen. Nicht Analyse, nicht eigenes LLM als Endprodukt —
sondern Schwaerzung als Enabler fuer Cloud-LLM-Nutzung.

Der Scope geht ueber PDFs hinaus. Die Kanzlei braucht breite Dokumentverarbeitungs-
Capabilities (OCR-Sonderfaelle, Rechnungen, Tabellen), die Algron bisher nicht hat.
Bisher existiert nur ein PoC fuer maschinell auslesbare PDFs.

## Was bereits geklaert ist

- **Haupt-Use-Case:** Schwaerzung/Redaktion. Ziel: Claude DSGVO-konform nutzbar machen. [W]
- **Fehlertoleranz:** Schwaerzung reicht — kein lueckenloser Audit-Trail noetig. [W]
- **Scope:** Multi-Format ist Teil des Kernproblems, kein Folgeprojekt. [W]
- **Status quo:** Nur maschinell auslesbare PDFs als PoC. Tausend Sonderfaelle offen. [W]
- **Tabellen/Rechnungen:** Vermutlich auch schwaerzen. Kein Blocker — muessen ohnehin erst eingelesen werden. [W]
- **Mimir-Haltung:** Henrik pragmatisch — guenstigste Loesung die funktioniert gewinnt. Mimir OK wenn noetig, aber kein Selbstzweck. [W]
- **Kostenmodell:** Kosten werden an die Kanzlei weitergereicht. Nicht Algrons Budget, sondern Kosten-Rechtfertigung gegenueber dem Kunden. [W]
- **Zeitrahmen:** Kein harter Liefertermin. Inkrementelle Lieferung, regelmaessig um Features erweitern. [W]
- **Endnutzer:** Kein Thema. Auftrag kommt vom Kanzlei-Chef, seine Wuensche sind relevant. Fragen gehen an ihn, nicht an Endnutzer. [W]

## Verbleibende Entscheidungspunkte

### 1. Mimir: Behalten oder ersetzen?

Henrik: Guenstigste Loesung die funktioniert. Kosten gehen an die Kanzlei, muessen
aber nachvollziehbar begruendet werden.

- **Option A: Mimir behalten** — GPU (~1000 EUR/Monat) weiter betreiben. Mimir fuer
  NER und Cleanup. Vorteil: Keine Daten verlassen das System, bereits funktionsfaehig.
  Nachteil: Moeglicherweise teurer als noetig fuer reinen Schwaerzungs-Use-Case.
- **Option B: Spezialisierte Pipeline** — Regex (IBAN, Aktenzeichen, Telefon) +
  Datenabgleich (Mandantenliste, Richterliste) + leichtgewichtiges NER (spaCy/Flair).
  Alles lokal, kein eigenes LLM. Vorteil: Deutlich guenstiger, weniger Komplexitaet.
  Nachteil: Moeglicherweise schlechtere Erkennung bei unstrukturierten Texten.
- **Option C: Hybrid** — Spezialisierte Pipeline als Default, Mimir als Fallback.

**Noetig um zu entscheiden:** Vergleichs-PoC — gleiche Dokumente durch Mimir-NER
und durch Regex+spaCy schicken, False-Negative-Rate vergleichen. Erst dann wissen
wir ob Option B funktioniert.

### 2. Dokumentverarbeitung: Prioritaeten

Alles muss eingelesen werden, bevor es geschwaerzt werden kann. Reihenfolge:

1. **Maschinell lesbare PDFs** — PoC existiert, bekannte Issues fixen. [Grundlage]
2. **OCR-Sonderfaelle** — Vektor-PDFs, Scans, gemischte Seiten. [Haeufig, blockiert Qualitaet]
3. **Tabellen in PDFs** — Struktur-Erhaltung fuer sinnvolle Schwaerzung. [Kanzlei-Signal]
4. **Rechnungen** — Vermutlich gleicher Schwaerzungs-Pfad. [Kanzlei-Signal]
5. **Weitere Formate** (Excel, Word, E-Mail) — [O] Noch nicht bestaetigt.

Frage an Kanzlei-Chef (via Henrik): Welche Dokumenttypen kommen am haeufigsten vor?
Das bestimmt die Reihenfolge der PoCs.

### 3. Technische Weiche: Python-Migration

Zwei bekannte Pipeline-Issues (Cleanup-Gate, OCR-Fehlzuendung) sind in C# loesbar,
aber aufwaendig. Python-Stack (PyMuPDF, pdfplumber) loest beide vermutlich mit und
bringt Tabellen-/Multi-Format-Support.

- **Option A: C# beibehalten** — Issues einzeln fixen, Pipeline bleibt homogen.
- **Option B: Extraktion nach Python** — Loest Issues, ermoeglicht Multi-Format.
  Architektur-Bruch, aber passt zum breiteren Scope.

Falls Mimir wegfaellt, wird der C#-Stack duenner — Python-Migration dann naheliegender.

## Noch offen — beim naechsten Henrik-Sync klaeren

1. **Volumen** — Dokumente pro Tag/Monat, Seitenanzahl. Viele Niederlassungen →
   moeglicherweise hoeher als gedacht. → Brauchen wir fuer Kosten-Rechtfertigung.
2. **Dokumenttypen-Verteilung** — Frage an Kanzlei-Chef: Wie viel Prozent sind
   maschinelle PDFs, Scans, Tabellen, Rechnungen, andere Formate?
   → Bestimmt PoC-Reihenfolge.

## Empfohlene naechste Schritte

Unabhaengig vom naechsten Henrik-Sync koennen wir jetzt starten:

1. `/research tech Regex+NER-Pipeline fuer PII-Schwaerzung Deutsch` — Was gibt es,
   was taugt fuer deutsche Rechtstexte?
2. `/poc PyMuPDF Textextraktion` — Loest der Python-Stack die bekannten PDF-Issues?
3. Danach: Vergleichs-PoC Mimir-NER vs. Regex+spaCy auf gleichen Dokumenten
   → Liefert Daten fuer Mimir-Entscheidung

## Was wir NICHT besprechen muessen

- **DSGVO-Grundprinzipien:** Lokal = sicher, Cloud nur nach Schwaerzung. Steht.
- **Team-Setup skadi-doku:** Agent-Team ist operativ.
- **Kanzlei-Kommunikation:** Henriks Kanal.
- **Claude-Analyse-Features:** Irrelevant — Schwaerzung kommt zuerst.
- **Endnutzer-Feedback:** Auftrag kommt vom Chef, nicht von Endnutzern.
