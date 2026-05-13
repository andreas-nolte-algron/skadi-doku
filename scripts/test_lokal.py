#!/usr/bin/env python3
"""
Lokaler Validierungs-Test: PDF -> Schwaerzung (Presidio-basiert)
Fuer manuelle Pruefung mit echten Kanzlei-Dokumenten (lokal, kein Cloud-Zugriff).

SETUP (einmalig):
    pip install pymupdf presidio-analyzer presidio-anonymizer spacy
    python3 -m spacy download de_core_news_lg
    # Fuer OCR (gescannte PDFs):
    # Linux: sudo apt install tesseract-ocr tesseract-ocr-deu
    # Mac:   brew install tesseract tesseract-lang

USAGE:
    python3 test_lokal.py dokument.pdf
    python3 test_lokal.py dokument.pdf --format txt
    python3 test_lokal.py dokument.pdf --output eigener_name.html
    python3 test_lokal.py dokument.pdf --volltext

Output-Datei wird automatisch gespeichert als:
    dokument_geschwärzt_20260512_143022.html  (im gleichen Ordner wie die PDF)
"""

import sys
import os
import html as html_mod
import argparse
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple


# ──────────────────────────────────────────────
# Dependency-Checks
# ──────────────────────────────────────────────

def check_dependencies():
    missing = []
    try:
        import pymupdf
    except ImportError:
        missing.append("pymupdf  →  pip install pymupdf")
    try:
        import spacy
        try:
            spacy.load("de_core_news_lg")
        except OSError:
            missing.append("spaCy-Modell  →  python3 -m spacy download de_core_news_lg")
    except ImportError:
        missing.append("spacy  →  pip install spacy && python3 -m spacy download de_core_news_lg")
    try:
        import presidio_analyzer
    except ImportError:
        missing.append("presidio-analyzer  →  pip install presidio-analyzer")
    try:
        import presidio_anonymizer
    except ImportError:
        missing.append("presidio-anonymizer  →  pip install presidio-anonymizer")
    if missing:
        print("FEHLT:")
        for m in missing:
            print(f"  {m}")
        sys.exit(1)

if __name__ == "__main__":
    check_dependencies()

import pymupdf
from presidio_analyzer import AnalyzerEngine, PatternRecognizer, Pattern
from presidio_analyzer.nlp_engine import NlpEngineProvider


# ──────────────────────────────────────────────
# Textextraktion: digital oder gescannt
# ──────────────────────────────────────────────

def extract_text_from_pdf(pdf_path: str) -> Tuple[str, List[Dict]]:
    """
    Extrahiert Text seitenweise. Gescannte Seiten werden via OCR verarbeitet.

    Returns:
        (gesamttext, seiten_infos)
    """
    doc = pymupdf.open(pdf_path)
    full_text = ""
    pages_info = []

    for page_num, page in enumerate(doc, 1):
        direct_text = page.get_text()
        alpha_count = sum(1 for c in direct_text if c.isalpha())

        if alpha_count >= 10:
            page_text = direct_text
            method = "direkt"
            ocr_used = False
        else:
            ocr_used = True
            try:
                tp = page.get_textpage_ocr(language="deu", dpi=300, full=True)
                page_text = page.get_text(textpage=tp)
                method = "OCR (Tesseract)"
                if len(page_text.strip()) < 20:
                    method = "OCR (wenig Text - Scan-Qualitaet pruefen!)"
            except Exception as e:
                page_text = ""
                method = f"OCR fehlgeschlagen: {e}"
                print(f"\n[!] Seite {page_num}: OCR fehlgeschlagen.")
                print(f"    Tesseract installiert? sudo apt install tesseract-ocr tesseract-ocr-deu")
                print(f"    Fehler: {e}")

        pages_info.append({
            "seite": page_num,
            "methode": method,
            "zeichen": len(page_text),
            "alpha": sum(1 for c in page_text if c.isalpha()),
            "ocr": ocr_used
        })
        full_text += page_text + "\n"

    doc.close()
    return full_text, pages_info


