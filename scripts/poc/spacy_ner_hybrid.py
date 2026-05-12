#!/usr/bin/env python3
"""
Hybrid NER: spaCy + Regex-Fallback
Kombiniert spaCy NER mit Regex-Mustern für häufige Anwalts-Kontexte.
"""

import re
import spacy
from typing import List, Dict, Set


def load_model():
    """Lädt de_core_news_lg."""
    try:
        return spacy.load("de_core_news_lg")
    except OSError:
        print("ERROR: Modell 'de_core_news_lg' nicht gefunden.")
        sys.exit(1)


def detect_persons_spacy(text: str, nlp) -> List[Dict]:
    """Erkennt PER-Entities mit spaCy."""
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
    """
    Regex-basierte Erkennung für Anwalts-Kontext.

    Pattern: [Rechtsanwalt/RA/Prozessbevollmächtigter] [Dr./Prof.] [Nachname]
    """
    patterns = [
        # Rechtsanwalt Dr. Name / Rechtsanwältin Name
        r'\b(?:Rechtsanwalt|Rechtsanwältin|RA)\s+(?:Dr\.\s+|Prof\.\s+)?([A-ZÄÖÜ][a-zäöüß]+(?:-[A-ZÄÖÜ][a-zäöüß]+)?)',
        # Prozessbevollmächtigter Name
        r'\bProzessbevollmächtigte[rn]?\s+([A-ZÄÖÜ][a-zäöüß]+(?:-[A-ZÄÖÜ][a-zäöüß]+)?)',
        # Bevollmächtigter Name
        r'\bBevollmächtigte[rn]?\s+([A-ZÄÖÜ][a-zäöüß]+(?:-[A-ZÄÖÜ][a-zäöüß]+)?)',
        # Herr/Frau Name (mit optionalem Titel)
        r'\b(?:Herr|Frau)\s+(?:Dr\.\s+|Prof\.\s+)?([A-ZÄÖÜ][a-zäöüß]+(?:-[A-ZÄÖÜ][a-zäöüß]+)?)',
        # Dr. Name (ohne vorangehende Berufsbezeichnung)
        r'\bDr\.\s+([A-ZÄÖÜ][a-zäöüß]+(?:-[A-ZÄÖÜ][a-zäöüß]+)?)',
    ]

    persons = []
    for pattern in patterns:
        for match in re.finditer(pattern, text):
            name = match.group(1)
            # Prüfe dass es nicht nur "Der" oder ähnlich ist
            if len(name) > 2 and name not in ["Die", "Das", "Der", "Den", "Dem"]:
                persons.append({
                    "text": name,
                    "start": match.start(1),
                    "end": match.end(1),
                    "source": "regex"
                })

    return persons


def merge_detections(spacy_persons: List[Dict], regex_persons: List[Dict]) -> List[Dict]:
    """
    Merged spaCy und Regex-Erkennungen, entfernt Duplikate.

    Duplikat-Kriterium: Overlapping character spans
    """
    all_persons = spacy_persons + regex_persons

    # Sortiere nach Start-Position
    all_persons.sort(key=lambda x: x["start"])

    # Entferne Overlaps
    merged = []
    for person in all_persons:
        # Prüfe ob schon eine Entity mit Overlap existiert
        has_overlap = False
        for existing in merged:
            if (person["start"] <= existing["end"] and person["end"] >= existing["start"]):
                has_overlap = True
                # Bevorzuge spaCy-Erkennungen bei Overlap
                if person["source"] == "spacy" and existing["source"] == "regex":
                    # Ersetze Regex-Erkennung durch spaCy
                    merged.remove(existing)
                    merged.append(person)
                break

        if not has_overlap:
            merged.append(person)

    # Sortiere wieder nach Start-Position
    merged.sort(key=lambda x: x["start"])

    return merged


def test_hybrid():
    """Testet das Hybrid-System."""
    nlp = load_model()

    test_cases = [
        ("Standard-Fall",
         "Herr Max Mustermann und Frau Maria Schneider waren anwesend.",
         ["Max Mustermann", "Maria Schneider"]),

        ("Anwalts-Kontext",
         "Rechtsanwalt Dr. Voigt vertritt die Klägerin. Rechtsanwältin Meier vertritt die Beklagte.",
         ["Voigt", "Meier"]),

        ("Prozessbevollmächtigter",
         "Der Prozessbevollmächtigte Schmidt legte Widerspruch ein.",
         ["Schmidt"]),

        ("Gemischt",
         "RA Dr. Weber und Rechtsanwältin Müller vertreten Klaus Mustermann.",
         ["Weber", "Müller", "Klaus Mustermann"]),
    ]

    print("=" * 80)
    print("Hybrid NER: spaCy + Regex")
    print("=" * 80)

    for test_name, text, expected in test_cases:
        print(f"\n--- {test_name} ---")
        print(f"Text: {text}")

        spacy_persons = detect_persons_spacy(text, nlp)
        regex_persons = detect_persons_regex(text)
        merged = merge_detections(spacy_persons, regex_persons)

        print(f"\nspaCy: {len(spacy_persons)} | Regex: {len(regex_persons)} | Merged: {len(merged)}")
        print(f"Erkannt:")
        for p in merged:
            print(f"  - '{p['text']}' (Quelle: {p['source']})")

        # Quick-Check gegen Expected
        detected_names = set([p["text"].lower() for p in merged])
        expected_lower = set([e.lower() for e in expected])

        # Partial matching
        matched = 0
        for exp in expected:
            for det in detected_names:
                if exp.lower() in det or det in exp.lower():
                    matched += 1
                    break

        recall = matched / len(expected) if len(expected) > 0 else 0
        print(f"Recall: {recall:.1%} ({matched}/{len(expected)})")


if __name__ == "__main__":
    test_hybrid()
