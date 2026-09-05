# Einsatz-Helfer Feuerwehr

Ein Helfer für die Einsatzstelle – läuft als **einzelne HTML-Datei** offline auf
Handy, Tablet oder Laptop. Keine Installation, kein Server, kein Konto.

> ⚠️ **Wichtig:** Die Atemschutzüberwachung in dieser App ist ein *Hilfsmittel*.
> Sie ersetzt weder die Atemschutzüberwachung nach **FwDV 7** noch die
> Überwachungstafel. Die Anzeige am Gerät und die Uhr am Trupp gelten immer vor
> der App. Alle Rechenwerte sind Näherungen und ersetzen keine Ausbildung.

## Was drin ist

**🫁 Atemschutzüberwachung**
- Trupps mit Namen, Auftrag und Startdruck erfassen, Einsatzuhr läuft mit
- Countdown bis zur nächsten Druckkontrolle (10-Minuten-Intervall nach FwDV 7)
- Rückzugsdruck automatisch: doppelter Anmarschverbrauch + 70 bar Sicherheit,
  ersatzweise die Ein-Drittel-Regel, solange kein Druck am Einsatzziel gemeldet ist
- Ampel je Trupp (grün / gelb / rot), Alarmzeile und Signalton bei Rot
- Display bleibt während der Überwachung wach (sofern der Browser das kann)

**📝 Einsatztagebuch**
- Zeitstempel automatisch, Schnellwahl für die üblichen Meldungen
  (Eintreffen, Wasser marsch, Feuer aus, Einrücken …)
- Alles aus der Atemschutzüberwachung wird automatisch mitprotokolliert

**🧮 Rechner**
- Benötigter Pumpenausgangsdruck (Schlauchart, Länge, Durchfluss, Höhe)
- Verbleibende Einsatzzeit aus Flaschendruck und Atemminutenvolumen
- Wasserbedarf und Tankreichweite
- Schaummittelbedarf und Reichweite des Vorrats

**⚙️ Daten**
- Einsatzbericht als TXT (Trupps, Druckkontrollen, komplettes Tagebuch)
- Backup als JSON, Druck-/PDF-Ansicht
- Abgeschlossene Einsätze im Archiv

## Benutzen

`index.html` im Browser öffnen – fertig.

**Auf dem Handy als App:** Datei über einen beliebigen Weg öffnen (oder auf einer
Webseite ablegen), dann im Browser *Teilen → Zum Home-Bildschirm*. Danach startet
sie wie eine normale App und funktioniert ohne Netz.

## Wo liegen die Daten?

Ausschließlich im `localStorage` des Browsers auf dem jeweiligen Gerät. Nichts
wird hochgeladen, es gibt keine Server-Verbindung. Umgekehrt heißt das: Wer die
Browserdaten löscht, löscht die Einsatzdaten. **Nach dem Einsatz den Bericht
exportieren.**

## Rechengrundlagen

| Größe | Formel / Wert |
|---|---|
| Druckverlust | Δp = k · (Q/100)² je 100 m; k = 0,0047 (A-110), 0,028 (B-75), 0,175 (C-52), 0,55 (C-42), 4,0 (D-25) |
| Höhendifferenz | 1 bar je 10 m |
| Rückzugsdruck | 2 × (Startdruck − Druck am Einsatzziel) + 60 bar Warnpfiff + 10 bar Reserve |
| Ein-Drittel-Regel | Rückzug bei ⅓ des Startdrucks, mindestens 60 bar |
| Luftvorrat | (aktueller Druck − Reserve) × Flaschenvolumen ÷ Atemminutenvolumen |
| Strahlrohre | Richtwerte bei 5 bar: C mit MS 100, C ohne MS 200, C-Hohlstrahl 235, B mit MS 400, B ohne MS 800 l/min |

Verteiler, Armaturen und Einzelfälle sind in den Näherungen **nicht** enthalten –
an der Pumpe wird am Manometer nachgeregelt.