# ──────────────────────────────────────────────
# Presidio: Analyzer mit deutschen Custom-Recognizern
# ──────────────────────────────────────────────

def create_analyzer() -> AnalyzerEngine:
    """
    Erstellt Presidio AnalyzerEngine mit deutschem spaCy-Modell
    und Kanzlei-spezifischen Custom-Recognizern.
    """
    # spaCy-Modell fuer Deutsch konfigurieren
    provider = NlpEngineProvider(nlp_configuration={
        "nlp_engine_name": "spacy",
        "models": [{"lang_code": "de", "model_name": "de_core_news_lg"}],
    })
    nlp_engine = provider.create_engine()

    analyzer = AnalyzerEngine(
        nlp_engine=nlp_engine,
        supported_languages=["de"],
    )

    # ── Custom Recognizer: KFZ-Kennzeichen ──
    analyzer.registry.add_recognizer(PatternRecognizer(
        supported_entity="KFZ_KENNZEICHEN",
        supported_language="de",
        patterns=[
            Pattern("kfz_standard", r"\b[A-ZÄÖÜ]{1,3}[\s\-][A-Z]{1,2}[\s\-]?\d{1,4}(?:\s?[HE])?\b", 0.7),
        ],
        context=["kennzeichen", "kfz", "amtl", "fahrzeug", "pkw", "lkw"],
    ))

    # ── Custom Recognizer: Handelsregister ──
    analyzer.registry.add_recognizer(PatternRecognizer(
        supported_entity="HANDELSREGISTER",
        supported_language="de",
        patterns=[
            Pattern("hrb", r"\bHR[AB]\s?\d{3,8}(?:\s?[A-Z])?\b", 0.85),
        ],
        context=["handelsregister", "registergericht", "amtsgericht", "eingetragen"],
    ))

    # ── Custom Recognizer: USt-IdNr ──
    analyzer.registry.add_recognizer(PatternRecognizer(
        supported_entity="UST_IDNR",
        supported_language="de",
        patterns=[
            Pattern("ust_id", r"\bDE\s?\d{9}\b", 0.9),
        ],
        context=["ust", "umsatzsteuer", "steuernummer", "steuer-id", "idnr"],
    ))

    # ── Custom Recognizer: Postfach ──
    analyzer.registry.add_recognizer(PatternRecognizer(
        supported_entity="POSTFACH",
        supported_language="de",
        patterns=[
            Pattern("postfach", r"\bPostfach\s+\d[\d\s]*\d\b", 0.9),
        ],
    ))

    # ── Custom Recognizer: Aktenzeichen ──
    analyzer.registry.add_recognizer(PatternRecognizer(
        supported_entity="AKTENZEICHEN",
        supported_language="de",
        patterns=[
            Pattern("az_gericht", r"\b\d{1,4}\s+[A-Z]{1,3}\s+\d+/\d{2,4}\b", 0.8),
            Pattern("az_kurz", r"\b[A-Z]{1,3}\s+\d+/\d{2,4}(?:/\d+)?\b", 0.6),
        ],
        context=["aktenzeichen", "az", "geschaeftsnummer", "verfahren"],
    ))

    # ── Custom Recognizer: Schaden-Nr / Referenznummern ──
    analyzer.registry.add_recognizer(PatternRecognizer(
        supported_entity="REFERENZNR",
        supported_language="de",
        patterns=[
            # Labelled: "Schaden-Nr.: 12345" etc.
            Pattern("ref_labelled",
                    r"(?:Schaden[s\-]?(?:Nr|Nummer|nr)\.?|Unser\s+Zeichen|Ihr\s+Zeichen|"
                    r"Vorgangs[_\-]?(?:Nr|Nummer|nr)\.?|Kfz[\-.]?Haftpflicht[\-.]?Schaden[\-.]?Nr\.?)"
                    r"[\s.:]+([A-Za-z0-9][\w\s/\-.:]{2,25})",
                    0.85),
            # Nummernfolge mit Slashes: 123/456/789
            Pattern("ref_slashes", r"\b\d{1,10}/\d{1,10}(?:/\d{1,10})+\b", 0.5),
        ],
        context=["schaden", "vorgang", "zeichen", "nummer", "versicherung", "haftpflicht"],
    ))

    # ── Custom Recognizer: Versicherungsnummer ──
    analyzer.registry.add_recognizer(PatternRecognizer(
        supported_entity="VERSICHERUNGSNR",
        supported_language="de",
        patterns=[
            Pattern("vers_nr",
                    r"(?:Versicherungs(?:nummer|nr\.|schein)|Vers[\.\-]?Nr\.?|"
                    r"Police[\-.\s:]?Nr\.?|Polizze[\-.\s:]?Nr\.?)"
                    r"[\s.:]*(\w{4,20})",
                    0.85),
        ],
        context=["versicherung", "police", "schein", "vertrag"],
    ))

    # ── Custom Recognizer: Geburtsdatum ──
    analyzer.registry.add_recognizer(PatternRecognizer(
        supported_entity="GEBURTSDATUM",
        supported_language="de",
        patterns=[
            Pattern("geb_datum",
                    r"(?:geb(?:oren|\.)?|Geburtsdatum|geboren\s+am)[\s.:]*\d{1,2}\.\s?\d{1,2}\.\s?\d{2,4}",
                    0.9),
        ],
    ))

    # ── Custom Recognizer: Adressen (Strasse + Hausnummer) ──
    analyzer.registry.add_recognizer(PatternRecognizer(
        supported_entity="ADRESSE",
        supported_language="de",
        patterns=[
            Pattern("strasse_nr",
                    r"\b[A-ZÄÖÜ][a-zäöüß]+(?:straße|str\.|gasse|weg|allee|platz|ring|damm|ufer|chaussee)\s+\d+\s?[a-zA-Z]?\b",
                    0.7),
            Pattern("strasse_2wort",
                    r"\b[A-ZÄÖÜ][a-zäöüß]+\s[A-ZÄÖÜ][a-zäöüß]+(?:straße|str\.|gasse|weg|allee|platz|ring)\s+\d+\s?[a-zA-Z]?\b",
                    0.7),
        ],
        context=["wohnhaft", "anschrift", "adresse", "strasse", "straße"],
    ))

    # ── Custom Recognizer: PLZ + Ort ──
    analyzer.registry.add_recognizer(PatternRecognizer(
        supported_entity="PLZ_ORT",
        supported_language="de",
        patterns=[
            Pattern("plz_ort", r"\b\d{5}\s+[A-ZÄÖÜ][a-zäöüß]+(?:\s[A-ZÄÖÜ][a-zäöüß]+)?\b", 0.5),
        ],
        context=["wohnhaft", "anschrift", "adresse", "postleitzahl", "plz"],
    ))

    return analyzer


