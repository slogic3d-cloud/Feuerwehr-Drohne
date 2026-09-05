# Kamerahalter — Konstruktionsunterlage

Vier gedruckte Teile, die Wärmebildkamera und Raspberry Pi an die Drohne
bringen. Die Maßzeichnungen stehen in
**[gehaeuse-zeichnung.html](gehaeuse-zeichnung.html)** — im Browser öffnen und
ausdrucken, du brauchst dafür kein Python.

> Die Zeichnung wird aus `werkzeuge/zeichnung_gehaeuse.py` erzeugt. Wenn ein Maß
> geändert wird, wird es dort geändert und die Zeichnung neu erzeugt — so gibt
> es nie zwei Wahrheiten.

---

## Die vier Teile

| Teil | Größe | Aufgabe |
|---|---|---|
| **1 · Grundplatte** | 84 × 54 × 3 mm | Wird direkt unter die Rahmenunterseite geschraubt. Trägt die vier Dämpferkugeln. |
| **2 · Kameraträger** | 76 × 48 × 3 mm | Hängt gedämpft darunter. Taschenwände zeigen **nach unten**, die Kamera wird von unten eingelegt. |
| **3 · Deckel** | 40 × 28 × 2 mm | Wird von unten angeschraubt und hält die Kamera in der Tasche. Ø 14 mm Fenster fürs Objektiv. |
| **4 · Pi-Wanne** | 71 × 36 × 2 mm, Rand 6 mm | Nimmt den Raspberry Pi auf, kommt oben aufs Rahmendeck neben den Akku. |

### Warum der Pi nicht an der Grundplatte hängt

Der erste Entwurf hatte den Pi oben auf der Grundplatte und die Kameratasche
nach oben geöffnet. Im Seitenschnitt kam heraus: Die Kamera hätte in den Bauraum
zwischen Grundplatte und Kameraträger geragt und wäre mit der Grundplatte
kollidiert. Der Weg drumherum — die Platten weiter auseinanderzuziehen — hätte
die Bauhöhe unter dem Rahmen auf 40 mm getrieben, und dann bräuchte die Drohne
längere Landebeine.

Die Lösung: Tasche nach unten öffnen, Deckel dazu, Pi in eine eigene Wanne aufs
Rahmendeck. Ergebnis **27 mm unter dem Rahmen** statt 40, und jedes Teil hat
genau eine Aufgabe.

---

## Der Aufbau von oben nach unten

| Höhe unter dem Rahmen | Was |
|---:|---|
| 0 mm | Rahmenunterseite |
| 0–3 mm | Grundplatte, direkt angeschraubt |
| 3–11 mm | vier Dämpferkugeln, 8 mm |
| 11–14 mm | Kameraträger |
| 14–25 mm | Kameratasche, Wände nach unten |
| 25–27 mm | Deckel mit Objektivfenster |

**Die Landebeine müssen mindestens 40 mm Bodenfreiheit geben** — sonst setzt der
Deckel beim Landen zuerst auf.

---

## Lochbilder

| Wofür | Bohrung | Rastermaß | Bemerkung |
|---|---|---|---|
| Rahmenbefestigung | ⌀ 3,2 mm | 30,5 × 30,5 | Standardmaß für Flugregler-Stapel |
| Rahmen, abweichend | Langloch 3,2 × 16 mm | ± 36 in x | gleicht andere Rahmen aus |
| Dämpferkugeln | ⌀ 6,2 mm | 64 × 38 | in Grundplatte und Kameraträger gleich |
| Deckel am Träger | ⌀ 2,7 mm | 34 in x | M2,5 Durchgang |
| Raspberry Pi | ⌀ 2,2 mm | 58 × 23 | in der Pi-Wanne, M2,5 schneidet sich selbst ein |
| Kabeldurchlass | 18 × 7 mm | mittig | USB-Kabel von der Wanne zur Kamera |

Die Pi-Platine misst **65 × 30 mm**, die Bohrungen liegen 3,5 mm von den Kanten
entfernt.

---

## Was du selbst nachmessen musst

Genau **drei** Maße hängen von deiner Kamera ab. Alles andere in der Zeichnung
ist davon unabhängig:

| Maß | Platzhalter | Wie messen |
|---|---|---|
| Kamerabreite | 27,0 mm | Messschieber, größte Ausdehnung |
| Kameratiefe | 18,0 mm | quer dazu |
| Kamerahöhe | 10,0 mm | inklusive Objektivfassung |

Dazu **die Lage des Objektivs**: Bei vielen Modellen sitzt es nicht in der Mitte
des Gehäuses. Miss den Abstand von zwei Kanten zur Objektivmitte und verschiebe
das Ø-14-Fenster im Deckel entsprechend.

Die Tasche wird mit **0,3 mm Spiel je Seite** ausgelegt, die Wände sind 2 mm dick.

