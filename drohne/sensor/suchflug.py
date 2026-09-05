"""Geometrie der Luftsuche.

Hier steckt die Rechnerei, die aus einer Waermebildkamera ein brauchbares
Suchgeraet macht:

* Wie breit ist der Streifen, den die Kamera aus einer bestimmten Hoehe sieht?
* Wie hoch darf ich fliegen, damit eine liegende Person noch genug Pixel hat?
* Wo genau am Boden liegt ein Fleck, den ich im Bild gefunden habe?
* Wie muss ich ein Suchgebiet abfliegen, damit nichts durchrutscht?

Alle Winkel in Grad, alle Laengen in Metern, Koordinaten in Dezimalgrad.
"""

import math

# Eine liegende erwachsene Person, laengste Ausdehnung.
PERSON_LAENGE_M = 1.75

# Mittlerer Erdumfang: ein Grad Breite entspricht rund 111,32 km.
METER_JE_GRAD = 111320.0


def streifenbreite(hoehe_m, bildwinkel_grad):
    """Wie breit ist der am Boden erfasste Streifen? (Kamera senkrecht nach unten)"""
    return 2.0 * hoehe_m * math.tan(math.radians(bildwinkel_grad) / 2.0)


def bodenaufloesung(hoehe_m, bildwinkel_grad, pixel):
    """Meter je Pixel am Boden."""
    return streifenbreite(hoehe_m, bildwinkel_grad) / float(pixel)


def pixel_je_person(hoehe_m, bildwinkel_grad, pixel, laenge_m=PERSON_LAENGE_M):
    """Wie viele Pixel lang ist eine liegende Person aus dieser Hoehe?"""
    aufloesung = bodenaufloesung(hoehe_m, bildwinkel_grad, pixel)
    return laenge_m / aufloesung if aufloesung > 0 else 0.0


def empfohlene_hoehe(mindestpixel, bildwinkel_grad, pixel, laenge_m=PERSON_LAENGE_M):
    """Groesste Hoehe, bei der eine Person noch ``mindestpixel`` lang erscheint.

    Hoeher fliegen heisst schneller suchen, aber irgendwann besteht die Person
    nur noch aus zwei Pixeln und geht im Rauschen unter. Diese Zahl ist die
    Grenze, an der man sich beim Suchflug orientiert.
    """
    if mindestpixel <= 0:
        return 0.0
    meter_je_pixel = laenge_m / mindestpixel
    breite = meter_je_pixel * pixel
    return breite / (2.0 * math.tan(math.radians(bildwinkel_grad) / 2.0))


def versatz_zu_koordinate(position, nord_m, ost_m):
    """Verschiebt eine Koordinate um eine Strecke in Metern."""
    breite = position[0] + nord_m / METER_JE_GRAD
    nenner = METER_JE_GRAD * math.cos(math.radians(position[0]))
    laenge = position[1] + (ost_m / nenner if abs(nenner) > 1e-6 else 0.0)
    return (breite, laenge)


def pixel_zu_koordinate(px, py, bild_breite, bild_hoehe, hoehe_m, kurs_grad,
                        position, bildwinkel_quer, bildwinkel_hoch):
    """Rechnet einen Bildpunkt in eine Bodenkoordinate um.

    Vorausgesetzt wird eine senkrecht nach unten blickende Kamera und eine
    waagerecht fliegende Drohne. Bei starker Schraeglage stimmt das Ergebnis
    nicht mehr genau - fuer die Vermisstensuche reicht es, weil der Trupp
    ohnehin die letzten Meter zu Fuss sucht.

    ``kurs_grad``: Flugrichtung, 0 = Norden, im Uhrzeigersinn.
    ``position``: (Breite, Laenge) der Drohne in Dezimalgrad.
    """
    quer_m = streifenbreite(hoehe_m, bildwinkel_quer)
    hoch_m = streifenbreite(hoehe_m, bildwinkel_hoch)

    # Bildmitte ist der Punkt direkt unter der Drohne.
    rechts_m = (px + 0.5 - bild_breite / 2.0) / bild_breite * quer_m
    vorne_m = (bild_hoehe / 2.0 - py - 0.5) / bild_hoehe * hoch_m

    kurs = math.radians(kurs_grad)
    nord_m = vorne_m * math.cos(kurs) - rechts_m * math.sin(kurs)
    ost_m = vorne_m * math.sin(kurs) + rechts_m * math.cos(kurs)
    return versatz_zu_koordinate(position, nord_m, ost_m)


def abstand_m(a, b):
    """Abstand zweier Koordinaten in Metern (fuer kurze Strecken genau genug)."""
    mittlere_breite = math.radians((a[0] + b[0]) / 2.0)
    nord = (b[0] - a[0]) * METER_JE_GRAD
    ost = (b[1] - a[1]) * METER_JE_GRAD * math.cos(mittlere_breite)
    return math.hypot(nord, ost)


