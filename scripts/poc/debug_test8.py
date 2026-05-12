#!/usr/bin/env python3
"""Debug Test 8 - warum werden die Namen nicht erkannt?"""

import spacy

nlp = spacy.load("de_core_news_lg")

text = """Rechtsanwalt Dr. Voigt vertritt die Klägerin. Rechtsanwältin Meier vertritt die Beklagte.
Der Prozessbevollmächtigte Schmidt legte Widerspruch ein."""

doc = nlp(text)

print("=== Alle erkannten Entities ===")
for ent in doc.ents:
    print(f"Text: '{ent.text}' | Label: {ent.label_} | Start: {ent.start_char} | End: {ent.end_char}")

print("\n=== Token-Analyse ===")
for token in doc:
    print(f"Token: '{token.text}' | POS: {token.pos_} | Tag: {token.tag_} | Dep: {token.dep_} | NER: {token.ent_type_}")
