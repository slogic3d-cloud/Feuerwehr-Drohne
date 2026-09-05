#!/usr/bin/env python3
"""Erzeugt die Massskizzen des Kamerahalters als druckbare HTML-Seite.

Warum ein Skript statt einer von Hand gezeichneten Datei: So kommen Zeichnung
und Spezifikation zwangslaeufig aus derselben Zahlenquelle. Aendert sich ein
Mass, aendert sich die Zeichnung mit - und es gibt keine zwei Wahrheiten.

    python3 werkzeuge/zeichnung_gehaeuse.py > gehaeuse-zeichnung.html

Alle Masse in Millimetern. Gezeichnet wird masstabsgetreu im SVG-Koordinaten-
system, Ursprung jeweils in der Mitte des Bauteils.
"""

# --- Masse ---------------------------------------------------------------

GRUND_B, GRUND_H, GRUND_D = 84.0, 54.0, 3.0     # Grundplatte
TRAEGER_B, TRAEGER_H, TRAEGER_D = 76.0, 48.0, 3.0  # Kameratraeger
ECKE_R = 4.0

RAHMEN_RASTER = 30.5      # uebliches Lochbild fuer Flugregler-Stapel
RAHMEN_LOCH = 3.2         # M3 Durchgang
LANGLOCH_B, LANGLOCH_L = 3.2, 16.0
LANGLOCH_X = 36.0

PI_RASTER_X, PI_RASTER_Y = 58.0, 23.0   # Raspberry Pi Zero 2 W
PI_LOCH = 2.2                            # M2,5 selbstschneidend in Kunststoff
PI_PLATINE_B, PI_PLATINE_H = 65.0, 30.0
WANNE_B, WANNE_H, WANNE_D = 71.0, 36.0, 2.0   # Pi-Wanne fuers Rahmendeck
WANNE_RAND = 6.0                              # Randhoehe der Wanne

DECKEL_B, DECKEL_H, DECKEL_D = 40.0, 28.0, 2.0   # haelt die Kamera in der Tasche
DECKEL_SCHRAUBE = 2.7                             # M2,5 Durchgang
DECKEL_RASTER = 34.0                              # Schraubabstand in x

DAEMPFER_X, DAEMPFER_Y = 32.0, 19.0      # halbe Rasterabstaende
DAEMPFER_LOCH = 6.2                       # Taille der Daempferkugel

SCHLITZ_B, SCHLITZ_H = 18.0, 7.0          # Kabeldurchlass

# Platzhalter - vor dem Konstruieren nachmessen!
KAMERA_B, KAMERA_H, KAMERA_T = 27.0, 18.0, 10.0
SPIEL = 0.3                               # je Seite
WAND, BODEN = 2.0, 2.0
OBJEKTIV_D = 14.0
USB_B, USB_H = 13.0, 8.0

TASCHE_B = KAMERA_B + 2 * SPIEL
TASCHE_H = KAMERA_H + 2 * SPIEL
TASCHE_T = KAMERA_T + SPIEL


# --- SVG-Bausteine -------------------------------------------------------

def platte(breite, hoehe, radius):
    return ('<rect x="%.2f" y="%.2f" width="%.2f" height="%.2f" rx="%.2f" '
            'class="kante"/>' % (-breite / 2, -hoehe / 2, breite, hoehe, radius))


def loch(x, y, durchmesser, klasse="loch"):
    return ('<circle cx="%.2f" cy="%.2f" r="%.2f" class="%s"/>'
            '<path d="M%.2f %.2f H%.2f M%.2f %.2f V%.2f" class="mitte"/>'
            % (x, y, durchmesser / 2, klasse,
               x - durchmesser, y, x + durchmesser,
               x, y - durchmesser, y + durchmesser))


def langloch(x, y, breite, laenge):
    """Laengs liegendes Langloch, Laenge in y-Richtung."""
    r = breite / 2
    return ('<rect x="%.2f" y="%.2f" width="%.2f" height="%.2f" rx="%.2f" '
            'class="loch"/>' % (x - r, y - laenge / 2, breite, laenge, r))


def rechteck(x, y, breite, hoehe, radius=0.0, klasse="loch"):
    return ('<rect x="%.2f" y="%.2f" width="%.2f" height="%.2f" rx="%.2f" '
            'class="%s"/>' % (x - breite / 2, y - hoehe / 2, breite, hoehe,
                              radius, klasse))


