#!/usr/bin/env python3
"""
PyMuPDF Text Extraction PoC
Vergleicht PyMuPDF gegen die C# iText-basierte Extraktion in Skadi.

Ziel: Pruefe ob PyMuPDF Issue 2 (OCR-Fehlzuendung auf Vektor-PDFs) automatisch loest.
"""

import sys
import os
from pathlib import Path

try:
    import pymupdf  # PyMuPDF package
except ImportError:
    print("ERROR: PyMuPDF nicht installiert.")
    print("Installation: python3 -m pip install --user pymupdf")
    print("oder: apt install python3-pymupdf")
    sys.exit(1)


def extract_text_pymupdf(pdf_path: str) -> dict:
    """
    Extrahiert Text aus PDF mit PyMuPDF.

    Returns:
        dict mit keys: text, page_count, char_count, alpha_chars_per_page
    """
    doc = pymupdf.open(pdf_path)

    results = {
        "text": "",
        "page_count": len(doc),
        "char_count": 0,
        "alpha_chars_per_page": [],
        "extraction_method": "pymupdf.get_text()"
    }

    for page_num, page in enumerate(doc):
        # Standard-Extraktion (entspricht iText dual-strategy ohne OCR)
        page_text = page.get_text()

        alpha_count = sum(1 for c in page_text if c.isalpha())
        results["alpha_chars_per_page"].append(alpha_count)
        results["text"] += page_text

    results["char_count"] = len(results["text"])
    doc.close()

    return results


def analyze_results(results: dict, filename: str):
    """
    Gibt Analyse-Output wie in Skadi Decision-Gates.
    """
    print(f"\n=== PyMuPDF Extraktion: {filename} ===")
    print(f"Seiten: {results['page_count']}")
    print(f"Gesamtzeichen: {results['char_count']}")
    print(f"Methode: {results['extraction_method']}")

    print("\nAlpha-Chars pro Seite (Skadi OCR-Gate: < 10 triggert OCR):")
    for i, alpha_count in enumerate(results["alpha_chars_per_page"], 1):
        ocr_trigger = " [!] OCR-TRIGGER" if alpha_count < 10 else ""
        print(f"  Seite {i}: {alpha_count} Alpha-Chars{ocr_trigger}")

    # Whitespace-Density-Check (Skadi Cleanup-Gate)
    text = results["text"]
    if len(text) > 0:
        whitespace_count = sum(1 for c in text if c.isspace())
        density = whitespace_count / len(text)
        cleanup_trigger = " [!] CLEANUP-TRIGGER" if density < 0.05 else ""
        print(f"\nWhitespace-Density: {density:.4f} (Gate: 0.05){cleanup_trigger}")

    # Text-Sample
    print(f"\nText-Sample (erste 300 Zeichen):")
    print(results["text"][:300])
    print("...")


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 pymupdf_extract.py <path-to-pdf>")
        print("\nBeispiel:")
        print("  python3 pymupdf_extract.py /home/andreas/test-docs/sample.pdf")
        sys.exit(1)

    pdf_path = sys.argv[1]

    if not os.path.exists(pdf_path):
        print(f"ERROR: Datei nicht gefunden: {pdf_path}")
        sys.exit(1)

    try:
        results = extract_text_pymupdf(pdf_path)
        analyze_results(results, Path(pdf_path).name)
    except Exception as e:
        print(f"ERROR bei Extraktion: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