def detect_pii(text: str, analyzer: AnalyzerEngine, score_threshold: float = 0.5) -> List[Dict]:
    """
    Erkennt PII via Presidio (NER + Pattern + Context-Scoring).
    Gibt sortierte Entity-Liste zurueck, kompatibel mit HTML-Output.
    """
    results = analyzer.analyze(
        text=text,
        language="de",
        score_threshold=score_threshold,
    )

    entities = []
    for r in results:
        entities.append({
            "text": text[r.start:r.end],
            "start": r.start,
            "end": r.end,
            "typ": r.entity_type,
            "quelle": f"presidio ({r.score:.0%})",
        })

    # Sortieren nach Position
    entities.sort(key=lambda x: x["start"])

    # Overlaps entfernen: bei Ueberlappung hoeheren Score behalten
    merged = []
    for ent in entities:
        overlap = False
        for i, existing in enumerate(merged):
            if ent["start"] < existing["end"] and ent["end"] > existing["start"]:
                overlap = True
                # Laengeren/hoeherwertigen behalten
                if len(ent["text"]) > len(existing["text"]):
                    merged[i] = ent
                break
        if not overlap:
            merged.append(ent)

    merged.sort(key=lambda x: x["start"])
    return merged


def entity_context(text: str, ent: Dict, window: int = 60) -> str:
    """Zeigt Entity mit Kontext-Fenster links/rechts."""
    start = max(0, ent["start"] - window)
    end = min(len(text), ent["end"] + window)
    pre = text[start:ent["start"]].replace("\n", " ")
    match = text[ent["start"]:ent["end"]]
    post = text[ent["end"]:end].replace("\n", " ")
    prefix = "..." if start > 0 else ""
    suffix = "..." if end < len(text) else ""
    return f'{prefix}{pre}[>>>{match}<<<]{post}{suffix}'


