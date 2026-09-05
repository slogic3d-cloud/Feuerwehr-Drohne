# Projekt — Werkzeuge für die Feuerwehr

Zwei Projekte für die Freiwillige Feuerwehr, beide praxistauglich gedacht und
ohne Installationsaufwand benutzbar.

## 🚒 [Einsatz-Helfer](index.html)

Eine einzelne HTML-Datei, die **offline** auf Handy oder Tablet an der
Einsatzstelle läuft:

* **Atemschutzüberwachung** — Einsatzuhr je Trupp, 10-Minuten-Countdown für die
  Druckkontrolle, automatisch berechneter Rückzugsdruck, Ampel und Alarmton
* **Einsatztagebuch** — Zeitstempel automatisch, Schnellwahl der üblichen Meldungen
* **Rechner** — Pumpenausgangsdruck, Luftvorrat, Wasserbedarf, Schaummittel
* **Bericht** als TXT, Backup als JSON, Druckansicht

`index.html` im Browser öffnen — fertig. Details in der
[Beschreibung weiter unten](#einsatz-helfer-im-detail).

> ⚠️ Hilfsmittel. Ersetzt weder die Atemschutzüberwachung nach FwDV 7 noch die
> Überwachungstafel.

## 🔎 [Personensuche mit Drohne](drohne/)

Software für eine selbstgebaute Suchdrohne: Wärmebildkamera nach unten,
Auswertung an Bord, Trefferalarm mit GPS-Koordinate aufs Tablet.

* [Technisches Konzept](drohne/KONZEPT.md) — Physik, Bauteilliste (600 €),
  Rechtslage, Stufenplan
* Läuft **sofort im Simulationsmodus**, ganz ohne Hardware:
  `cd drohne/sensor && python3 suchkopf.py`
* Bildstabilisierung gegen Wind, lernender Klassifikator, 84 Tests

> ⚠️ Eigenbauprojekt, kein zugelassenes Einsatzmittel.

---

## Einsatz-Helfer im Detail

### Atemschutzüberwachung
Trupps mit Namen, Auftrag und Startdruck erfassen; die Einsatzuhr läuft mit.
Der Rückzugsdruck wird automatisch berechnet — doppelter Anmarschverbrauch plus
70 bar Sicherheit, ersatzweise die Ein-Drittel-Regel, solange kein Druck am
Einsatzziel gemeldet ist. Bei Rot gibt es Alarmzeile und Signalton, und das
Display bleibt während der Überwachung wach.

### Rechengrundlagen

| Größe | Formel / Wert |
|---|---|
| Druckverlust | Δp = k · (Q/100)² je 100 m; k = 0,0047 (A-110), 0,028 (B-75), 0,175 (C-52), 0,55 (C-42), 4,0 (D-25) |
| Höhendifferenz | 1 bar je 10 m |
| Rückzugsdruck | 2 × (Startdruck − Druck am Einsatzziel) + 60 bar Warnpfiff + 10 bar Reserve |
| Ein-Drittel-Regel | Rückzug bei ⅓ des Startdrucks, mindestens 60 bar |
| Luftvorrat | (aktueller Druck − Reserve) × Flaschenvolumen ÷ Atemminutenvolumen |
| Strahlrohre | Richtwerte bei 5 bar: C mit MS 100, C ohne MS 200, C-Hohlstrahl 235, B mit MS 400, B ohne MS 800 l/min |

Verteiler, Armaturen und Einzelfälle sind in den Näherungen **nicht** enthalten
— an der Pumpe wird am Manometer nachgeregelt.

### Wo liegen die Daten?
Ausschließlich im `localStorage` des jeweiligen Geräts. Nichts wird
hochgeladen. Umgekehrt heißt das: Browserdaten löschen löscht die Einsatzdaten.
**Nach dem Einsatz den Bericht exportieren.**
