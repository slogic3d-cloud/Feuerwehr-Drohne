# Personensuche mit Drohne

Software für eine selbstgebaute Suchdrohne der Freiwilligen Feuerwehr
Ebersdorf bei Coburg: **Wärmebildkamera nach unten, Auswertung an Bord,
Trefferalarm mit GPS-Koordinate aufs Tablet.**

* **[PLAN.md](PLAN.md)** — der Arbeitsplan: was in welcher Reihenfolge zu tun
  ist und womit man anfängt
* **[KONZEPT.md](KONZEPT.md)** — das technische Konzept: Physik, Bauteilliste,
  Rechtslage, Grenzen des Verfahrens
* **[messprotokoll.html](messprotokoll.html)** — Messprotokoll zum Ausdrucken
  für den Nachtversuch und die späteren Flugversuche (braucht nur einen Browser)

> ⚠️ Eigenbauprojekt, kein zugelassenes Einsatzmittel. Wild und Haustiere
> sehen im Wärmebild aus wie Menschen — **jeder Treffer muss vom Bediener am
> Bild geprüft werden.** Rechtliche Voraussetzungen siehe Konzept, Abschnitt 8.

## Sofort ausprobieren — ganz ohne Hardware

```bash
cd sensor
python3 suchkopf.py
```

Dann `http://localhost:8080/` im Browser öffnen. Es läuft ein simulierter
nächtlicher Suchflug: kalte Wiese, ein sonnenwarmer Feldweg, ein Steinhaufen,
ein Auto mit heißer Motorhaube — und eine Person. Die Erkennung muss beweisen,
dass sie nur die Person meldet.

```bash
python3 suchkopf.py --pruefen     # einmal auswerten, Ergebnis auf der Konsole
python3 -m unittest discover -s ../tests    # 84 Tests
```

Es wird **nichts installiert**: reines Python 3 aus der Standardbibliothek.
OpenCV braucht nur der Treiber der echten USB-Wärmebildkamera.

## Mit echter Hardware

```bash
WAERMEBILD_TYP=infiray WAERMEBILD_QUELLE=/dev/video0 \
GPS_QUELLE=/dev/ttyAMA0 FLUGHOEHE_M=40 python3 suchkopf.py
```

Alle Einstellungen stehen in `sensor/konfig.py` und lassen sich über
Umgebungsvariablen überschreiben — an der Einsatzstelle muss niemand Code
anfassen.

## Aufbau

| Datei | Aufgabe |
|---|---|
| `sensor/suchkopf.py` | Hauptprogramm, Taktschleife |
| `sensor/erkennung.py` | Fleckensuche und Bewertung im Wärmebild |
| `sensor/suchflug.py` | Streifenbreite, Suchhöhe, Georeferenzierung, Suchmuster |
| `sensor/stabilisierung.py` | Bildstabilisierung bei Wind, Fleckverfolgung |
| `sensor/lernen.py` | Lernender Klassifikator aus den Bewertungen am Tablet |
| `sensor/treffer.py` | Trefferverwaltung, Speicherung als JSON + PGM-Bild |
| `sensor/web.py` | HTTP-Server und Ereignisstrom zur Bodenstation |
| `sensor/geraete/` | Treiber Wärmebild und GPS, jeweils mit Simulation |
| `bodenstation/index.html` | Oberfläche fürs Tablet |
| `tests/` | 84 Tests, laufen ohne Hardware |

## Wie erkannt wird

Aus 40 m Höhe ist ein Mensch kein 33-Grad-Körper mehr — Luft dämpft, jeder
Bildpunkt mischt Person und Untergrund. Bewertet wird deshalb der **Kontrast
zum Boden** nach drei Merkmalen: **Abhebung** (5–9 K nachts auf kalter Wiese),
**Größe** (aus der Flughöhe ist ausrechenbar, wie viele Bildpunkte eine
liegende Person haben muss) und **Form** (kompakt, nicht langgestreckt wie ein
aufgeheizter Weg).

Dazu die **Beständigkeit**: Ein Fleck, der nur in einem einzigen Bild
auftaucht, ist bei Wind meist ein Verwackler.

## Das Modell trainieren

Jede Fundstelle wird gespeichert. Wer sie am Tablet als „Person" oder
„Fehlalarm" markiert, erzeugt damit Trainingsdaten:

```bash
python3 lernen.py            # trainiert aus dem Ordner treffer/
```

Das Modell (logistische Regression über acht Merkmale) ersetzt die Regeln
nicht, sondern wird mit ihnen gemischt — umso stärker, je mehr Beispiele es
gesehen hat. Mit drei Beispielen entscheidet weiterhin die Regel.

## Datenschutz

Gespeichert werden **nur Treffer**, kein Dauermitschnitt: Wärmebildaufnahmen
von Personen und Grundstücken sind personenbezogene Daten.