def redact_text(text: str, entities: List[Dict]) -> str:
    """Ersetzt erkannte Entities durch [GESCHWÄRZT]."""
    result = text
    for ent in sorted(entities, key=lambda x: x["start"], reverse=True):
        result = result[:ent["start"]] + "[GESCHWÄRZT]" + result[ent["end"]:]
    return result


def generate_html(text: str, entities: List[Dict], pages_info: List[Dict], pdf_name: str) -> str:
    """
    Erzeugt HTML mit geschwärzten Stellen als schwarze Balken.
    Hover zeigt PII-Kategorie + Confidence (nicht den Originalwert).
    """
    segments = []
    cursor = 0
    for ent in sorted(entities, key=lambda x: x["start"]):
        if cursor < ent["start"]:
            segments.append(("text", text[cursor:ent["start"]]))
        segments.append(("entity", ent["text"], ent["typ"], ent["quelle"]))
        cursor = ent["end"]
    if cursor < len(text):
        segments.append(("text", text[cursor:]))

    body_parts = []
    for seg in segments:
        if seg[0] == "text":
            escaped = html_mod.escape(seg[1])
            escaped = escaped.replace("\n", "<br>\n")
            body_parts.append(escaped)
        else:
            _, original, typ, quelle = seg
            bar_len = max(4, len(original))
            bars = "\u2588" * bar_len
            body_parts.append(
                f'<span class="redacted" title="{html_mod.escape(typ)} [{html_mod.escape(quelle)}]">{bars}</span>'
            )

    ocr_count = sum(1 for p in pages_info if p["ocr"])
    typ_counts = {}
    for ent in entities:
        typ_counts[ent["typ"]] = typ_counts.get(ent["typ"], 0) + 1
    typ_summary = " &nbsp;|&nbsp; ".join(f"{t}: {n}" for t, n in sorted(typ_counts.items()))

    return _html_wrapper(
        title=f"Geschwaerzt: {html_mod.escape(pdf_name)}",
        summary_html=f"""<strong>{len(entities)} PII-Entities geschwaerzt</strong>
    &nbsp;|&nbsp; {len(pages_info)} Seiten ({ocr_count} via OCR)
    {"&nbsp;|&nbsp; " + typ_summary if typ_summary else ""}""",
        body_html="".join(body_parts),
        legend="Schwarze Balken = geschwaerzte PII. Maus drueberhalten zeigt Kategorie + Confidence.",
        extra_css=""".redacted {
      background: #111;
      color: #111;
      border-radius: 2px;
      padding: 1px 3px;
      letter-spacing: 1px;
      cursor: help;
      font-family: monospace;
    }
    .redacted:hover {
      background: #cc0000;
      color: #fff;
    }""",
    )


