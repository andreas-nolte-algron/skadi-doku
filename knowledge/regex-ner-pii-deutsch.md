# Research: Regex+NER-Pipeline fuer PII-Schwaerzung Deutsch (tech)
Datum: 2026-05-11

## Zusammenfassung

Fuer deutsche PII-Erkennung existieren drei Architektur-Ebenen: (1) Regex fuer strukturierte Patterns (IBAN, Telefon, PLZ), (2) NER-Modelle fuer unstrukturierte Entities (Namen, Orte, Organisationen), (3) Orchestrierungs-Frameworks die beides kombinieren. **[W]** Presidio (Microsoft) ist das reifste Open-Source-Framework mit German-Support **[A]**, erfordert aber Konfiguration. **[W]** spaCy und Flair bieten beste deutsche NER-Modelle. **[O]** Mimir-NER-Qualitaet im Vergleich zu spaCy/Flair noch nicht evaluiert. **[O]** False-Negative-Rate aktueller Pipeline unbekannt.

## Ergebnisse

### Orchestrierungs-Frameworks

| Option | Capability [W/A/O] | DSGVO-Eignung [W/A/O] | Kosten-Indikator [W/A/O] | Quellen |
|--------|-------------------|----------------------|--------------------------|---------|
| **Presidio** (Microsoft) | [W] Kombiniert Regex + NER + Context-Scoring. [A] German-Support via spaCy/Stanza-Integration. [W] Erweiterbar via Custom-Recognizers. | [W] Lokal deploybar (Python). [W] Keine Cloud-Abhaengigkeit. [A] Wird von MS als PII-Redaction-Loesung aktiv maintained. | [W] Open Source (MIT). [A] Runtime: CPU-only moeglich, GPU optional fuer NER-Beschleunigung. | [1] [2] [3] [4] |
| **piisa/pii-extract-plg-regex** | [W] Regex-only, strukturiert nach Land/Sprache. [O] German-Coverage unklar (Repo zeigt Beispiele fuer EU). [W] Modulare Plugin-Architektur. | [W] Lokal deploybar (Python). [W] Open Source. | [W] Open Source. [W] Keine ML-Abhaengigkeit → sehr leichtgewichtig. | [5] [6] |
| **Custom Pipeline** (wie aktuell in Skadi) | [W] Volle Kontrolle. [O] Maintainability abhaengig von internem Know-how. | [W] Lokal. [W] Volle Kontrolle ueber Datenfluss. | [A] Entwicklungszeit hoch bei Feature-Erweiterungen. [W] Keine Lizenzkosten. | Aktuelle Skadi-Implementierung |

### NER-Modelle (Named Entity Recognition)

| Option | Capability [W/A/O] | DSGVO-Eignung [W/A/O] | Kosten-Indikator [W/A/O] | Quellen |
|--------|-------------------|----------------------|--------------------------|---------|
| **spaCy de_core_news_lg** | [W] Erkennt PER, LOC, ORG, MISC. [W] Schnell (Transformer-basiert optional). [A] F1-Score ~85-90% auf deutschen Benchmark-Datasets. [O] Performance auf Anwaltsdokumenten ungetestet. | [W] Lokal deploybar. [W] Open Source (MIT). [W] Offline nutzbar. | [W] Open Source. [A] CPU: ~50-200 Docs/Sek (abhaengig von Laenge). [A] GPU optional fuer Transformer-Pipelines. | Allgemeinwissen + [7] |
| **Flair NER-German** | [W] Erkennt PER, LOC, ORG, MISC. [W] State-of-the-art Accuracy fuer Deutsch (F1 ~92%). [O] Langsamer als spaCy (Contextual String Embeddings). | [W] Lokal deploybar. [W] Open Source (MIT). [W] Offline nutzbar. | [W] Open Source. [A] CPU: ~10-50 Docs/Sek. [A] GPU empfohlen fuer Production. | Allgemeinwissen |
| **Stanza (Stanford NLP)** | [W] Multi-Language, inkl. Deutsch. [A] Accuracy aehnlich spaCy. [O] Weniger verbreitet als spaCy/Flair in deutscher PII-Community. | [W] Lokal deploybar. [W] Open Source (Apache 2.0). [W] Offline nutzbar. | [W] Open Source. [A] Performance aehnlich spaCy. | Allgemeinwissen + [2] |
| **Mimir (aktuell)** | [O] Capability im Vergleich zu spaCy/Flair unklar. [O] Welche Entity-Types werden erkannt? [O] False-Negative-Rate? | [W] Bereits deployed + lokal. [W] Volle Kontrolle. | [W] Bereits bezahlt/deployed. [O] Wartungsaufwand? | Skadi-Pipeline |

