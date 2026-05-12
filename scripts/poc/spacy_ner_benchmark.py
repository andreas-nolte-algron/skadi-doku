#!/usr/bin/env python3
"""
Finales Benchmark: spaCy NER vs. Hybrid (spaCy + Regex)
Misst False-Negative-Rate für realistischen Schriftsatz.
"""

import re
import spacy
from typing import List, Dict


def load_model():
    return spacy.load("de_core_news_lg")


def detect_persons_spacy(text: str, nlp) -> List[Dict]:
    doc = nlp(text)
    persons = []
    for ent in doc.ents:
        if ent.label_ == "PER":
            persons.append({
                "text": ent.text,
                "start": ent.start_char,
                "end": ent.end_char,
                "source": "spacy"
            })
    return persons


def detect_persons_regex(text: str) -> List[Dict]:
    patterns = [
        r'\b(?:Rechtsanwalt|Rechtsanwältin|RA)\s+(?:Dr\.\s+|Prof\.\s+)?([A-ZÄÖÜ][a-zäöüß]+(?:-[A-ZÄÖÜ][a-zäöüß]+)?)',
        r'\bProzessbevollmächtigte[rn]?\s+([A-ZÄÖÜ][a-zäöüß]+)',
        r'\bBevollmächtigte[rn]?\s+([A-ZÄÖÜ][a-zäöüß]+)',
    ]

    persons = []
    for pattern in patterns:
        for match in re.finditer(pattern, text):
            name = match.group(1)
            if len(name) > 2 and name not in ["Die", "Das", "Der", "Den", "Dem"]:
                persons.append({
                    "text": name,
                    "start": match.start(1),
                    "end": match.end(1),
                    "source": "regex"
                })
    return persons


def merge_detections(spacy_persons: List[Dict], regex_persons: List[Dict]) -> List[Dict]:
    all_persons = spacy_persons + regex_persons
    all_persons.sort(key=lambda x: x["start"])

    merged = []
    for person in all_persons:
        has_overlap = False
        for existing in merged:
            if (person["start"] <= existing["end"] and person["end"] >= existing["start"]):
                has_overlap = True
                if person["source"] == "spacy" and existing["source"] == "regex":
                    merged.remove(existing)
                    merged.append(person)
                break
        if not has_overlap:
            merged.append(person)

    merged.sort(key=lambda x: x["start"])
    return merged


def create_benchmark_schriftsatz() -> tuple:
    """Realistischer Schriftsatz mit allen Edge-Cases."""
    text = """Landgericht Berlin
Aktenzeichen: 27 O 123/2026

Klage
der Kanzlei Voigt Rechtsanwälte, vertreten durch Rechtsanwalt Dr. Henrik Voigt,
Kanzleistraße 12, 10115 Berlin,

gegen

1. Herrn Max Mustermann, wohnhaft in Musterstraße 123, 10115 Berlin,
2. Frau Maria Schneider, wohnhaft in Lindenallee 45, 80331 München,
3. die Müller GmbH, vertreten durch Geschäftsführer Hans Müller, Industriestr. 5, 80333 München.

Die Klagepartei, vertreten durch Rechtsanwalt Voigt, beantragt die Feststellung, dass die Beklagten
zur Zahlung von Schadensersatz verpflichtet sind.

Sachverhalt:

Am 15. März 2025 kam es zu einem Vorfall, bei dem der Zeuge Klaus Müller beobachtete, wie
Herr Mustermann und Frau Schneider gegen vertragliche Vereinbarungen verstießen.

Prof. Dr. Thomas Weber, der als Gutachter hinzugezogen wurde, bestätigte in seinem Gutachten
vom 20. März 2025 die Mängel. Auch die Zeugin Anna Schmidt bestätigte dies in ihrer
eidesstattlichen Versicherung.

Rechtliche Würdigung:

Die Prozessbevollmächtigte der Beklagten, Rechtsanwältin Dr. Meier, bestreitet die Vorwürfe.
Der Bevollmächtigte Schmidt, der Herrn Mustermann vertritt, verwies auf die Aussage des
Sachverständigen Weber.

Die Aussage Frau Schneiders ist widersprüchlich. Herr Mustermanns Anwalt, RA Schulze,
legte dagegen Widerspruch ein.

Berlin, den 11. Mai 2026

Dr. Henrik Voigt
Rechtsanwalt
"""

    ground_truth = [
        "Dr. Henrik Voigt",
        "Henrik Voigt",
        "Max Mustermann",
        "Maria Schneider",
        "Hans Müller",  # Geschäftsführer
        "Voigt",
        "Klaus Müller",  # Zeuge
        "Prof. Dr. Thomas Weber",
        "Thomas Weber",
        "Anna Schmidt",
        "Dr. Meier",  # Anwältin Beklagte
        "Meier",
        "Schmidt",  # Bevollmächtigter
        "Weber",  # Sachverständiger
        "Schneiders",  # Genitiv
        "Mustermanns",  # Genitiv
        "Schulze",  # RA
    ]

    return text, ground_truth