def generate_html_extraction(text: str, pages_info: List[Dict], pdf_name: str) -> str:
    """
    Erzeugt HTML des extrahierten Rohtexts (ohne Schwaerzung).
    Zeigt was PyMuPDF/Tesseract geliefert hat — als Referenz fuer Abgleich.
    """
    ocr_count = sum(1 for p in pages_info if p["ocr"])

    escaped_text = html_mod.escape(text)
    escaped_text = escaped_text.replace("\n", "<br>\n")

    return _html_wrapper(
        title=f"Extraktion (Rohtext): {html_mod.escape(pdf_name)}",
        summary_html=f"""<strong>Extrahierter Rohtext</strong>
    &nbsp;|&nbsp; {len(pages_info)} Seiten ({ocr_count} via OCR)
    &nbsp;|&nbsp; {len(text)} Zeichen""",
        body_html=escaped_text,
        legend="Rohtext wie von PyMuPDF/Tesseract geliefert. Keine Schwaerzung. Zum Abgleich mit geschwaerzter Version.",
        extra_css="",
    )


def _html_wrapper(title: str, summary_html: str, body_html: str, legend: str, extra_css: str) -> str:
    """Gemeinsames HTML-Template fuer Extraktion und Schwaerzung."""
    return f"""<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="utf-8">
  <title>{title}</title>
  <style>
    body {{
      font-family: Georgia, 'Times New Roman', serif;
      font-size: 14px;
      line-height: 1.7;
      color: #222;
      max-width: 860px;
      margin: 40px auto;
      padding: 0 20px;
      background: #fafafa;
    }}
    h2 {{
      font-size: 16px;
      color: #444;
      border-bottom: 1px solid #ccc;
      padding-bottom: 8px;
    }}
    .summary {{
      background: #fff3f3;
      border-left: 4px solid #cc0000;
      padding: 10px 16px;
      margin: 16px 0 28px 0;
      font-size: 13px;
      color: #555;
    }}
    .summary strong {{
      color: #cc0000;
      font-size: 15px;
    }}
    .document {{
      background: #fff;
      border: 1px solid #ddd;
      padding: 28px 36px;
      border-radius: 2px;
    }}
    .legend {{
      margin-top: 24px;
      font-size: 12px;
      color: #888;
    }}
    {extra_css}
  </style>
</head>
<body>
  <h2>{title}</h2>
  <div class="summary">
    {summary_html}
  </div>
  <div class="document">
    {body_html}
  </div>
  <div class="legend">
    {legend}
  </div>
</body>
</html>"""


# ──────────────────────────────────────────────
# Terminal-Ausgabe
# ──────────────────────────────────────────────

def print_section(title: str):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")


def print_extraction_report(pages_info: List[Dict]):
    print_section("1. EXTRAKTION")
    ocr_pages = [p for p in pages_info if p["ocr"]]
    print(f"Seiten gesamt: {len(pages_info)}  |  OCR-Seiten: {len(ocr_pages)}")
    print()
    for p in pages_info:
        ocr_flag = " [OCR]" if p["ocr"] else ""
        warn = " !! WENIG TEXT" if p["alpha"] < 50 else ""
        print(f"  Seite {p['seite']:2d}:  {p['alpha']:5d} Alpha-Zeichen  |  {p['methode']}{ocr_flag}{warn}")
    if ocr_pages:
        print(f"\n[i] OCR aktiv auf {len(ocr_pages)} Seite(n). OCR-Qualitaet beeinflusst Erkennungsrate.")


def print_pii_report(text: str, entities: List[Dict]):
    print_section("2. GEFUNDENE PII")

    if not entities:
        print("  Keine PII erkannt.")
        return

    by_type = {}
    for ent in entities:
        by_type.setdefault(ent["typ"], []).append(ent)

    for typ, ents in sorted(by_type.items()):
        print(f"\n  [{typ}]  ({len(ents)} Treffer)")
        for ent in ents:
            ctx = entity_context(text, ent)
            print(f"    '{ent['text']}'  ({ent['quelle']})")
            print(f"    Kontext: {ctx}")
            print()