---

## Parameter für Fusion 360

Diese als Benutzerparameter anlegen, dann lässt sich das Modell später in einem
Rutsch anpassen:

```
kamera_breite      = 27 mm      // nachmessen
kamera_tiefe       = 18 mm      // nachmessen
kamera_hoehe       = 10 mm      // nachmessen
spiel              = 0.3 mm
wand               = 2 mm
platte_dicke       = 3 mm
deckel_dicke       = 2 mm

daempfer_x         = 64 mm      // Rastermaß, Mitte zu Mitte
daempfer_y         = 38 mm
daempfer_bohrung   = 6.2 mm

rahmen_raster      = 30.5 mm
rahmen_bohrung     = 3.2 mm
pi_raster_x        = 58 mm
pi_raster_y        = 23 mm
pi_bohrung         = 2.2 mm
deckel_raster      = 34 mm
deckel_bohrung     = 2.7 mm
objektiv           = 14 mm

tasche_breite      = kamera_breite + 2 * spiel
tasche_tiefe       = kamera_tiefe + 2 * spiel
tasche_hoehe       = kamera_hoehe + 1 mm
```

**Vorgehen:** Jede Platte als eine Skizze auf der XY-Ebene zeichnen, Rechteck mit
4 mm Eckenradius, Bohrungen als Kreise mit dem Lochwerkzeug, dann extrudieren.
Die Taschenwände beim Kameraträger als zweite Extrusion nach unten. So bleibt
alles in einem Körper und lässt sich über die Parameter nachziehen.

---

## Toleranzen und Passprobe

**Bevor die großen Teile laufen: eine Passprobe drucken.** Ein Reststück
40 × 20 × 3 mm mit je einer Bohrung ⌀ 3,2, ⌀ 2,7, ⌀ 2,2 und ⌀ 6,2 — zehn Minuten
Druckzeit. Daran ausprobieren:

- geht die M3-Schraube durch die 3,2er Bohrung?
- schneidet sich die M2,5 sauber in die 2,2er ein, ohne zu sprengen?
- rastet die Dämpferkugel in der 6,2er ein und hält?

Fast jeder Drucker legt 0,1 bis 0,2 mm zu eng. Die Durchmesser im Modell
entsprechend nachziehen — dann passen alle vier Teile auf Anhieb.

---

## Druckeinstellungen

| Einstellung | Wert | Warum |
|---|---|---|
| Material | ABS oder ABS-CF | PETG, wenn der Drucker keine geschlossene Kammer hat — dann fällt die Temperaturfestigkeit weg, was für reine Suchflüge kein Problem ist |
| Schichthöhe | 0,2 mm | |
| Wandlinien | 4 | die Festigkeit steckt in den Wänden, nicht in der Füllung |
| Füllung | 30 %, Gyroid | |
| Lage | alle Teile flach auf dem Bett | alle Bohrungen senkrecht, keine Stützen nötig |
| Rand | 5 mm Brim bei ABS | gegen Verzug an den Ecken |

Gewicht aller vier Teile zusammen: rund **30 g**. Mit Kamera (9 g), Pi (11 g),
Kabel und Schrauben liegt die gesamte Nutzlast bei etwa **65 g**.

---

## Einbaulage der Kamera — das ist keine Kosmetik

Die Software rechnet aus einem Bildpunkt die GPS-Koordinate der Fundstelle.
Dabei gilt in `sensor/suchflug.py`:

> **Oben im Bild ist vorne in Flugrichtung.**

Die Kamera also so in die Tasche legen, dass ihre Bildoberkante zur Nase der
Drohne zeigt und der USB-C-Anschluss nach hinten. Steht sie verdreht eingebaut,
stimmen die gemeldeten Koordinaten nicht — und der Trupp sucht an der falschen
Stelle.

Nach dem Zusammenbau einmal prüfen: Drohne anheben, jemanden vor die Nase
stellen, im Wärmebild muss er **oben** erscheinen.

---

## Zusammenbau

1. Passprobe drucken und Durchmesser nachziehen
2. Alle vier Teile drucken
3. Dämpferkugeln in Grundplatte und Kameraträger einrasten
4. Kamera von unten in die Tasche legen, Deckel mit 2 × M2,5 anschrauben — nicht
   festknallen, das Kunststoffgewinde reißt sonst aus
5. Pi in die Wanne setzen, 4 × M2,5, SD-Karte zum Schlitz hin ausrichten
6. Wanne aufs Rahmendeck kleben oder schnallen, USB-Kabel durch den
   Kabelschlitz nach unten führen
7. Grundplatte an den Rahmen schrauben
8. **Schwerpunkt prüfen** — die Drohne muss an den Motorachsen aufgehängt
   waagerecht bleiben
9. Kabel gegen Vibration sichern, überall Schraubensicherung
