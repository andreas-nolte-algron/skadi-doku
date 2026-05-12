# Stakeholder-Kontext

Stand: 2026-05-11

## Algron (Auftragnehmer)

Kleine IT-Firma (~5 Personen). Baut und betreibt die Skadi-Pipeline fuer Kanzlei Voigt.

| Person | Rolle | Relevanz fuer skadi-doku |
|--------|-------|--------------------------|
| Henrik | CEO + Chef-Entwickler | Entscheidet Scope/Budget. Interface zur Kanzlei. Doppelrolle: Business + Tech-Meinung. [W] |
| Andi | KI-Manager + Unternehmensentwicklung | Baut Skadi-Pipeline, fuehrt technische Research durch. Kein Entwickler. Kein direkter Kanzlei-Kontakt. [W] |
| LLM-Entwickler | Hat Mimir gebaut, betreut GPU-Infrastruktur | Relevant fuer Mimir-vs-Alternative-Entscheidungen und Infra-Fragen. [W] |
| Weiterer Entwickler | Arbeitet ebenfalls an Skadi, aber nicht am neuen Projekt! | [O] Genaue Zustaendigkeit unklar. |
| Paula | User Stories, Kundenfeedback-Optimierung | Sitzt in Strategie-Meetings. Keine Entwicklerin. [W] Moeglicherweise existierende User Stories fuer skadi-doku? [O] |

## Kanzlei Voigt (Hauptkunde)

Anwaltskanzlei mit vielen Niederlassungen. [W]

| Person/Einheit | Rolle | Relevanz fuer skadi-doku |
|----------------|-------|--------------------------|
| Kanzlei-Chef | Treibt Anforderungen, definiert Prioritaeten | Quelle des Tabellen/Rechnungen-Signals. [W] |
| EDV-Abteilung | Eine Abteilung fuer gesamte Kanzlei | Bottleneck fuer Deployment/Wartung on-prem. [A] Name/Kontakt unbekannt. [O] |
| Endnutzer | Anwaelte, Sekretariat? | [O] Wer genau bedient Skadi? Welche Niederlassungen? Hier fehlt uns bei algron Infos, die wir erst in ein paar Monaten bekommen, aber nicht rechtzeitig |
| Datenschutzbeauftragter | Unklar ob vorhanden | [O] Relevant fuer DSGVO-Entscheidungen. |

## Entscheidungsfluss

```
Kanzlei-Chef  →  WAS      (Anforderungen, Prioritaeten, Schmerzpunkte)
       ↕
Henrik         →  SCOPE    (Was Algron uebernimmt, Zeitrahmen, Budget)
       ↕
Andi           →  WIE      (Architektur, Tech-Stack, Implementierung)
```

## Kommunikation

- **Andi ↔ Henrik:** Technische Strategie. Tool: `/strategie-sync`. [W]
- **Henrik ↔ Kanzlei-Chef:** Geschaeftliche Abstimmung. [W]
- **Andi ↔ Kanzlei:** Aktuell kein direkter Kanal. Alles ueber Henrik. [W]
- **Paula:** In Strategie-Meetings dabei, liefert Kundenfeedback. [W] Kanal zu skadi-doku? [O]

## Signale vom Kunden

- Kanzlei will neben PDFs auch **Tabellen, Rechnungen und weitere Formate** verarbeiten. Zweck noch unklar. [W]
- Viele Niederlassungen → Volumen potenziell hoeher als angenommen. [A]

## Offene Punkte

- [ ] Name/Rolle der EDV-Person bei Voigt?
- [ ] Datenschutzbeauftragter bei Voigt vorhanden?
- [ ] Hat Paula User Stories / Anforderungsdokumente fuer skadi-doku?
- [ ] Zustaendigkeit des zweiten Skadi-Entwicklers?
- [ ] Welche Niederlassungen nutzen Skadi / sollen es nutzen?
- [ ] AVV (Auftragsverarbeitungsvertrag) zwischen Algron und Voigt vorhanden?
