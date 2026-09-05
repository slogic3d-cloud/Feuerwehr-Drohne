# Personensuche mit Drohne — Technisches Konzept

**Für: Freiwillige Feuerwehr Ebersdorf bei Coburg (Florian Ebersdorf)**
**Stand: September 2026 · Eigenbauprojekt, noch kein Einsatzmittel**

---

## 1. Was das Gerät können soll

Eine Drohne, die bei **Vermisstensuchen im Freien** aus der Luft nach Personen
sucht: Wärmebildkamera nach unten, automatische Auswertung an Bord, Livebild
und Trefferalarm aufs Tablet, GPS-Koordinate jeder Fundstelle.

Typische Lagen:

* Vermisste, hilflose oder demente Person, Suchgebiet Feld, Wiese, Waldrand
* Kind vermisst, große Fläche in kurzer Zeit absuchen
* Person nach Verkehrsunfall aus dem Fahrzeug geschleudert, Nachtsuche
* Personensuche nach Gewässerunfall im Uferbereich

**Ausdrücklich nicht** vorgesehen: Innenraumerkundung, Brandbekämpfung, Flug in
Rauch oder Hitze. Das war eine frühere Projektidee und wurde verworfen — die
Anforderungen widersprechen sich (drinnen zählt Wendigkeit und Kollisionsschutz,
draußen Flugzeit und Sichtfeld).

---

## 2. Die ehrlichen Grenzen — bitte zuerst lesen

Diese Punkte entscheiden darüber, ob das Gerät im Einsatz hilft oder falsche
Sicherheit erzeugt:

| Grenze | Was das bedeutet |
|---|---|
| **Wild sieht aus wie Mensch** | Reh, Wildschwein und Hund haben im Wärmebild praktisch dieselbe Signatur wie ein liegender Mensch. Die Software kann das **nicht** sicher trennen. Jeder Treffer muss vom Bediener am Bild geprüft werden. |
| **Laubdach blockiert** | Unter dichtem Blätter- oder Nadeldach ist eine Person aus der Luft unsichtbar. Im Sommerwald ist die Drohne nahezu wirkungslos, im Winterwald deutlich besser. |
| **Mittagshitze** | Wenn der Boden sonnenwarm ist, verschwindet der Temperaturunterschied zum Menschen. Beste Bedingungen: **nachts und in den frühen Morgenstunden**, kalter Boden, trocken. |
| **Regen und Nebel** | Wassertropfen dämpfen die Wärmestrahlung. Bei Regen sinkt die Reichweite deutlich, bei dichtem Nebel geht praktisch nichts. |
| **Kein Ersatz für die Fläche** | Die Drohne ersetzt keine Suchkette und keinen Rettungshund. Sie ist ein Werkzeug, das Flächen vorsortiert. |
| **Rechtlicher Rahmen** | Ein selbstgebautes Gerät ohne C-Klassifizierung darf in der offenen Kategorie nur in **A3** fliegen — mindestens 150 m Abstand zu Wohn- und Gewerbegebieten. Für den Einsatzflug über bewohntem Gebiet braucht die Wehr eine eigene Genehmigung (siehe Abschnitt 8). |

---

## 3. Physik: was die Kamera aus welcher Höhe sieht

Alles folgt aus einer einzigen Formel — der Streifenbreite am Boden:

```
Streifenbreite = 2 × Flughöhe × tan(Bildwinkel / 2)
```

Mit der vorgesehenen Kamera (256 Pixel quer, 45,6° Bildwinkel quer):

| Flughöhe | Streifenbreite | cm je Pixel | Person (1,75 m) |
|---:|---:|---:|---:|
| 20 m | 16,8 m | 6,6 cm | 27 Pixel |
| 30 m | 25,2 m | 9,9 cm | 18 Pixel |
| **40 m** | **33,6 m** | **13,1 cm** | **13 Pixel** |
| 60 m | 50,4 m | 19,7 cm | 9 Pixel |
| 80 m | 67,3 m | 26,3 cm | 7 Pixel |

Unter etwa **8 Pixel Körperlänge** geht eine Person im Bodenrauschen unter.
Daraus folgt die Obergrenze von rund **66 m**. Empfohlene Arbeitshöhe:
**40 m** — genug Reserve, gute Flächenleistung.

**Flächenleistung** bei 40 m, 8 m/s und 25 % Bahnüberlappung:

```
Bahnabstand   25,2 m
Flächenrate   1,21 ha je Minute
Ein Akku (30 min)  ≈ 36 ha  ≈ ein Gebiet von 600 × 600 m
```

Zum Vergleich: Eine Suchkette mit 20 Kräften schafft dieselbe Fläche in
deutlich mehr Zeit — und sieht dabei anderes als die Drohne. Beides ergänzt
sich, keines ersetzt das andere.