def mass_waagerecht(x1, x2, y, text, ueber=6.0):
    """Waagerechte Massline mit Hilfslinien und Pfeilen."""
    yl = y - ueber
    return (
        '<path d="M%.2f %.2f V%.2f M%.2f %.2f V%.2f" class="hilfe"/>'
        '<path d="M%.2f %.2f H%.2f" class="mass" marker-start="url(#pfeil)" '
        'marker-end="url(#pfeil)"/>'
        '<text x="%.2f" y="%.2f" class="masstext">%s</text>'
        % (x1, y, yl - 1, x2, y, yl - 1,
           x1, yl, x2,
           (x1 + x2) / 2, yl - 1.6, text))


def mass_senkrecht(y1, y2, x, text, neben=6.0):
    xl = x + neben
    return (
        '<path d="M%.2f %.2f H%.2f M%.2f %.2f H%.2f" class="hilfe"/>'
        '<path d="M%.2f %.2f V%.2f" class="mass" marker-start="url(#pfeil)" '
        'marker-end="url(#pfeil)"/>'
        '<text x="%.2f" y="%.2f" class="masstext" transform="rotate(-90 %.2f %.2f)">%s</text>'
        % (x, y1, xl + 1, x, y2, xl + 1,
           xl, y1, y2,
           xl - 1.6, (y1 + y2) / 2, xl - 1.6, (y1 + y2) / 2, text))


def hinweis(x, y, zx, zy, text):
    """Hinweislinie mit Text am Ende."""
    anker = "start" if zx >= x else "end"
    return ('<path d="M%.2f %.2f L%.2f %.2f" class="hilfe"/>'
            '<text x="%.2f" y="%.2f" class="hinweistext" text-anchor="%s">%s</text>'
            % (x, y, zx, zy, zx + (1.5 if anker == "start" else -1.5), zy + 1.2,
               anker, text))


def zeichnung(inhalt, breite, hoehe, rand=26.0):
    return ('<svg viewBox="%.2f %.2f %.2f %.2f" class="riss">%s</svg>'
            % (-breite / 2 - rand, -hoehe / 2 - rand,
               breite + 2 * rand, hoehe + 2 * rand, inhalt))


# --- Die drei Risse ------------------------------------------------------

def grundplatte():
    t = [platte(GRUND_B, GRUND_H, ECKE_R)]

    for sx in (-1, 1):
        for sy in (-1, 1):
            t.append(loch(sx * RAHMEN_RASTER / 2, sy * RAHMEN_RASTER / 2, RAHMEN_LOCH))
            t.append(loch(sx * DAEMPFER_X, sy * DAEMPFER_Y, DAEMPFER_LOCH))
    for sx in (-1, 1):
        t.append(langloch(sx * LANGLOCH_X, 0, LANGLOCH_B, LANGLOCH_L))
    t.append(rechteck(0, 0, SCHLITZ_B, SCHLITZ_H, SCHLITZ_H / 2))

    # Masse: aussen und Daempfer oben, Rahmen und Pi unten, Hoehen rechts,
    # Pi-Hoehe links - so kreuzt keine Masslinie eine andere.
    t.append(mass_waagerecht(-GRUND_B / 2, GRUND_B / 2, -GRUND_H / 2, "84", 16))
    t.append(mass_waagerecht(-DAEMPFER_X, DAEMPFER_X, -GRUND_H / 2, "64", 9))
    t.append(mass_waagerecht(-RAHMEN_RASTER / 2, RAHMEN_RASTER / 2, GRUND_H / 2 + 3, "30,5", -3))
    t.append(mass_senkrecht(-GRUND_H / 2, GRUND_H / 2, GRUND_B / 2, "54", 16))
    t.append(mass_senkrecht(-DAEMPFER_Y, DAEMPFER_Y, GRUND_B / 2, "38", 8))

    t.append(hinweis(DAEMPFER_X, -DAEMPFER_Y, 45, -34, "4× ⌀ 6,2 Dämpfer"))
    t.append(hinweis(-RAHMEN_RASTER / 2, -RAHMEN_RASTER / 2, -45, -30, "4× ⌀ 3,2 Rahmen"))
    t.append(hinweis(LANGLOCH_X, LANGLOCH_L / 2, 45, 24, "2× Langloch 3,2 × 16"))
    t.append(hinweis(0, -SCHLITZ_H / 2, 0, -31, "Kabelschlitz 18 × 7"))
    return zeichnung("".join(t), GRUND_B, GRUND_H, 42)


