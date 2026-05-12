#!/usr/bin/env python3
"""
Batch-Test aller Test-PDFs gegen PyMuPDF.
Erstellt vergleichbare Metriken fuer Evaluation gegen C# iText-Baseline.
"""

import sys
import os
from pathlib import Path
import glob

try:
    import pymupdf
except ImportError:
    print("ERROR: PyMuPDF nicht installiert.")
    sys.exit(1)


def extract_text_pymupdf(pdf_path: str) -> dict:
    """Extrahiert Text aus PDF mit PyMuPDF."""
    doc = pymupdf.open(pdf_path)

    results = {
        "text": "",
        "page_count": len(doc),
        "char_count": 0,
        "alpha_chars_per_page": [],
        "min_alpha_chars": float('inf'),
        "extraction_method": "pymupdf.get_text()"
    }

    for page_num, page in enumerate(doc):
        page_text = page.get_text()
        alpha_count = sum(1 for c in page_text if c.isalpha())
        results["alpha_chars_per_page"].append(alpha_count)
        results["text"] += page_text

        if alpha_count < results["min_alpha_chars"]:
            results["min_alpha_chars"] = alpha_count

    results["char_count"] = len(results["text"])

    # Whitespace-Density
    if results["char_count"] > 0:
        whitespace_count = sum(1 for c in results["text"] if c.isspace())
        results["whitespace_density"] = whitespace_count / results["char_count"]
    else:
        results["whitespace_density"] = 0.0

    # OCR-Trigger-Check (Skadi: < 10 Alpha-Chars auf einer Seite)
    results["would_trigger_ocr"] = results["min_alpha_chars"] < 10

    # Cleanup-Trigger-Check (Skadi: Whitespace-Density < 0.05)
    results["would_trigger_cleanup"] = results["whitespace_density"] < 0.05

    doc.close()
    return results


def main():
    test_dir = "/home/andreas/claude-projects/skadi-doku/test-files"
    pdf_files = sorted(glob.glob(os.path.join(test_dir, "*.pdf")))

    if not pdf_files:
        print(f"Keine PDFs in {test_dir} gefunden.")
        sys.exit(1)

    print("=" * 80)
    print(f"PyMuPDF Batch-Test: {len(pdf_files)} PDFs")
    print("=" * 80)
    print()

    # Tabellen-Header
    print(f"{'Datei':<30} {'Seiten':>6} {'Zeichen':>8} {'Min-Alpha':>10} {'OCR?':>6} {'Cleanup?':>8} {'WS-Density':>11}")
    print("-" * 80)

    results_list = []

    for pdf_path in pdf_files:
        filename = Path(pdf_path).name

        try:
            results = extract_text_pymupdf(pdf_path)
            results_list.append((filename, results))

            ocr_flag = "JA" if results["would_trigger_ocr"] else "nein"
            cleanup_flag = "JA" if results["would_trigger_cleanup"] else "nein"

            # Kuerze Dateinamen wenn noetig
            display_name = filename[:28] + ".." if len(filename) > 30 else filename

            print(f"{display_name:<30} {results['page_count']:>6} {results['char_count']:>8} "
                  f"{results['min_alpha_chars']:>10} {ocr_flag:>6} {cleanup_flag:>8} "
                  f"{results['whitespace_density']:>11.4f}")

        except Exception as e:
            print(f"{filename:<30} ERROR: {e}")

    print()
    print("=" * 80)
    print("Legende:")
    print("  OCR?     - Wuerde in C# Skadi OCR-Fallback triggern (< 10 Alpha-Chars/Seite)")
    print("  Cleanup? - Wuerde Mimir-Cleanup triggern (Whitespace-Density < 0.05)")
    print("=" * 80)
    print()

    # Detaillierte Text-Samples fuer kritische Faelle
    print("Detaillierte Samples (erste 200 Zeichen):")
    print()
    for filename, results in results_list:
        if results["would_trigger_ocr"] or results["char_count"] < 100:
            print(f"--- {filename} ---")
            print(results["text"][:200])
            print()


if __name__ == "__main__":
    main()
