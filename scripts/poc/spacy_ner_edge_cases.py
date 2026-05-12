#!/usr/bin/env python3
"""
spaCy NER Edge-Cases Test
Testet schwierige Fälle: Titel, Genitiv, Anreden, zusammengesetzte Namen, etc.
"""

import sys
import spacy
from typing import List, Dict, Tuple


def load_model():
    """Lädt de_core_news_lg."""
    try:
        return spacy.load("de_core_news_lg")
    except OSError:
        print("ERROR: Modell 'de_core_news_lg' nicht gefunden.")
        print("Installation: python3 -m spacy download de_core_news_lg")
        sys.exit(1)


def detect_persons(text: str, nlp) -> List[Dict]:
    """Erkennt PER-Entities."""
    doc = nlp(text)
    persons = []
    for ent in doc.ents:
        if ent.label_ == "PER":
            persons.append({
                "text": ent.text,
                "start": ent.start_char,
                "end": ent.end_char
            })
    return persons


def create_edge_case_tests() -> List[Tuple[str, str, List[str]]]:
    """
    Erstellt Edge-Case-Tests.

    Returns:
        Liste von (name, text, expected_names)
    """
    tests = []

    # Test 1: Titel und akademische Grade
    tests.append((
        "Akademische Titel",
        """Prof. Dr. med. Klaus-Dieter Müller-Schmidt ist der behandelnde Arzt.
        Auch Dr. h.c. Anna Maria von Weber war anwesend.""",
        ["Prof. Dr. med. Klaus-Dieter Müller-Schmidt", "Dr. h.c. Anna Maria von Weber"]
    ))

    # Test 2: Genitiv-Formen
    tests.append((
        "Genitiv",
        """Das Auto des Herrn Mustermanns wurde beschädigt.
        Die Aussage Frau Schneiders ist widersprüchlich.""",
        ["Mustermanns", "Schneiders"]  # spaCy erkennt oft Genitiv-Formen
    ))

    # Test 3: Mehrfachnennung mit Anreden
    tests.append((
        "Anreden",
        """Herr Müller, Frau Schmidt und Herr Dr. Weber waren anwesend.
        Auch Herrn Müllers Anwalt kam.""",
        ["Müller", "Schmidt", "Dr. Weber", "Müllers"]
    ))

    # Test 4: Namen in Listen
    tests.append((
        "Listen",
        """Anwesend waren: 1. Max Mustermann, 2. Maria Schneider, 3. Klaus Müller.""",
        ["Max Mustermann", "Maria Schneider", "Klaus Müller"]
    ))

    # Test 5: Firmennamen vs. Personennamen
    tests.append((
        "Firmen vs. Personen",
        """Die Müller GmbH, vertreten durch Geschäftsführer Hans Müller, klagt gegen
        die Schmidt & Partner KG, vertreten durch Thomas Schmidt.""",
        ["Hans Müller", "Thomas Schmidt"]  # Firmen sollten ORG sein, nicht PER
    ))

    # Test 6: Vornamen allein (oft in Anwaltsschriftsätzen bei Wiederholungen)
    tests.append((
        "Vornamen allein",
        """Der Kläger, Max Mustermann, bestreitet dies. Max war nicht am Tatort.""",
        ["Max Mustermann", "Max"]  # Zweites "Max" sollte auch erkannt werden
    ))

    # Test 7: Namen in Adressen
    tests.append((
        "Adressen",
        """Herr Thomas Weber, wohnhaft in Müllerstraße 5, 10115 Berlin.""",
        ["Thomas Weber"]  # "Müllerstraße" sollte NICHT als Person erkannt werden
    ))

    # Test 8: Häufige Anwalts-Kontexte
    tests.append((
        "Anwalts-Kontext",
        """Rechtsanwalt Dr. Voigt vertritt die Klägerin. Rechtsanwältin Meier vertritt die Beklagte.
        Der Prozessbevollmächtigte Schmidt legte Widerspruch ein.""",
        ["Dr. Voigt", "Meier", "Schmidt"]
    ))

    return tests


def evaluate_test(test_name: str, text: str, expected: List[str], detected: List[Dict]):
    """Evaluiert einen einzelnen Test."""
    detected_texts = [d["text"] for d in detected]

    # Simple Matching: prüfe ob erwartete Namen in erkannten enthalten sind
    matched = []
    missed = []

    for exp_name in expected:
        found = False
        exp_lower = exp_name.lower()
        for det_name in detected_texts:
            # Prüfe Substring-Match in beide Richtungen
            if exp_lower in det_name.lower() or det_name.lower() in exp_lower:
                found = True
                matched.append(exp_name)
                break
        if not found:
            missed.append(exp_name)

    # False Positives: Erkannte Namen die nicht erwartet wurden
    false_positives = []
    for det_name in detected_texts:
        det_lower = det_name.lower()
        expected_match = False
        for exp_name in expected:
            if exp_name.lower() in det_lower or det_lower in exp_name.lower():
                expected_match = True
                break
        if not expected_match:
            false_positives.append(det_name)

    recall = len(matched) / len(expected) if len(expected) > 0 else 0
    precision = (len(detected) - len(false_positives)) / len(detected) if len(detected) > 0 else 0

    return {
        "test_name": test_name,
        "expected_count": len(expected),
        "detected_count": len(detected),
        "matched": matched,
        "missed": missed,
        "false_positives": false_positives,
        "recall": recall,
        "precision": precision
    }


def main():
    print("Lade spaCy-Modell...")
    nlp = load_model()
    print(f"Modell: {nlp.meta['name']} v{nlp.meta['version']}\n")

    tests = create_edge_case_tests()

    results = []
    for test_name, text, expected in tests:
        detected = detect_persons(text, nlp)
        result = evaluate_test(test_name, text, expected, detected)
        results.append(result)

    # Output
    print("=" * 80)
    print("spaCy NER Edge-Cases: de_core_news_lg")
    print("=" * 80)

    total_expected = 0
    total_matched = 0
    total_missed = 0
    total_false_positives = 0

    for i, result in enumerate(results, 1):
        print(f"\nTest {i}: {result['test_name']}")
        print("-" * 80)
        print(f"Erwartet: {result['expected_count']} Namen")
        print(f"Erkannt: {result['detected_count']} Entities")
        print(f"Korrekt: {len(result['matched'])}")
        print(f"Übersehen: {len(result['missed'])}")
        print(f"False Positives: {len(result['false_positives'])}")
        print(f"Recall: {result['recall']:.2%}")
        print(f"Precision: {result['precision']:.2%}")

        if result['missed']:
            print(f"\nÜBERSEHEN:")
            for name in result['missed']:
                print(f"  - {name}")

        if result['false_positives']:
            print(f"\nFALSE POSITIVES:")
            for name in result['false_positives']:
                print(f"  - {name}")

        total_expected += result['expected_count']
        total_matched += len(result['matched'])
        total_missed += len(result['missed'])
        total_false_positives += len(result['false_positives'])

    # Gesamt-Statistik
    print("\n" + "=" * 80)
    print("GESAMT-STATISTIK")
    print("=" * 80)
    print(f"Tests: {len(results)}")
    print(f"Erwartete Namen: {total_expected}")
    print(f"Korrekt erkannt: {total_matched}")
    print(f"Übersehen: {total_missed}")
    print(f"False Positives: {total_false_positives}")
    overall_recall = total_matched / total_expected if total_expected > 0 else 0
    print(f"Overall Recall: {overall_recall:.2%}")
    print(f"False-Negative-Rate: {total_missed / total_expected * 100:.1f}%")


if __name__ == "__main__":
    main()