def kameratraeger():
    t = [platte(TRAEGER_B, TRAEGER_H, ECKE_R)]
    for sx in (-1, 1):
        for sy in (-1, 1):
            t.append(loch(sx * DAEMPFER_X, sy * DAEMPFER_Y, DAEMPFER_LOCH))
    aussen_b = TASCHE_B + 2 * WAND
    aussen_h = TASCHE_H + 2 * WAND
    t.append(rechteck(0, 0, aussen_b, aussen_h, 1.5, "kante"))
    t.append(rechteck(0, 0, TASCHE_B, TASCHE_H, 1.0, "tasche"))
    t.append(rechteck(0, aussen_h / 2, USB_B, USB_H, 1.0, "loch"))
    for sx in (-1, 1):
        t.append(loch(sx * DECKEL_RASTER / 2, 0, DECKEL_SCHRAUBE))

    t.append(mass_waagerecht(-TRAEGER_B / 2, TRAEGER_B / 2, -TRAEGER_H / 2, "76", 16))
    t.append(mass_waagerecht(-DAEMPFER_X, DAEMPFER_X, -TRAEGER_H / 2, "64", 9))
    t.append(mass_waagerecht(-TASCHE_B / 2, TASCHE_B / 2, TRAEGER_H / 2 + 3,
                             "%.1f *" % TASCHE_B, -3))
    t.append(mass_senkrecht(-TRAEGER_H / 2, TRAEGER_H / 2, TRAEGER_B / 2, "48", 16))
    t.append(mass_senkrecht(-DAEMPFER_Y, DAEMPFER_Y, TRAEGER_B / 2, "38", 8))
    t.append(mass_senkrecht(-TASCHE_H / 2, TASCHE_H / 2, -TASCHE_B / 2,
                            "%.1f *" % TASCHE_H, -31))

    t.append(hinweis(DECKEL_RASTER / 2, 0, 45, 6, "2× ⌀ 2,7 für Deckel"))
    t.append(hinweis(USB_B / 2, aussen_h / 2 + USB_H / 2, 45, 20,
                     "USB-C 13 × 8 (nach hinten)"))
    t.append(hinweis(-aussen_b / 2, -aussen_h / 2, -45, -28, "Tasche, Wand 2 mm"))
    return zeichnung("".join(t), TRAEGER_B, TRAEGER_H, 42)


def deckel_und_wanne():
    """Deckel (haelt die Kamera) und Wanne (traegt den Pi) nebeneinander."""
    t = []
    versatz = -34.0
    # Deckel links
    t.append('<g transform="translate(%.2f 0)">' % versatz)
    t.append(platte(DECKEL_B, DECKEL_H, 2.5))
    t.append(loch(0, 0, OBJEKTIV_D))
    for sx in (-1, 1):
        t.append(loch(sx * DECKEL_RASTER / 2, 0, DECKEL_SCHRAUBE))
    t.append(mass_waagerecht(-DECKEL_B / 2, DECKEL_B / 2, -DECKEL_H / 2, "40", 9))
    t.append(mass_waagerecht(-DECKEL_RASTER / 2, DECKEL_RASTER / 2,
                             DECKEL_H / 2 + 3, "34", -3))
    t.append(mass_senkrecht(-DECKEL_H / 2, DECKEL_H / 2, DECKEL_B / 2, "28", 8))
    t.append(hinweis(-OBJEKTIV_D / 2, 0, -26, -20, "⌀ 14 Objektiv"))
    t.append('<text x="0" y="%.2f" class="masstext">Teil 3 · Deckel, 2 mm</text>'
             % (DECKEL_H / 2 + 22))
    t.append('</g>')

    # Wanne rechts
    t.append('<g transform="translate(%.2f 0)">' % (-versatz + 24))
    t.append(platte(WANNE_B, WANNE_H, 3.0))
    t.append(rechteck(0, 0, WANNE_B - 2 * WAND, WANNE_H - 2 * WAND, 2.0, "kante"))
    t.append(rechteck(0, 0, PI_PLATINE_B, PI_PLATINE_H, 2.0, "strichpunkt"))
    for sx in (-1, 1):
        for sy in (-1, 1):
            t.append(loch(sx * PI_RASTER_X / 2, sy * PI_RASTER_Y / 2, PI_LOCH))
    t.append(rechteck(-WANNE_B / 2, 0, 2 * WAND, 14, 1.0, "loch"))
    t.append(mass_waagerecht(-WANNE_B / 2, WANNE_B / 2, -WANNE_H / 2, "71", 15))
    t.append(mass_waagerecht(-PI_RASTER_X / 2, PI_RASTER_X / 2, -WANNE_H / 2, "58", 8))
    t.append(mass_senkrecht(-WANNE_H / 2, WANNE_H / 2, WANNE_B / 2, "36", 8))
    t.append(mass_senkrecht(-PI_RASTER_Y / 2, PI_RASTER_Y / 2, -PI_RASTER_X / 2, "23", -22))
    t.append(hinweis(-WANNE_B / 2 + WAND, 7, -46, 24, "Schlitz für SD-Karte"))
    t.append(hinweis(PI_RASTER_X / 2, PI_RASTER_Y / 2, 40, 26, "4× ⌀ 2,2 (M2,5)"))
    t.append('<text x="0" y="%.2f" class="masstext">Teil 4 · Pi-Wanne, Rand 6 mm</text>'
             % (WANNE_H / 2 + 30))
    t.append('</g>')
    return zeichnung("".join(t), 180, WANNE_H, 30)