def evaluate(detected: List[Dict], ground_truth: List[str]) -> Dict:
    detected_texts = [d["text"] for d in detected]

    matched = 0
    missed = []

    for gt_name in ground_truth:
        found = False
        gt_lower = gt_name.lower()
        for det_name in detected_texts:
            if gt_lower in det_name.lower() or det_name.lower() in gt_lower:
                found = True
                break
        if found:
            matched += 1
        else:
            missed.append(gt_name)

    recall = matched / len(ground_truth) if len(ground_truth) > 0 else 0
    fn_rate = len(missed) / len(ground_truth) if len(ground_truth) > 0 else 0

    return {
        "detected_count": len(detected),
        "ground_truth_count": len(ground_truth),
        "matched": matched,
        "missed": missed,
        "recall": recall,
        "false_negative_rate": fn_rate
    }


def main():
    print("Lade spaCy-Modell de_core_news_lg...")
    nlp = load_model()

    text, ground_truth = create_benchmark_schriftsatz()

    # spaCy allein
    spacy_persons = detect_persons_spacy(text, nlp)
    spacy_eval = evaluate(spacy_persons, ground_truth)

    # Hybrid (spaCy + Regex)
    regex_persons = detect_persons_regex(text)
    hybrid_persons = merge_detections(spacy_persons, regex_persons)
    hybrid_eval = evaluate(hybrid_persons, ground_truth)

    # Output
    print("\n" + "=" * 80)
    print("BENCHMARK: spaCy NER vs. Hybrid (spaCy + Regex)")
    print("=" * 80)

    print(f"\nTestdokument: Realistischer Schriftsatz ({len(text)} Zeichen)")
    print(f"Ground Truth: {len(ground_truth)} Namen")

    print("\n--- spaCy allein ---")
    print(f"Erkannt: {spacy_eval['detected_count']}")
    print(f"Korrekt: {spacy_eval['matched']}/{spacy_eval['ground_truth_count']}")
    print(f"Übersehen: {len(spacy_eval['missed'])}")
    print(f"Recall: {spacy_eval['recall']:.2%}")
    print(f"False-Negative-Rate: {spacy_eval['false_negative_rate']:.2%}")
    if spacy_eval['missed']:
        print(f"\nÜbersehen:")
        for name in spacy_eval['missed'][:10]:  # Max 10 anzeigen
            print(f"  - {name}")

    print("\n--- Hybrid (spaCy + Regex) ---")
    print(f"Erkannt: {hybrid_eval['detected_count']} (spaCy: {len(spacy_persons)}, Regex: {len(regex_persons)})")
    print(f"Korrekt: {hybrid_eval['matched']}/{hybrid_eval['ground_truth_count']}")
    print(f"Übersehen: {len(hybrid_eval['missed'])}")
    print(f"Recall: {hybrid_eval['recall']:.2%}")
    print(f"False-Negative-Rate: {hybrid_eval['false_negative_rate']:.2%}")
    if hybrid_eval['missed']:
        print(f"\nÜbersehen:")
        for name in hybrid_eval['missed']:
            print(f"  - {name}")

    print("\n--- Verbesserung durch Hybrid ---")
    improvement = hybrid_eval['recall'] - spacy_eval['recall']
    fn_reduction = spacy_eval['false_negative_rate'] - hybrid_eval['false_negative_rate']
    print(f"Recall-Gewinn: {improvement:+.2%}")
    print(f"False-Negative-Reduktion: {fn_reduction:+.2%}")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