### Regex-Patterns fuer deutsche PII

| PII-Typ | Regex-Complexity [W/A/O] | False-Positive-Risk [W/A/O] | Quellen |
|---------|-------------------------|----------------------------|---------|
| **IBAN (Deutsch)** | [W] DE + 20 Digits mit Checksumme validierbar. Pattern: `DE\d{2}[\s]?\d{4}[\s]?\d{4}[\s]?\d{4}[\s]?\d{4}[\s]?\d{2}` | [W] Niedrig bei Checksummen-Validierung. [A] Mittel ohne Checksumme (22-stellige Zahlenfolgen selten in Fliesstext). | [8] |
| **Telefonnummern (DE)** | [W] Pattern fuer +49, 0049, lokale Vorwahlen. [A] Hohe Varianz (Leerzeichen, Bindestriche, Klammern). | [A] Mittel-hoch ohne Kontext (z.B. "Raum 030 1234" vs. Telefonnummer). | [6] |
| **PLZ + Ort** | [W] Pattern: `\d{5}\s+[A-Za-zäöüÄÖÜß\s]{2,35}`. [W] 5-stellige PLZ eindeutig fuer Deutschland. | [W] Niedrig (5-stellige Zahl + Stadt-Name-Pattern robust). | [9] [10] [11] |
| **Strasse + Hausnummer** | [A] Pattern komplex: Strassenname (mit ae/oe/ue, "straße"/"str."/"Allee" etc.) + Hausnummer + ggf. Zusatz. Beispiel: `^(.*?)(?:\s+(\d+[a-z]?))` | [A] Mittel (viele Variations, z.B. "Am Ring 5a" vs. "Berliner Str. 123"). | [9] [12] |
| **Aktenzeichen** | [O] Kanzlei-spezifisches Format? [A] Typisch: `\d+ [A-Z]+ \d+/\d+` (z.B. "12 O 34/25"). [O] Voigt-Format unbekannt. | [O] Unbekannt ohne Kanzlei-Input. | - |
| **Datum (DE-Format)** | [W] Pattern: `\d{1,2}\.\d{1,2}\.\d{4}` oder `\d{1,2}\.\d{1,2}\.\d{2}`. [W] Einfach. | [A] Mittel-hoch ohne Kontext (z.B. Versionsnummern "1.2.2024" als False Positive). | Standard |
| **E-Mail** | [W] Standard-Pattern: `[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}`. | [W] Niedrig (E-Mail-Format eindeutig). | [6] |
| **Namen (Anwalts-Kontext)** | [W] Pattern fuer "Rechtsanwalt [Dr./Prof.] [Name]", "Prozessbevollmächtigter [Name]", "Herr/Frau [Name]". Siehe PoC `spacy_ner_hybrid.py`. | [W] Niedrig bei konservativen Patterns (nur nach Berufsbezeichnungen). [A] False-Negative-Rate 0% in PoC-Tests. | PoC 2026-05-12 |

## Annahmen die noch geklaert werden muessen

- [O] Wie gut ist Mimir-NER im Vergleich zu spaCy/Flair? (False-Negative-Rate, Entity-Types, Speed)
  - **Update 2026-05-12:** spaCy-PoC abgeschlossen (siehe `poc-spacy-ner-2026-05-12.md`)
  - **Ergebnis:** spaCy de_core_news_lg allein 82.35% Recall | Hybrid (spaCy + Regex) 100% Recall
  - **Naechster Schritt:** Gleicher Test gegen Mimir-NER
- [O] Welche PII-Kategorien sind Pflicht fuer die Kanzlei? (IBAN, Aktenzeichen, Richternamen, Gesundheitsdaten?)
- [O] Liegt Benchmark-Testset mit realen Anwaltsdokumenten vor?
- [O] Aktenzeichen-Format der Kanzlei Voigt?
- [O] Ist Context-Scoring (wie in Presidio) gewuenscht? (z.B. "Name: Müller" hoehere Confidence als isoliertes "Müller")
- [O] Performance-Anforderung: Wie viele Docs/Stunde muessen verarbeitet werden?
- [O] Gibt es eine definierte False-Negative-Toleranz? (0.1%? 1%? 5%?)

## Technische Architektur-Optionen

### Option A: Presidio-Integration (Empfehlung fuer Neuaufbau)

**Pro:**
- [W] Aktiv maintained (Microsoft).
- [W] Kombiniert Regex + NER + Context-Scoring out-of-the-box.
- [W] Erweiterbar via Custom-Recognizers (z.B. Aktenzeichen).
- [A] German-Support via spaCy/Flair-Integration dokumentiert.
- [W] Python → passt zu PoC-Pipeline, aber nicht zu C#-Stack.

