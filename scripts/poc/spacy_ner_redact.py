#!/usr/bin/env python3
"""
spaCy NER Schwärzungs-PoC
Nutzt de_core_news_lg zur Erkennung von PER-Entities in deutschen Schriftsätzen.

Ziel: False-Negative-Rate bei Namen-Erkennung messen.
Baut auf PyMuPDF-Extraktion auf.
"""

import sys
import os
from pathlib import Path
from typing import List, Dict, Tuple

try:
    import spacy
except ImportError:
    print("ERROR: spaCy nicht installiert.")
    print("Installation: python3 -m pip install spacy")
    print("Modell: python3 -m spacy download de_core_news_lg")
    sys.exit(1)

try:
    import pymupdf
except ImportError:
    print("ERROR: PyMuPDF nicht installiert.")
    print("Installation: python3 -m pip install pymupdf")
    sys.exit(1)


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extrahiert Text aus PDF mit PyMuPDF."""
    doc = pymupdf.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text


def load_spacy_model():
    """Lädt das deutsche spaCy-Modell."""
    try:
        nlp = spacy.load("de_core_news_lg")
        return nlp
    except OSError:
        print("ERROR: Modell 'de_core_news_lg' nicht gefunden.")
        print("Installation: python3 -m spacy download de_core_news_lg")
        sys.exit(1)


def detect_persons(text: str, nlp) -> List[Dict]:
    """
    Erkennt PER-Entities mit spaCy.

    Returns:
        Liste von dicts: {"text": str, "start": int, "end": int, "label": str}
    """
    doc = nlp(text)
    persons = []

    for ent in doc.ents:
        if ent.label_ == "PER":
            persons.append({
                "text": ent.text,
                "start": ent.start_char,
                "end": ent.end_char,
                "label": ent.label_
            })

    return persons


def redact_text(text: str, entities: List[Dict]) -> str:
    """
    Ersetzt erkannte Entities durch [GESCHWÄRZT].
    """
    # Sort entities by start position (reverse) to maintain offsets
    sorted_entities = sorted(entities, key=lambda x: x["start"], reverse=True)

    redacted = text
    for entity in sorted_entities:
        redacted = redacted[:entity["start"]] + "[GESCHWÄRZT]" + redacted[entity["end"]:]

    return redacted


def create_synthetic_schriftsatz() -> Tuple[str, List[str]]:
    """
    Erstellt synthetischen deutschen Schriftsatz mit bekannten Namen.

    Returns:
        (text, ground_truth_names) - Text und Liste der Namen die erkannt werden sollten
    """
    text = """Landgericht Berlin
Aktenzeichen: 27 O 123/2026

Klage
der Kanzlei Voigt Rechtsanwälte, vertreten durch Rechtsanwalt Dr. Henrik Voigt,
gegen
Herrn Max Mustermann, wohnhaft in Musterstraße 123, 10115 Berlin,

sowie
Frau Maria Schneider, wohnhaft in Lindenallee 45, 80331 München.

Die Klägerin, vertreten durch Dr. Voigt, beantragt die Feststellung, dass die Beklagten,
Herr Mustermann und Frau Schneider, zur Zahlung von Schadensersatz verpflichtet sind.

Der Sachverhalt:
Am 15. März 2025 kam es zu einem Vorfall, bei dem Klaus Müller, ein Zeuge des Geschehens,
beobachtete, wie die Beklagten gegen vertragliche Vereinbarungen verstießen.

Herr Thomas Weber, der als Gutachter hinzugezogen wurde, bestätigte in seinem Bericht vom
20. März 2025, dass erhebliche Mängel vorliegen. Auch Frau Anna Schmidt, die als weitere
Zeugin vernommen wurde, bestätigte diese Aussage.

Der Bevollmächtigte der Klägerin, Rechtsanwalt Voigt, fordert daher Schadensersatz in Höhe
von 50.000 Euro. Die Beklagten, Max Mustermann und Maria Schneider, haben bislang keine
Stellungnahme abgegeben.

