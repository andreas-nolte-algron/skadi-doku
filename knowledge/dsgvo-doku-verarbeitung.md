# DSGVO-konforme Doku-Verarbeitung — Grundregeln

Stand: 2026-05-11 (Skeleton — Team baut auf)

## Kernprinzip: Lokal vs. Cloud

**[W] Lokal ist sicher:** Mimir laeuft auf eigener GPU-Instanz. Keine Daten verlassen das System.
**[W] Cloud-Tools (Claude/ChatGPT) sind verboten fuer sensitive Daten.** Erst nach Redaktion zugelassen.
**[A]** Redaktionierte Texte duerfen zu Claude — aber "vollstaendig redaktioniert" muss nachweisbar sein.

## Anwaltsgeheimnis (§ 203 StGB)

**[W]** Anwaelte unterliegen beruflichem Geheimnis. Mandantendaten sind besonders schutzwuerdig.
**[O]** Welche Datenkategorien kommen vor? (Namen, Adressen, Aktenzeichen, Bankdaten, Gesundheitsdaten?)
**[O]** Gibt es interne Richtlinien der Kanzlei fuer Cloud-Nutzung?

## Auftragsverarbeitung (Art. 28 DSGVO)

**[A]** Bei externem Dienstleister (Algron) braucht die Kanzlei einen Auftragsverarbeitungsvertrag (AVV).
**[O]** Liegt ein AVV zwischen Kanzlei und Algron vor?
**[O]** Welche Rechenzentrumsstandorte sind akzeptabel? (EU-only?)

## Was darf wohin

| Daten-Typ | Lokal (Mimir) | Nach Redaktion zu Claude | Direkt zu Claude |
|-----------|:---:|:---:|:---:|
| Rohe Mandanten-Dokumente | Ja | Nein | Nein |
| Redaktionierte Texte | Ja | Ja [A] | Nein |
| Anonymisierte Analysen | Ja | Ja | Ja [A] |
| Struktur-Fragen (kein Inhalt) | Ja | Ja | Ja |

Legende: [A] = Annahme, noch nicht verifiziert

## Redaktions-Vollstaendigkeit

Kernfrage: Wie beweisbar ist "vollstaendig redaktioniert"?

- Aktuelle Pipeline: `RedactionService` (regex-basiert) + `MimirNerService` (NER)
- **[O]** Gibt es False-Negative-Rate aus Tests?
- **[O]** Welche PII-Kategorien muessen sicher erkannt werden? (Name, Adresse, IBAN, Aktenzeichen, Datum, Richter?)
- **[O]** Reicht "best effort" oder braucht die Kanzlei Audit-Trail pro Redaktion?

## Offene Rechts-Fragen (Team klaert nicht allein)

Diese Fragen brauchen entweder Henriks Input oder externen Datenschutz-Rat:
- Darf pseudonymisierter Text (Aktenzeichen durch Kuerzel ersetzt) als "nicht sensitiv" behandelt werden?
- Wie lange duerfen Audit-Logs gespeichert werden?
- Loeschkonzept fuer verarbeitete Dokumente?

---

*Weitere Knowledge-Files entstehen organisch: ner-landschaft-de.md, ocr-optionen.md,
pdf-extraction.md, kosten-compute.md, anwaltliche-doku-workflows.md*