---

## 4. Aufbau

```
                    ┌─────────────────────────────┐
                    │  7-Zoll-Quadrocopter        │
                    │  ArduPilot auf F405         │
                    │  Li-Ion 6S2P · 30–35 min    │
                    └──────────┬──────────────────┘
                               │
       ┌───────────────────────┼────────────────────────┐
       │                       │                        │
┌──────▼──────┐        ┌───────▼────────┐      ┌────────▼────────┐
│ Wärmebild   │  USB   │ Raspberry Pi   │ UART │ GPS / Kompass   │
│ P2 Pro      ├───────►│ Zero 2 W       │◄─────┤ M10             │
│ 256×192     │        │  Suchkopf      │      └─────────────────┘
└─────────────┘        │  (Python)      │
                       └───────┬────────┘
                               │ WLAN (später zusätzlich LTE)
                       ┌───────▼────────┐
                       │ Tablet         │
                       │ Bodenstation   │
                       └────────────────┘
       ELRS-Fernsteuerung ───► Flugregler   (getrennter, vorrangiger Weg)
```

Zwei getrennte Wege sind Absicht: **Fliegen** läuft über die
ELRS-Fernsteuerung direkt zum Flugregler und ist damit unabhängig von Pi,
WLAN und Tablet. **Sehen und Auswerten** läuft über den Pi. Fällt der Pi aus,
fliegt die Drohne weiter und kommt nach Hause.

---

## 5. Bauteilliste

### Zelle und Antrieb

| Teil | Auswahl | Preis |
|---|---|---:|
| Rahmen | 7-Zoll-Langstreckenrahmen, Carbon | 40 € |
| Motoren | 4 × 2807, ca. 1300 KV | 60 € |
| Regler | 4-in-1, 45 A, 6S | 40 € |
| Flugregler | F405-Stack, ArduPilot-tauglich | 40 € |
| Propeller | 7 Zoll, 3 Sätze | 15 € |
| GPS + Kompass | M10-Modul | 25 € |
| Empfänger | ELRS 2,4 GHz | 15 € |
| | **Zwischensumme** | **235 €** |

### Energie

| Teil | Auswahl | Preis |
|---|---|---:|
| Akku | Li-Ion 6S2P (P42A), 8,4 Ah / 180 Wh — 30–40 min | 120 € |
| Akku, leichte Alternative | Li-Ion 6S1P, 4,2 Ah — 20–25 min | 65 € |
| Ladegerät | muss Li-Ion können, falls nicht vorhanden | 45 € |

Li-Ion statt LiPo ist die wichtigste Einzelentscheidung für die Flugzeit:
etwa doppelte Energiedichte bei geringerem Dauerstrom — für ruhigen
Suchflug genau richtig, für Kunstflug ungeeignet.

### Nutzlast

| Teil | Auswahl | Preis |
|---|---|---:|
| Wärmebild | InfiRay P2 Pro oder Topdon TC001, 256×192, 9 g | 230 € |
| Rechner | Raspberry Pi Zero 2 W + SD-Karte | 30 € |
| Positionslicht | grün blinkend — für Nachtflug vorgeschrieben | 10 € |
| Halter | 3D-Druck ABS / ABS-CF, Eigenfertigung | 5 € |
| | **Zwischensumme** | **275 €** |

### Fernsteuerung

| Teil | Auswahl | Preis |
|---|---|---:|
| Sender | RadioMaster Pocket ELRS, falls nicht vorhanden | 70 € |

### Summen

| Fall | Betrag |
|---|---:|
| **Hauptteile, wenn Sender und Ladegerät vorhanden sind** | **630 €** |
| Vollständig inklusive Kleinteile und Werkzeug | 715–900 € |
| Später nachrüstbar: LTE-Modem SIM7600 + Tarif | + 55 € |

Die vollständige Einkaufsliste mit allen Kleinteilen, Stückzahlen und
Kaufhinweisen steht in **[TEILELISTE.md](TEILELISTE.md)** — diese Tabelle hier
nennt nur die Hauptposten.

**Sparmöglichkeiten, falls es enger wird:** LiPo 6S statt Li-Ion spart 25 €
(kostet aber ein Drittel der Flugzeit). Ein 5-Zoll-Rahmen spart 30 € (kostet
ebenfalls Flugzeit). **Nicht sparen** an der Wärmebildkamera — der billige
MLX90640 mit 32×24 Pixeln würde aus 40 m eine Person auf weniger als einen
Bildpunkt abbilden und ist für diesen Zweck unbrauchbar.

---

## 6. Software

