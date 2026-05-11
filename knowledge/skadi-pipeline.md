# Skadi Pipeline — C#-Architektur

Stand: 2026-05-11 (aus handoff-context.md extrahiert)

## Repo-Layout

```
skadi/
├── DataExtractorHybrid/
│   └── WDM Eingabemaske/          # WPF Windows-Client
│       ├── Services/Mimir/
│       │   ├── PdfTextExtractor.cs          # iText + OCR-Fallback
│       │   ├── ChatService.cs
│       │   └── ...
│       └── UserInterface/Mimir/
│           ├── MimirChatTab.xaml(.cs)
│           ├── MimirChatViewModel.cs
│           ├── BatchPreviewDialog.xaml(.cs)  # Testmodus, kein Claude
│           └── BatchPreviewDialogViewModel.cs
├── SkadiService/
│   ├── SkadiServiceCore/Services/Redaction/
│   │   ├── MimirTextCleanupService.cs    # Pass B Word-Boundary-Cleanup
│   │   ├── RedactionService.cs
│   │   └── MimirNerService.cs
│   └── SkadiWeb/
│       ├── Controllers/DocumentAnalysisController.cs
│       └── NLog.config                   # Fallback — live Config vom Netzwerk-Share
└── docs/specs/                           # historische Specs + Handoffs
```

## Pipeline-Fluss

WDM-Client → SkadiWeb HTTP API → Mimir (lokal) + Claude (cloud)

### Client-Side

1. **PDF-Extraktion** — `PdfTextExtractor.ExtractAsync`: iText dual-strategy, OCR-Fallback bei <10 Alpha-Chars/Seite
2. **API-Aufruf** — POST an `/Documents/Analyze` oder `/Documents/PreviewRedaction`
3. **Antwort-Rendering** — Chat-Bubble; [DOC]-Marker loest "Als Word speichern" aus
4. **Word-Export** — POST an `/Documents/ExportWord`

### Server-Side: `Analyze` (voller Pfad mit Claude)

1. Cleanup: `MimirTextCleanupService.CleanupAsync` (Pass B)
2. Redact Loop: `RedactionService` (klassisches PII) + `MimirNerService` (NER: Namen, Adressen, Org, DE-Identifier)
3. Truncation bei Uebergroe
4. Claude-Aufruf mit `cache_control: ephemeral` fuer Docs >= `MinCacheableDocChars`
5. Retry ohne cache_control bei `ClaudeValidationException`
6. Audit-Row in MySQL `log_service` via NLog-Logger `Skadi.DocumentAnalysisAudit`

### Server-Side: `PreviewRedaction` (kein Claude)

Gleicher Cleanup + Redact-Pfad. **Kein Audit-Log** (nur `Logger.Info`).

## Decision-Gates

| Gate | Datei | Schwellwert | Status |
|------|-------|-------------|--------|
| File-Size-Limit | PdfTextExtractor | 20 MB | Settled |
| OCR-Trigger | PdfTextExtractor.MinAlphaCharsForTextPage | 10 Alpha-Chars | **Verdaechtig — Issue 2** |
| OCR-Timeout | PdfTextExtractor.OcrPageTimeout | 30s | Bumped von 15s |
| Strategy-Picker | ExtractPageWithBestStrategy | Letter→Space-Transitions | Gefixt in 406b4fce9 |
| Cleanup-Density-Gate | MimirTextCleanupService.WhitespaceDensityThreshold | 0.05 | **5% zu niedrig — Issue 1** |
| Cleanup-Input-Cap | MaxCleanupInputChars | 30.000 Chars | Settled |
| Cleanup-Output-Cap | MaxOutputTokens | 8192 | Bumped von 2048 |
| Debug-Bypass | AlwaysInvokeCleanup | true | **Aktuell aktiv — muss zurueckgesetzt werden** |

## Bekannte Issues

### Issue 1 — Cleanup-Gate-Schwellwert

**Problem:** `WhitespaceDensityThreshold = 0.05` (5%) liegt unter realem Wert (7-9% bei normalen Docs).
Gate-Bypass `AlwaysInvokeCleanup = true` aktuell aktiv.

**Optionen:**
- Quick-Fix: Schwellwert auf 0.12 anheben
- Better-Fix: Metrik tauschen — Median-Token-Laenge > 15 Zeichen statt Dichte-Heuristik
  (Median ist robuster: normale Prosa Median ~5-7, zusammengewuerschelter Text Median 25+)

### Issue 2 — OCR-Fehlzuendung auf Vektor-PDFs

**Problem:** iText liefert 0 Alpha-Chars bei manchen Vektor-PDFs trotz sichtbarem Text
→ OCR-Fallback → Tesseract Buchstaben-Substitutionen (p→z, c→d etc.)
→ Sanity-Check verwirft Korrekturen, aber Source-Text in Redaction-Pipeline bleibt korrumpiert.

**Root-Cause-Kandidaten:** Custom CMap, Font-Subsetting mit nicht-standard Glyph-IDs, Encrypted Fonts, PDFSharp-Quirks.

**Strategische Frage:** Vor C#-Debugging pruefen ob Python-Migration (PyMuPDF/pdfplumber)
das Problem automatisch loest. Python-PDF-Stack behandelt Font-Encoding-Edge-Cases deutlich besser.

## Pitfalls

### NLog-using-Stripping

IDE entfernt `using NLog;` automatisch (Linter sieht namespace nicht als "benutzt").
**Fix:** NLog vollqualifiziert angeben:
```csharp
private static readonly NLog.Logger Logger = NLog.LogManager.GetCurrentClassLogger();
```

### Audit-Logging-Asymmetrie

`Analyze` schreibt strukturierten Audit-Row. `PreviewRedaction` schreibt nur `Logger.Info`.
Wer in der Audit-DB nach `cleanupInvoked` sucht und BatchPreview nutzt, findet nichts.

### NLog-Config-Share

Live-Config von `\\fs03.voigt.local\...\global_config\skadi_service_nlog.config`.
In-Repo `NLog.config` = Fallback. MySQL-Target: `voigt-user-settings.log_service` auf `10.0.0.31`.

### Test-Server-Pipeline

Test-Server deployed von Branch `feature/mimir-demo-claude-only-ocr`.
Live-Server laeuft `main` (ohne Cleanup/Audit/Word-Export).
In Logs: `Version`-Spalte enthaelt CommitSha.

## Konfigurationskonstanten

`MimirTextCleanupService.cs`: WhitespaceDensityThreshold=0.05 | MinTextLengthForCleanup=50 |
MaxCleanupInputChars=30.000 | MaxOutputTokens=8192 | MaxLengthExpansionRatio=1.30 |
MaxCorrectionsPerDocument=100 | MinOriginalLength=6 | **AlwaysInvokeCleanup=true** (DEBUG)

`PdfTextExtractor.cs`: MaxBytes=20MB | OcrPageTimeout=30s | **MinAlphaCharsForTextPage=10** (verdaechtig)
