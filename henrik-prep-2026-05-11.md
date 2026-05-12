# Henrik-Gespraech: Anker-Fragen
Datum: 2026-05-11

Ziel: 5 Minuten Kontext holen damit ich in die richtige Richtung loslaufe.

---

## Den Auftrag verstehen

- "Was soll am Ende rauskommen?"
=> Service, den ich per API ansprechen kann, dem ich ein Dokument geben kann. Der daraus den Inhalt extrahiert und schwärzt. Input (PDF, auch gescannt, text- und bildbasiert). Output: in einer Form, die Claude Code verarbeiten kann.
=> Bisher in .NET gebaut für Scannen. Schwärzung per Regex. => gern Open Source und mit kleinerem Model (z.b. Hetzner-Server mit 250€ pro Monat). Mimir läuft auf Gemma 4 (RTX 6000 mit 96GB)
- "Was davon kommt vom Kanzlei-Chef, was kommt von dir?"
=> Kanzlei-Chef: 
- gibt kurze Liste, was er gern hätte. Und diese möchte er zu Claude schicken können.
- "Können wir uns die 1000€ im Monat sparen?" (er hat viel Halbwissen, er geht ins Internet und bekommt Werbung für Dokumentschwärzung für 20€/User/Jahr)

## Den Scope verstehen

- "Geht es nur um die Schwaerzung, oder steckt da mehr dahinter?"
=> geht um Schwärzung, kann es als Docker laufen? Damit es nach Claude gesendet werden kann.
- "Die Tabellen und Rechnungen die erwaehnt wurden — war das ein konkreter Wunsch
  vom Chef, oder eher so ein 'waere auch cool'?"
- "Welche Zuverlässigkeit braucht die Kanzlei?" => Fehlerquote von 3%

## Meine Rolle verstehen

- "Wie eigenstaendig soll ich das machen? Soll ich einfach loslegen und dir
  Ergebnisse zeigen, oder willst du zwischendurch eingebunden sein?"
- "Welche Entscheidungen darf ich eigenstaendig treffen, welche moechtest du erst absegnen?"

## Zum Schluss

- "Okay, ich fass kurz zusammen was ich verstanden habe: [...]  — passt das so?"
- Deadline: in 1 Woche ist 1 Kategorie integriert und ausprobierbar.