Der komplette Code liegt in diesem Verzeichnis und läuft **ohne
Fremdbibliotheken** — reines Python 3, kein numpy, kein OpenCV nötig (außer
für die USB-Kamera selbst). Das ist auf einem Pi Zero die robustere Wahl:
nichts, was beim Systemupdate zerbricht.

| Datei | Aufgabe |
|---|---|
| `sensor/suchkopf.py` | Hauptprogramm auf der Drohne, Taktschleife |
| `sensor/erkennung.py` | Fleckensuche und Bewertung im Wärmebild |
| `sensor/suchflug.py` | Geometrie: Streifenbreite, Suchhöhe, Georeferenzierung, Suchmuster |
| `sensor/stabilisierung.py` | Bildstabilisierung bei Wind, Fleckverfolgung über mehrere Bilder |
| `sensor/lernen.py` | Lernender Klassifikator, trainiert aus den Bewertungen am Tablet |
| `sensor/treffer.py` | Trefferverwaltung, Speicherung als JSON + Bild |
| `sensor/web.py` | HTTP-Server und Ereignisstrom zur Bodenstation |
| `sensor/geraete/` | Treiber für Wärmebildkamera und GPS, jeweils mit Simulation |
| `bodenstation/index.html` | Oberfläche fürs Tablet |

### Wie erkannt wird

Aus 40 m Höhe ist ein Mensch **kein 33-Grad-Körper** mehr — Luft dämpft, und
jeder Bildpunkt mischt Person und Untergrund. Bewertet wird deshalb der
**Kontrast zum Boden**, nach drei Merkmalen:

1. **Abhebung** — wie viel wärmer als der Untergrund? Nachts auf kalter Wiese
   sind 5–9 K realistisch. Zu wenig ist ein warmer Stein, zu viel ist Technik.
2. **Größe** — aus der Flughöhe ist ausrechenbar, wie viele Bildpunkte eine
   liegende Person haben *muss*. Alles deutlich Größere ist Weg, Dach oder Feld.
3. **Form** — ein Mensch ist kompakt. Lange dünne Streifen sind aufgeheizte
   Wege, Mauern und Leitplanken.

Dazu kommt die **Beständigkeit**: ein Fleck, der nur in einem einzigen Bild
auftaucht, ist bei Wind meist ein Verwackler. Erst was über mehrere Bilder
hinweg an derselben Stelle bleibt, zählt voll.

### Bildstabilisierung bei Wind

Der Flugregler stabilisiert die **Fluglage** — das kann keine Software auf dem
Pi. Was der Suchkopf stabilisiert, ist das **Bild**: Zwischen zwei Aufnahmen
wird der Versatz geschätzt und herausgerechnet, damit derselbe Fleck über
mehrere Bilder hinweg wiedererkannt wird.

Nebenprodukt ist eine **Böigkeitsanzeige**: Der gleichmäßige Anteil des
Bildversatzes ist der Vorwärtsflug, der zappelnde Rest ist Wind. Wird es zu
unruhig, warnt das Tablet und die Bewertung wird vorsichtiger.

### Der lernende Klassifikator

Kein neuronales Netz — das läuft auf einem Pi Zero nicht in Echtzeit, und die
Tausenden beschrifteten Wärmebilder, die es bräuchte, gibt es für diesen Zweck
nicht frei.

Stattdessen eine **logistische Regression** über acht Merkmale, trainiert aus
genau den Klicks, die der Bediener am Tablet macht: „Person" oder „Fehlalarm".
Jede bewertete Fundstelle wird gespeichert; nach ein paar Übungsflügen über
bekannte Ziele kennt das Modell die örtlichen Verhältnisse besser als jede von
Hand gesetzte Schwelle.

```bash
python3 lernen.py            # trainiert aus dem Ordner treffer/
```

Das Modell ersetzt die Regeln nicht, sondern wird mit ihnen gemischt — und
zwar umso stärker, je mehr Beispiele es gesehen hat. Mit drei Beispielen
entscheidet weiterhin die Regel. Acht Gewichte, die man sich ansehen kann; das
Programm gibt sie beim Training aus.

**Ausbaupfad:** Wenn später ein Raspberry Pi 5 oder ein Jetson mitfliegt, ist
ein echtes Bilderkennungsnetz möglich. Die Schnittstelle in `lernen.py` bleibt
dieselbe, nur die Bewertungsfunktion wird ausgetauscht.

---

## 7. Ablauf im Einsatz

**Vorbereitung (läuft ohne Einsatzdruck)**

1. Suchgebiet mit der Einsatzleitung festlegen, Startpunkt mit freier Sicht wählen
2. Drohne aufbauen, Akku einsetzen, GPS-Empfang abwarten
3. Tablet mit dem WLAN der Drohne verbinden, Bodenstation öffnen
4. Flughöhe eingeben — der Suchplan rechnet Bahnabstand und Flächenleistung aus