def schnitt():
    """Seitenschnitt des zusammengebauten Halters. Ursprung = Rahmenunterseite."""
    b = 96.0
    t = []
    y_rahmen = -6.0
    y_grund = y_rahmen                      # Grundplatte direkt unter den Rahmen
    y_traeger = y_grund + GRUND_D + 8.0     # 8 mm Daempferhoehe
    y_deckel = y_traeger + TRAEGER_D + TASCHE_T + 1.0

    t.append('<path d="M%.2f %.2f H%.2f" class="strichpunkt"/>'
             % (-b / 2 - 4, y_rahmen, b / 2 + 4))
    t.append(hinweis(-b / 2 - 2, y_rahmen, -52, y_rahmen - 9, "Rahmenunterseite"))

    t.append(rechteck(0, y_grund + GRUND_D / 2, GRUND_B, GRUND_D, 0, "voll"))
    t.append(hinweis(-GRUND_B / 2, y_grund + GRUND_D / 2, -52, y_grund + 5,
                     "Teil 1 · Grundplatte"))

    for sx in (-1, 1):
        t.append('<circle cx="%.2f" cy="%.2f" r="4.0" class="gummi"/>'
                 % (sx * DAEMPFER_X, y_grund + GRUND_D + 4.0))
    t.append(hinweis(DAEMPFER_X, y_grund + GRUND_D + 4.0, 54, y_grund + 2,
                     "Dämpferkugel, 8 mm"))

    t.append(rechteck(0, y_traeger + TRAEGER_D / 2, TRAEGER_B, TRAEGER_D, 0, "voll"))
    t.append(hinweis(-TRAEGER_B / 2, y_traeger + TRAEGER_D / 2, -52, y_traeger + 4,
                     "Teil 2 · Kameraträger"))

    # Taschenwaende zeigen nach unten
    tiefe = TASCHE_T + 1.0
    for sx in (-1, 1):
        t.append(rechteck(sx * (TASCHE_B / 2 + WAND / 2), y_traeger + TRAEGER_D + tiefe / 2,
                          WAND, tiefe, 0, "voll"))
    t.append(rechteck(0, y_traeger + TRAEGER_D + TASCHE_T / 2, TASCHE_B, TASCHE_T,
                      0, "kante"))
    t.append(hinweis(TASCHE_B / 2, y_traeger + TRAEGER_D + TASCHE_T / 2, 54,
                     y_traeger + 13, "Kamera, von unten eingelegt"))

    t.append(rechteck(0, y_deckel + DECKEL_D / 2, DECKEL_B, DECKEL_D, 0, "voll"))
    t.append(hinweis(-DECKEL_B / 2, y_deckel + DECKEL_D / 2, -52, y_deckel + 7,
                     "Teil 3 · Deckel"))

    t.append('<path d="M0 %.2f V%.2f" class="mass" marker-end="url(#pfeil)"/>'
             % (y_deckel + DECKEL_D, y_deckel + DECKEL_D + 12))
    t.append('<text x="3" y="%.2f" class="hinweistext">Blickrichtung nach unten</text>'
             % (y_deckel + DECKEL_D + 10))

    t.append(mass_senkrecht(y_rahmen, y_deckel + DECKEL_D, GRUND_B / 2,
                            "%.0f Bauhöhe" % (y_deckel + DECKEL_D - y_rahmen), 4))
    return zeichnung("".join(t), b, 62, 46)