def print_quality_checklist():
    print_section("3. MANUELLE PRUEFUNG")
    checks = [
        "Alle Namen erkannt (Mandanten, Gegenseite, Zeugen, Anwaelte)?",
        "Adressen vollstaendig (Strasse + PLZ + Ort)?",
        "Telefon / Fax / E-Mail erkannt?",
        "Aktenzeichen / Referenznummern erkannt?",
        "KFZ-Kennzeichen komplett (inkl. Zahlen)?",
        "Versicherungs-/Schaden-Nummern erkannt?",
        "Handelsregister / USt-IdNr erkannt?",
        "Falsch-Positive: etwas geschwaerzt das NICHT PII ist?",
    ]
    for i, check in enumerate(checks, 1):
        print(f"  {i:2d}. [ ] {check}")


def print_redacted_text(redacted: str, volltext: bool = False):
    print_section("4. GESCHWAERZTER TEXT")
    if volltext:
        print(redacted)
    else:
        limit = 800
        print(redacted[:limit])
        if len(redacted) > limit:
            print(f"\n  ... ({len(redacted) - limit} weitere Zeichen, --volltext fuer alles)")


# ──────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="PDF-Schwaerzungs-Test fuer Kanzlei-Dokumente (Presidio)"
    )
    parser.add_argument("pdf", help="Pfad zur PDF-Datei")
    parser.add_argument("--output", "-o", help="Eigener Ausgabedateiname (optional)")
    parser.add_argument("--format", "-f", choices=["html", "txt"], default="html",
                        help="Ausgabeformat: html (Standard) oder txt")
    parser.add_argument("--volltext", action="store_true",
                        help="Gesamten geschwaerzten Text im Terminal ausgeben")
    args = parser.parse_args()

    if not os.path.exists(args.pdf):
        print(f"FEHLER: Datei nicht gefunden: {args.pdf}")
        sys.exit(1)

    pdf_name = Path(args.pdf).name
    print(f"\nDokument: {pdf_name}")

    print("Initialisiere Presidio (spaCy de_core_news_lg + Custom-Recognizer)...")
    analyzer = create_analyzer()

    print("Extrahiere Text...")
    text, pages_info = extract_text_from_pdf(args.pdf)

    print("Erkenne PII...")
    entities = detect_pii(text, analyzer)

    redacted = redact_text(text, entities)

    # Terminal-Ausgabe
    print_extraction_report(pages_info)
    print_pii_report(text, entities)
    print_quality_checklist()
    print_redacted_text(redacted, volltext=args.volltext)

    # Zusammenfassung
    print_section("ZUSAMMENFASSUNG")
    ocr_count = sum(1 for p in pages_info if p["ocr"])
    print(f"  Seiten:       {len(pages_info)} gesamt, {ocr_count} via OCR")
    print(f"  PII erkannt:  {len(entities)} Entities")
    print(f"  Zeichen:      {len(text)} -> {len(redacted)} (geschwaerzt)")

    # Dateien speichern: Extraktion (Rohtext) + Schwaerzung
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    stem = Path(args.pdf).stem
    output_dir = Path(args.pdf).parent
    ext = args.format

    # 1. Extraktion (Rohtext)
    extraktion_path = output_dir / f"{stem}_extraktion_{timestamp}.{ext}"
    if args.format == "html":
        extraktion_content = generate_html_extraction(text, pages_info, pdf_name)
    else:
        extraktion_content = text

    with open(extraktion_path, "w", encoding="utf-8") as f:
        f.write(extraktion_content)

    # 2. Schwaerzung
    if args.output:
        schwärzung_path = Path(args.output)
    else:
        schwärzung_path = output_dir / f"{stem}_geschwärzt_{timestamp}.{ext}"

    if args.format == "html":
        schwärzung_content = generate_html(text, entities, pages_info, pdf_name)
    else:
        schwärzung_content = redacted

    with open(schwärzung_path, "w", encoding="utf-8") as f:
        f.write(schwärzung_content)

    print(f"\n  Extraktion (Rohtext): {extraktion_path}")
    print(f"  Geschwaerzt:         {schwärzung_path}")
    if args.format == "html":
        print(f"  -> Beide im Browser oeffnen, nebeneinander vergleichen")

    print()


if __name__ == "__main__":
    main()