**Contra:**
- [A] Migration von C# zu Python oder .NET-Wrapper noetig.
- [O] Performance-Overhead durch Framework-Layer?

**Deployment:** Python-Service neben SkadiWeb oder als Ersatz fuer MimirNerService.

### Option B: Hybrid (Regex in C# + Mimir-NER beibehalten)

**Pro:**
- [W] Minimale Architektur-Aenderung.
- [W] Regex-Patterns in C# implementierbar (siehe aktuelle RedactionService).
- [W] Mimir bereits deployed.

**Contra:**
- [O] Mimir-Qualitaet ungetestet vs. spaCy/Flair.
- [A] Kein Context-Scoring (nur Pattern-Match + NER-Entity-List).
- [A] Maintainability: Custom-Code statt Framework.

**Deployment:** Erweitere `RedactionService` um deutsche Regex-Patterns aus Tabelle oben.

### Option C: spaCy/Flair-NER + Regex-Custom-Pipeline (Python)

**Pro:**
- [W] State-of-the-art NER-Qualitaet (Flair F1 ~92%).
- [W] Volle Kontrolle ueber Pipeline-Logic.
- [W] Python-Oekosystem fuer NLP ausgereifter als C#.

**Contra:**
- [A] Mehr Entwicklungsaufwand als Presidio.
- [A] Keine Context-Scoring-Logic out-of-the-box.

**Deployment:** Python-Microservice neben SkadiWeb oder als Ersatz fuer MimirNerService.

## Empfehlung / naechster Schritt

**Empfehlung:**

1. **Benchmark Mimir-NER vs. spaCy de_core_news_lg** via `/poc` auf Skadi-Test-PDFs.
   - Metriken: False-Negative-Rate fuer Namen/Adressen/Orgs, Processing-Speed.
   - Falls Mimir >= spaCy: **Option B** (Regex erweitern, Mimir beibehalten).
   - Falls Mimir < spaCy: **Option C oder A** (Python-Migration).

2. **Regex-Pattern-PoC** fuer IBAN/PLZ/Telefon/E-Mail in C# (erweitere RedactionService).
   - Test gegen 50 Skadi-Docs: False-Positive/False-Negative-Rate messen.

3. **Klaere mit Henrik:**
   - Welche PII-Kategorien sind Pflicht? (siehe Annahmen oben)
   - Gibt es Aktenzeichen-Format-Spec?
   - False-Negative-Toleranz?

4. **Falls Presidio-Interesse:** PoC mit Presidio + spaCy de_core_news_lg gegen gleiche 50 Docs.

**Naechster Skill-Aufruf:** `/poc spaCy de_core_news_lg NER Deutsch` + `/poc Presidio German PII Detection`.

---

## Quellen

1. [Multi-language support - Microsoft Presidio](https://microsoft.github.io/presidio/analyzer/languages/)
2. [Additional models/languages - Microsoft Presidio](https://microsoft.github.io/presidio/tutorial/05_languages/)
3. [Custom Pattern Recognizer Not Working Properly with German Language in Analyzer Engine · Issue #1343](https://github.com/microsoft/presidio/issues/1343)
4. [presidio-analyzer · PyPI](https://pypi.org/project/presidio-analyzer/)
5. [GitHub - piisa/pii-extract-plg-regex](https://github.com/piisa/pii-extract-plg-regex)
6. [Regular Expressions used in PII Scanning · PII Crawler Blog](https://www.piicrawler.com/blog/regular-expressions-used-in-pii-scanning/)
7. [Using NLP and Pattern Matching to Detect, Assess, and Redact PII in Logs - Part 2 — Elastic Observability Labs](https://www.elastic.co/observability-labs/blog/pii-ner-regex-assess-redact-part-2)
8. [Extract German Address and IBAN in Python - Regex Generator](https://www.easyregex.com/regex/b5241b8710d2073a2f00750a07850e4d)
9. [How to Use Regex to Split a German Address into Its Components - CodingTechRoom](https://codingtechroom.com/question/-regex-split-german-address)
10. [Postal Code > Germany | Regex DB](https://rgxdb.com/r/373ICO02)
11. [German City and Postal Code Regex - CodePal](https://codepal.ai/regex-generator/query/iV9pKSfr/german-city-postal-code-regex)
12. [Regex for German street names - Regular Expressions](https://gist.github.com/0OZ/447ecddcbbe8e9bef546701822fb8cde)