# --- Seite ---------------------------------------------------------------

SEITE = """<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Kamerahalter — Maßzeichnungen</title>
<style>
  @page { size: A4; margin: 12mm; }
  * { box-sizing: border-box; }
  body {
    font: 11pt/1.45 -apple-system, "Segoe UI", Roboto, Arial, sans-serif;
    color: #000; background: #fff; margin: 0 auto; padding: 16px; max-width: 200mm;
  }
  h1 { font-size: 15pt; margin: 0 0 2px; }
  h2 {
    font-size: 11.5pt; margin: 20px 0 4px; padding-bottom: 3px;
    border-bottom: 1.5px solid #000; text-transform: uppercase; letter-spacing: .04em;
  }
  .unter { font-size: 9pt; color: #444; }
  .riss { width: 100%%; height: auto; display: block; margin: 6px 0 2px; }

  .kante  { fill: none; stroke: #000; stroke-width: .45; }
  .voll   { fill: #d8d8d8; stroke: #000; stroke-width: .45; }
  .loch   { fill: #fff; stroke: #000; stroke-width: .4; }
  .auge   { fill: #eee; }
  .tasche { fill: #f2f2f2; stroke: #000; stroke-width: .4; stroke-dasharray: 1.6 1; }
  .gummi  { fill: #999; stroke: #000; stroke-width: .35; }
  .mitte  { stroke: #000; stroke-width: .18; stroke-dasharray: 1.4 .8 .3 .8; }
  .strichpunkt { fill: none; stroke: #777; stroke-width: .3; stroke-dasharray: 3 1 .6 1; }
  .hilfe  { stroke: #555; stroke-width: .2; fill: none; }
  .mass   { stroke: #000; stroke-width: .3; fill: none; }
  .masstext { font-size: 3.4px; text-anchor: middle; font-family: Arial, sans-serif; }
  .hinweistext { font-size: 3px; font-family: Arial, sans-serif; fill: #222; }

  table { width: 100%%; border-collapse: collapse; font-size: 9.5pt; margin-top: 6px; }
  th, td { border: 1px solid #000; padding: 4px 6px; text-align: left; }
  th { background: #e8e8e8; font-size: 8.5pt; text-transform: uppercase; }
  .warn { border: 1.5px solid #000; background: #f4f4f4; padding: 9px 11px;
          font-size: 9.5pt; line-height: 1.5; margin: 10px 0; }
  .warn b { display: block; margin-bottom: 3px; }
  .seitenumbruch { page-break-before: always; }
  .drucken { text-align: right; margin-bottom: 6px; }
  .drucken button { font: inherit; padding: 7px 14px; border: 1.5px solid #000;
                    background: #fff; border-radius: 6px; cursor: pointer; font-weight: 600; }
  @media print { .drucken { display: none; } body { padding: 0; } }
</style>
</head>
<body>
<div class="drucken"><button onclick="window.print()">Drucken</button></div>

<svg width="0" height="0" style="position:absolute">
  <defs>
    <marker id="pfeil" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="4"
            markerHeight="4" orient="auto-start-reverse">
      <path d="M0 1 L10 5 L0 9 z" fill="#000"/>
    </marker>
  </defs>
</svg>

<h1>Kamerahalter für die Suchdrohne</h1>
<div class="unter">Alle Maße in Millimetern · Zeichnung erzeugt aus
werkzeuge/zeichnung_gehaeuse.py · Auslegung für Akku 6S1P</div>

<div class="warn">
  <b>Die mit * bezeichneten Maße sind Platzhalter.</b>
  Die Kameratasche ist mit 27 × 18 × 10 mm angesetzt. <b style="display:inline">Vor dem
  Konstruieren die eigene Kamera mit dem Messschieber nachmessen</b> — Gehäuse und
  vor allem die Lage des Objektivs weichen je nach Modell ab. Alles andere in
  dieser Zeichnung ist unabhängig davon.
</div>

<h2>Teil 1 · Grundplatte — Draufsicht</h2>
<div class="unter">Wird direkt unter die Rahmenunterseite geschraubt. Daran hängen
über vier Dämpferkugeln der Kameraträger und der Deckel.</div>
%(grundplatte)s

<h2>Teil 2 · Kameraträger — Draufsicht</h2>
<div class="unter">Hängt gedämpft unter der Grundplatte. Die Taschenwände zeigen
<b>nach unten</b>, die Kamera wird von unten eingelegt und vom Deckel gehalten.</div>
%(traeger)s

<h2>Teil 3 · Deckel und Teil 4 · Pi-Wanne</h2>
<div class="unter">Der Deckel hält die Kamera in der Tasche. Die Wanne nimmt den
Raspberry Pi auf und wird oben auf das Rahmendeck geklebt oder geschnallt.</div>
%(deckel)s

<div class="seitenumbruch"></div>

<h2>Zusammenbau — Seitenschnitt</h2>
%(schnitt)s

<h2>Lochbilder auf einen Blick</h2>
<table>
  <tr><th>Wofür</th><th>Bohrung</th><th>Rastermaß</th><th>Bemerkung</th></tr>
  <tr><td>Rahmenbefestigung</td><td>⌀ 3,2 mm</td><td>30,5 × 30,5</td><td>Standardmaß für Flugregler-Stapel</td></tr>
  <tr><td>Rahmen, abweichend</td><td>Langloch 3,2 × 16</td><td>± 36 in x</td><td>gleicht andere Rahmen aus</td></tr>
  <tr><td>Raspberry Pi Zero 2 W</td><td>⌀ 2,2 mm</td><td>58 × 23</td><td>in der Pi-Wanne; M2,5 schneidet sich selbst ein</td></tr>
  <tr><td>Deckel am Kameraträger</td><td>⌀ 2,7 mm</td><td>34 in x</td><td>M2,5 Durchgang</td></tr>
  <tr><td>Dämpferkugeln</td><td>⌀ 6,2 mm</td><td>64 × 38</td><td>in beiden Platten gleich</td></tr>
  <tr><td>Kabeldurchlass</td><td>18 × 7 mm</td><td>mittig</td><td>USB-Kabel von der Wanne zur Kamera</td></tr>
</table>

<h2>Druckeinstellungen</h2>
<table>
  <tr><th>Einstellung</th><th>Wert</th><th>Warum</th></tr>
  <tr><td>Material</td><td>ABS oder ABS-CF</td><td>PETG, wenn der Drucker keine geschlossene Kammer hat</td></tr>
  <tr><td>Schichthöhe</td><td>0,2 mm</td><td></td></tr>
  <tr><td>Wandlinien</td><td>4</td><td>die Festigkeit steckt in den Wänden, nicht in der Füllung</td></tr>
  <tr><td>Füllung</td><td>30 %%, Gyroid</td><td></td></tr>
  <tr><td>Lage</td><td>beide Platten flach auf dem Bett</td><td>alle Bohrungen senkrecht, keine Stützen nötig</td></tr>
  <tr><td>Rand</td><td>5 mm Brim bei ABS</td><td>gegen Verzug an den Ecken</td></tr>
</table>

<div class="warn">
  <b>Zuerst eine Passprobe drucken.</b>
  Ein Reststück mit je einer ⌀ 3,2-, ⌀ 2,2- und ⌀ 6,2-Bohrung, zehn Minuten
  Druckzeit. Schraube, Gewinde und Dämpferkugel daran ausprobieren und die
  Durchmesser im Modell nachziehen, bevor die großen Teile laufen. Jeder Drucker
  liegt anders — meist 0,1 bis 0,2 mm zu eng.
</div>

<div class="warn">
  <b>Einbaulage der Kamera — das ist keine Kosmetik.</b>
  Die Software rechnet aus einem Bildpunkt die GPS-Koordinate der Fundstelle.
  Dabei gilt: <b style="display:inline">oben im Bild ist vorne in Flugrichtung.</b>
  Die Kamera also so einsetzen, dass ihre Bildoberkante zur Nase der Drohne zeigt.
  Steht sie verdreht, stimmen die gemeldeten Koordinaten nicht — und der Trupp
  sucht an der falschen Stelle.
</div>
</body>
</html>
"""


def main():
    return SEITE % {
        "grundplatte": grundplatte(),
        "traeger": kameratraeger(),
        "deckel": deckel_und_wanne(),
        "schnitt": schnitt(),
    }


if __name__ == "__main__":
    print(main())