Berlin, den 11. Mai 2026
Dr. Henrik Voigt
Rechtsanwalt
"""

    ground_truth = [
        "Dr. Henrik Voigt",
        "Henrik Voigt",
        "Max Mustermann",
        "Maria Schneider",
        "Klaus Müller",
        "Thomas Weber",
        "Anna Schmidt",
        "Voigt"
    ]

    return text, ground_truth


def evaluate_detection(detected: List[Dict], ground_truth: List[str], text: str) -> Dict:
    """
    Bewertet die Erkennungsqualität.

    Returns:
        dict mit Metriken: detected_names, ground_truth_names, false_negatives, precision
    """
    detected_texts = [d["text"] for d in detected]

    # Normalisiere für Vergleich (Case-insensitive, Strip)
    detected_normalized = set([d.lower().strip() for d in detected_texts])
    ground_truth_normalized = set([g.lower().strip() for g in ground_truth])

    # False Negatives: Namen die im Ground Truth sind aber nicht erkannt wurden
    false_negatives = []
    for gt_name in ground_truth:
        # Prüfe ob Name irgendwo in detected_texts vorkommt (auch als Teilstring)
        found = False
        gt_lower = gt_name.lower()
        for detected_name in detected_texts:
            if gt_lower in detected_name.lower() or detected_name.lower() in gt_lower:
                found = True
                break
        if not found:
            false_negatives.append(gt_name)

    # True Positives: Korrekt erkannte Namen
    true_positives = len(ground_truth) - len(false_negatives)

    # Recall: Wie viele der echten Namen wurden gefunden?
    recall = true_positives / len(ground_truth) if len(ground_truth) > 0 else 0

    return {
        "detected_count": len(detected),
        "detected_names": detected_texts,
        "ground_truth_count": len(ground_truth),
        "ground_truth_names": ground_truth,
        "false_negatives": false_negatives,
        "false_negative_count": len(false_negatives),
        "true_positives": true_positives,
        "recall": recall,
        "false_negative_rate": len(false_negatives) / len(ground_truth) if len(ground_truth) > 0 else 0
    }


def analyze_results(text: str, detected: List[Dict], evaluation: Dict, redacted_text: str):
    """Gibt detaillierte Analyse aus."""
    print("=" * 80)
    print("spaCy NER Schwärzungs-PoC: de_core_news_lg")
    print("=" * 80)

    print(f"\n--- Original-Text ({len(text)} Zeichen) ---")
    print(text[:500] + "..." if len(text) > 500 else text)

    print(f"\n--- Erkannte PER-Entities ({evaluation['detected_count']}) ---")
    for i, entity in enumerate(detected, 1):
        print(f"{i}. '{entity['text']}' (Position {entity['start']}-{entity['end']})")

    print(f"\n--- Ground Truth ({evaluation['ground_truth_count']} Namen) ---")
    for i, name in enumerate(evaluation['ground_truth_names'], 1):
        print(f"{i}. {name}")

    print(f"\n--- Bewertung ---")
    print(f"True Positives: {evaluation['true_positives']}/{evaluation['ground_truth_count']}")
    print(f"False Negatives: {evaluation['false_negative_count']}")
    print(f"Recall: {evaluation['recall']:.2%}")
    print(f"False-Negative-Rate: {evaluation['false_negative_rate']:.2%}")

    if evaluation['false_negatives']:
        print(f"\nNICHT erkannte Namen:")
        for name in evaluation['false_negatives']:
            print(f"  - {name}")

    print(f"\n--- Geschwärzter Text (Sample) ---")
    print(redacted_text[:500] + "..." if len(redacted_text) > 500 else redacted_text)

    print("\n" + "=" * 80)


def main():
    print("Lade spaCy-Modell de_core_news_lg...")
    nlp = load_spacy_model()
    print(f"Modell geladen: {nlp.meta['name']} v{nlp.meta['version']}")

    # Option 1: PDF-Datei verarbeiten
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
        if not os.path.exists(pdf_path):
            print(f"ERROR: Datei nicht gefunden: {pdf_path}")
            sys.exit(1)

        print(f"\nExtrahiere Text aus PDF: {pdf_path}")
        text = extract_text_from_pdf(pdf_path)
        ground_truth = []  # Bei echten PDFs haben wir kein Ground Truth
        print(f"Text extrahiert: {len(text)} Zeichen")

    # Option 2: Synthetischer Testfall
    else:
        print("\nKeine PDF-Datei angegeben - verwende synthetischen Testfall")
        text, ground_truth = create_synthetic_schriftsatz()

    # NER-Erkennung
    print("\nFuehre NER-Erkennung durch...")
    detected = detect_persons(text, nlp)

    # Schwärzung
    redacted_text = redact_text(text, detected)

    # Evaluation (nur wenn Ground Truth vorhanden)
    if ground_truth:
        evaluation = evaluate_detection(detected, ground_truth, text)
        analyze_results(text, detected, evaluation, redacted_text)
    else:
        # Ohne Ground Truth nur Erkennungs-Output
        print(f"\n--- Erkannte PER-Entities ({len(detected)}) ---")
        for i, entity in enumerate(detected, 1):
            print(f"{i}. '{entity['text']}' (Position {entity['start']}-{entity['end']})")
        print(f"\n--- Geschwärzter Text (Sample) ---")
        print(redacted_text[:500] + "..." if len(redacted_text) > 500 else redacted_text)


if __name__ == "__main__":
    main()