**Suchflug**

5. Bahnen möglichst **gegen den Wind** legen (ruhigeres Bild, gleichmäßigere Geschwindigkeit)
6. Konstant 6–8 m/s, Höhe halten
7. Bei Alarm: Bild ansehen, Form prüfen — Mensch oder Wild?
8. Fundstelle als „Person" oder „Fehlalarm" markieren (das trainiert zugleich das Modell)
9. Koordinate kopieren und an die Einsatzleitung geben

**Nachbereitung**

10. Ordner `treffer/` sichern
11. `python3 lernen.py` laufen lassen — das Modell wird besser

---

## 8. Rechtliches — das ist vor dem ersten Einsatz zu klären

> Das ist eine Sammlung der Punkte und Ansprechstellen, **keine Rechtsberatung**.
> Vor dem ersten Einsatzflug gehört das über die Kreisbrandinspektion geklärt.

* **Betreiberregistrierung** beim Luftfahrt-Bundesamt (e-ID), Kennzeichnung am Gerät.
* **Kompetenznachweis A1/A3** — Online-Prüfung beim LBA, kostenlos, ein Nachmittag.
* **Kategorie:** Ein privat gebautes Gerät ohne C-Klassifizierung über 250 g darf
  in der offenen Kategorie nur in **A3** fliegen: mindestens 150 m Abstand zu
  Wohn-, Gewerbe-, Industrie- und Erholungsgebieten. Für Flüge darüber hinaus
  braucht es eine **Betriebsgenehmigung in der speziellen Kategorie** oder eine
  BOS-Ausnahme.
* **Zuständige Behörde für Oberfranken:** Luftamt Nordbayern (Regierung von
  Mittelfranken, Nürnberg). Dort laufen Ausnahmegenehmigungen für BOS.
* **Nachtflug** ist in der offenen Kategorie zulässig, wenn ein **grün
  blinkendes Positionslicht** vorhanden ist — deshalb steht es in der Bauteilliste.
* **Versicherung:** Halterhaftpflicht ist Pflicht. Für ein Feuerwehrgerät muss
  der kommunale Versicherer eingebunden werden — die private Drohnenversicherung
  deckt Einsatzflüge in der Regel nicht.
* **Datenschutz:** Wärmebildaufnahmen von Personen und Grundstücken sind
  personenbezogene Daten. Deshalb speichert die Software bewusst **nur
  Treffer**, keinen Dauermitschnitt.

---

## 9. Stufenplan

Jede Stufe ist für sich abgeschlossen und bringt schon etwas — wichtig bei
einem Projekt, das nebenbei läuft.

| Stufe | Inhalt | Aufwand | Kosten |
|---|---|---|---:|
| **1** | Wärmebildkamera + Pi auf dem Tisch, Software läuft, Erkennung mit der Hand durch den Garten getestet | 2 Wochenenden | 260 € |
| **2** | Flugzelle aufbauen, ArduPilot einrichten, ohne Nutzlast fliegen lernen | 3–4 Wochenenden | 325 € |
| **3** | Nutzlast montieren (3D-Druck-Halter), Schwerpunkt und Flugzeit prüfen | 1 Wochenende | 15 € |
| **4** | Übungsflüge über bekannte Ziele: Helfer legt sich auf die Wiese, Trefferquote messen, Modell trainieren | laufend | 0 € |
| **5** | Der Wehrführung vorführen, Genehmigungen und Versicherung klären | — | — |
| **6** | Optional LTE nachrüsten — Livebild für Einsatzleitung und Leitstelle | 1 Wochenende | 55 € |

Zwischen Stufe 1 und 2 liegt der eigentliche Bruch: **erst wenn die Erkennung
am Boden zuverlässig funktioniert, lohnt sich das Fliegen.** Und Stufe 4 ist
die wichtigste — ohne gemessene Trefferquote über bekannte Ziele weiß niemand,
ob das Gerät im Ernstfall etwas taugt.

---

## 10. Was als nächstes ansteht

- [ ] Wärmebildkamera bestellen und mit `WAERMEBILD_TYP=infiray` an den Pi hängen
- [ ] Erkennung im Garten gegen bekannte Ziele prüfen, Schwellen in `konfig.py` nachziehen
- [ ] Halter für Kamera und Pi in CAD konstruieren, in ABS drucken
- [ ] Flugzelle aufbauen, ArduPilot einrichten, Failsafes setzen
- [ ] Übungsflüge bei Nacht über abgemähter Wiese, Trefferquote dokumentieren
- [ ] Genehmigungslage mit der Kreisbrandinspektion klären