def streifenabstand(hoehe_m, bildwinkel_quer, ueberlappung):
    """Abstand benachbarter Flugbahnen mit Sicherheitsueberlappung."""
    return streifenbreite(hoehe_m, bildwinkel_quer) * (1.0 - ueberlappung)


def maeander(ecke_a, ecke_b, abstand_m_streifen, richtung="nord"):
    """Erzeugt Wegpunkte, die ein Rechteck in Bahnen abfliegen.

    ``ecke_a`` und ``ecke_b`` sind zwei gegenueberliegende Ecken als
    (Breite, Laenge). Die Bahnen verlaufen entweder in Nord-Sued-Richtung
    ("nord") oder in Ost-West-Richtung ("ost"). Jede zweite Bahn wird
    rueckwaerts geflogen, damit keine Leerfahrten entstehen.
    """
    breite_min, breite_max = sorted((ecke_a[0], ecke_b[0]))
    laenge_min, laenge_max = sorted((ecke_a[1], ecke_b[1]))
    mittlere_breite = (breite_min + breite_max) / 2.0

    grad_je_meter_breite = 1.0 / METER_JE_GRAD
    nenner = METER_JE_GRAD * math.cos(math.radians(mittlere_breite))
    grad_je_meter_laenge = 1.0 / nenner if abs(nenner) > 1e-6 else 0.0

    wegpunkte = []
    if richtung == "nord":
        schritt = abstand_m_streifen * grad_je_meter_laenge
        if schritt <= 0:
            return []
        laenge = laenge_min
        vorwaerts = True
        while laenge <= laenge_max + schritt * 0.001:
            if vorwaerts:
                wegpunkte.append((breite_min, laenge))
                wegpunkte.append((breite_max, laenge))
            else:
                wegpunkte.append((breite_max, laenge))
                wegpunkte.append((breite_min, laenge))
            vorwaerts = not vorwaerts
            laenge += schritt
    else:
        schritt = abstand_m_streifen * grad_je_meter_breite
        if schritt <= 0:
            return []
        breite = breite_min
        vorwaerts = True
        while breite <= breite_max + schritt * 0.001:
            if vorwaerts:
                wegpunkte.append((breite, laenge_min))
                wegpunkte.append((breite, laenge_max))
            else:
                wegpunkte.append((breite, laenge_max))
                wegpunkte.append((breite, laenge_min))
            vorwaerts = not vorwaerts
            breite += schritt
    return wegpunkte


def strecke_m(wegpunkte):
    return sum(abstand_m(wegpunkte[i], wegpunkte[i + 1])
               for i in range(len(wegpunkte) - 1))


def flaechenleistung_ha_min(geschwindigkeit_ms, abstand_m_streifen):
    """Wie viel Flaeche wird je Minute abgesucht?"""
    return geschwindigkeit_ms * abstand_m_streifen * 60.0 / 10000.0


def suchplan(hoehe_m, bildwinkel_quer, kamera_breite, gitter_breite,
             ueberlappung, geschwindigkeit_ms, mindestpixel):
    """Fasst die Eckwerte eines Suchflugs zusammen - fuers Tablet.

    Unterschieden wird bewusst zwischen der Aufloesung der **Kamera** und der
    des **Analysegitters**: die Erkennung arbeitet auf dem verkleinerten
    Gitter, und nur dessen Aufloesung entscheidet darueber, ob eine Person
    gefunden wird. Fuer das Auge am Tablet zaehlt dagegen die volle
    Kameraaufloesung - deshalb stehen beide Zahlen da.
    """
    abstand = streifenabstand(hoehe_m, bildwinkel_quer, ueberlappung)
    return {
        "hoehe_m": round(hoehe_m, 1),
        "streifenbreite_m": round(streifenbreite(hoehe_m, bildwinkel_quer), 1),
        "streifenabstand_m": round(abstand, 1),
        "kamera_cm_je_pixel": round(
            bodenaufloesung(hoehe_m, bildwinkel_quer, kamera_breite) * 100, 1),
        "gitter_cm_je_zelle": round(
            bodenaufloesung(hoehe_m, bildwinkel_quer, gitter_breite) * 100, 1),
        "person_zellen_lang": round(
            pixel_je_person(hoehe_m, bildwinkel_quer, gitter_breite), 1),
        "hoechste_sinnvolle_hoehe_m": round(
            empfohlene_hoehe(mindestpixel, bildwinkel_quer, gitter_breite), 1),
        "flaechenleistung_ha_min": round(
            flaechenleistung_ha_min(geschwindigkeit_ms, abstand), 2),
        "geschwindigkeit_ms": round(geschwindigkeit_ms, 1),
    }
