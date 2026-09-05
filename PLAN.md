# Arbeitsplan

Was in welcher Reihenfolge zu tun ist, damit aus dem Code ein Gerät wird, das
im Einsatz wirklich hilft. Das **Warum** und die technischen Begründungen
stehen in [KONZEPT.md](KONZEPT.md) — hier steht das **Was, wann und womit**.

**Stand:** Software fertig und getestet (84 Tests, läuft im Simulationsmodus).
Hardware: nichts gekauft — und das bleibt bis Phase B auch so.

---

## Die Reihenfolge

> **Erst alles, was ohne Hardware geht. Dann eine einzige Bestellung.**

Das hat einen handfesten Vorteil: Wenn die Teile ankommen, kannst du schon
fliegen (im Simulator geübt), hast den Kompetenznachweis in der Tasche, die
Halter fertig konstruiert und weißt, wo du üben darfst. Statt monatelang
zwischen Warten und Basteln zu pendeln, baust du in ein, zwei Wochenenden
durch.

**Der Preis dafür, ehrlich gesagt:** Du legst rund 700 € auf einmal hin,
bevor bewiesen ist, dass die Wärmebilderkennung mit *deiner* Kamera auf
*deinen* Wiesen funktioniert. Das ist ein bewusst eingegangenes Risiko. Es
lässt sich kleinhalten: Kamera und Pi zuerst auspacken und die Bodenmessreihe
(Schritt C1) machen, **bevor** ein einziges Kabel an der Flugzelle gelötet
wird. Geht dort etwas schief, kannst du den Rest der Teile noch zurückgeben.

---

# Phase A — Alles ohne Hardware

**Zeit:** so lange du brauchst · **Kosten:** 0 €

## A0 — Die wichtigste Frage vorab beantworten — mit der Kamera der Wehr

**Kosten: 0 €. Das ist der Versuch, der über das ganze Projekt entscheidet.**

Die Wehr hat eine Wärmebildkamera. Damit lässt sich schon heute klären, ob sich
nachts ein liegender Mensch auf *unseren* Flächen überhaupt deutlich genug vom
Boden abhebt. Wenn nicht, hilft auch die beste Software nichts — und niemand
hat Geld ausgegeben.

- [ ] [messprotokoll.html](messprotokoll.html) im Browser öffnen und Blatt 1
      ausdrucken (die Datei braucht kein Python, nur einen Browser)
- [ ] Nach Einbruch der Dunkelheit raus, mindestens zwei Stunden nach
      Sonnenuntergang, am besten bei klarem Himmel
- [ ] Erhöhten Standpunkt suchen: Drehleiter, Hochsitz, Böschung, Feldscheune
- [ ] Helfer legt sich flach hin und bleibt ruhig liegen
- [ ] Messen und eintragen: Temperatur der Person, Temperatur des Bodens
      daneben, **Differenz** — und das über wachsende Abstände
- [ ] Auch Störer notieren: Was sah aus wie ein Mensch, war aber keiner?

**Die Zahl, auf die es ankommt, ist die Differenz.** Unter 2 K wird es für die
Automatik schwierig, ab 4 K ist es gut, ab 6 K sehr gut.

**Fertig, wenn:** Du weißt, mit wie viel Kelvin Unterschied du auf euren Wiesen
rechnen kannst — und ob es überhaupt genug ist.

Wenn möglich, den Versuch zweimal machen: einmal bei klarem Himmel und einmal
bei Bewölkung. Der Unterschied ist groß und sagt dir, wann ein Einsatz Sinn
hat und wann nicht.

## A1 — Software zum Laufen bringen

- [ ] Python 3 installieren, falls noch nicht vorhanden
      ([python.org](https://www.python.org/downloads/) — unter Windows beim
      Installieren **„Add python.exe to PATH" ankreuzen**)
- [ ] Simulation starten:
      ```bash
      cd sensor
      python3 suchkopf.py      # Windows: py suchkopf.py
      ```
      Dann `http://localhost:8080/` im Browser öffnen
- [ ] Tests laufen lassen:
      ```bash
      cd tests
      python3 -m unittest discover -s .
      ```
- [ ] Mit der Oberfläche spielen: Farbskala umschalten, Fundstelle als
      „Person" und als „Fehlalarm" markieren, Koordinate kopieren
- [ ] In `sensor/konfig.py` an den Schwellen drehen und zusehen, was passiert —
      das ist die beste Art, das Verfahren zu verstehen

**Fertig, wenn:** Du das Wärmebild im Browser gesehen hast und weißt, wo du
etwas verstellst.

## A2 — Fliegen lernen, bevor teure Teile da sind

Das ist der Punkt, an dem sonst Geld kaputtgeht. Ein Simulator kostet 20–30 €
oder nichts und spart erfahrungsgemäß mindestens einen Satz Propeller, oft
mehr.

- [ ] Simulator einrichten (ArduPilot SITL ist kostenlos; für Flugpraxis sind
      Liftoff oder Velocidrone realistischer) und den Gamepad anlernen
- [ ] Schweben üben, bis es langweilig wird
- [ ] Koordinierte Kurven, Bahnen abfliegen, Landen
- [ ] Notfälle üben: Orientierung verloren, Drohne kommt auf dich zu

**Fertig, wenn:** Du eine Bahn geradeaus abfliegen und sauber landen kannst,
ohne zu überlegen.

## A3 — Papiere, die Zeit brauchen

- [ ] **Kompetenznachweis A1/A3** beim Luftfahrt-Bundesamt — Online-Test,
      kostenlos, ein Nachmittag
- [ ] Betreiberregistrierung beim LBA (e-ID) — die Nummer kommt später aufs Gerät
- [ ] Versicherungsfrage klären: private Drohnenversicherung deckt
      Einsatzflüge in der Regel **nicht**

## A4 — Konstruktion

- [ ] Maße der Kamera und des Pi aus den Datenblättern holen
- [ ] Halter konstruieren: Kamera senkrecht nach unten, Pi daneben,
      Kabelführung, Vibrationsdämpfung
- [ ] Probedrucke in ABS oder ABS-CF — auch um herauszufinden, ob dein Drucker
      ABS überhaupt sauber hinbekommt (ohne geschlossene Kammer zieht es sich
      krumm; dann PETG nehmen und auf die 80 °C verzichten)

## A5 — Rahmenbedingungen klären

- [ ] **Übungsgelände:** Für A3 brauchst du 150 m Abstand zu Wohn- und
      Gewerbegebieten. Feld hinter dem Ort? Modellflugplatz? Einen Landwirt
      fragen?
- [ ] Bei der Kreisbrandinspektion vorfühlen: Ist so ein Projekt erwünscht?
      Wer müsste zustimmen?
- [ ] Einen zweiten Mann suchen — ein Gerät, das nur einer bedienen kann, ist
      im Einsatz nicht verfügbar

## A6 — Bestellung vorbereiten

- [ ] **[TEILELISTE.md](TEILELISTE.md)** durchgehen — vollständige Liste mit
      Stückzahlen und Kaufhinweisen
- [ ] Preise und Verfügbarkeit prüfen, möglichst wenige Händler
- [ ] Prüfen, was du schon hast: RC-Sender? Ladegerät? Lötstation?
      Schrumpfschlauch, XT60-Stecker, Silikonlitze?
- [ ] Verbrauchsmaterial nicht vergessen: Ersatzpropeller, Ersatzarme,
      Kabelbinder, Klettband, Schraubensicherung

---

# Phase B — Die eine Bestellung

**Kosten:** rund 600 € (mit Sender und Ladegerät 715 €)

| Bereich | Inhalt | Betrag |
|---|---|---:|
| Nutzlast | InfiRay P2 Pro / Topdon TC001, Pi Zero 2 W + SD + OTG-Adapter | 260 € |
| Zelle | Rahmen 7", 4× Motor 2807, 4-in-1-Regler, F405-Stack, Propeller, GPS M10, ELRS-Empfänger | 235 € |
| Energie | Li-Ion 6S2P | 90 € |
| Kleinteile | BEC 5 V/3 A, Stecker, Litze, Klettband | 15 € |
| falls nötig | RC-Sender 70 €, Ladegerät 45 € | 115 € |

---

# Phase C — Aufbau

## C1 — Zuerst die Kamera, noch bevor gelötet wird

**Das ist der Test, der über alles entscheidet — und der einzige, nach dem du
den Rest noch zurückschicken kannst.**

- [ ] Raspberry Pi OS Lite (64 Bit) aufspielen, WLAN und SSH schon beim
      Schreiben der Karte eintragen
- [ ] Repo auf den Pi holen, `sudo apt install python3-opencv`
      (nur der Kameratreiber braucht das)
- [ ] Kamera über OTG anstecken, prüfen: `v4l2-ctl --list-devices`
- [ ] Erster echter Lauf:
      ```bash
      WAERMEBILD_TYP=infiray python3 suchkopf.py
      ```
- [ ] **Messreihe:** Jemand legt sich hin, Kamera aus 3, 5, 10 und 15 m
      draufhalten. Notieren: Abhebung in Kelvin, Zellen je Fleck
- [ ] Dasselbe **nachts** — der Unterschied wird dich überraschen
- [ ] Schwellen in `sensor/konfig.py` nachziehen, vor allem `ABHEBUNG_K`

**Fertig, wenn:** Eine nachts auf der Wiese liegende Person zuverlässig als
Treffer gemeldet wird und ein Heizkörper nicht.

## C2 — Flugzelle

- [ ] Aufbauen und löten
- [ ] ArduPilot flashen, Rahmentyp, Motorreihenfolge, Drehrichtungen
- [ ] Kalibrieren: Beschleunigungsmesser, Kompass, Regler, Funk, Akku
- [ ] **Failsafes setzen** — Rückkehr zum Startpunkt bei Funkverlust,
      Akkuwarnung, Höhenbegrenzung. Keine Fleißaufgabe.
- [ ] Erstflug **ohne Nutzlast** auf freier Fläche
- [ ] Zehn Akkus leerfliegen, Rückkehrfunktion und Notabschaltung ausprobieren.
      Erst danach kommt die 230-€-Kamera ans Gerät.

## C3 — Zusammenbau

- [ ] Halter montieren, Pi über BEC versorgen, Kabel gegen Vibration sichern
- [ ] Schwerpunkt prüfen
- [ ] **Flugzeit mit Nutzlast messen** — die echte Zahl, nicht die gerechnete
- [ ] Im Schwebeflug das Wärmebild ansehen: scharf? Was sagt die
      Böigkeitsanzeige? Zu viel Vibration heißt: Dämpfung unter den Halter

---

# Phase D — Trefferquote messen

**Zeit:** laufend · **Kosten:** 0 € · **Die Phase, die zählt**

Ohne diese Zahlen ist es ein Bastelprojekt. Mit ihnen ist es etwas, über das
man mit der Wehrführung reden kann.

- [ ] Nachts auf eine abgemähte Wiese. Ein Helfer legt sich an eine Stelle,
      **die du nicht kennst** — jemand Drittes weist ihn ein
- [ ] In 20, 30, 40, 50 und 60 m Höhe überfliegen. Notieren: gefunden ja/nein,
      nach wie vielen Sekunden, welches Vertrauen
- [ ] Jede Fundstelle am Tablet bewerten, danach `python3 lernen.py`
- [ ] Wiederholen: Stoppelfeld, hohes Gras, Waldrand, leichter Regen, tagsüber
- [ ] Tabelle führen: **Höhe → Trefferquote → Fehlalarme je Flug**

**Fertig, wenn:** Du den Satz sagen kannst: „Bei 40 m über abgemähter Wiese
finde ich nachts 9 von 10 Personen, mit im Schnitt 2 Fehlalarmen je Flug."

---

# Phase E — Aus dem Bastelprojekt wird ein Einsatzmittel

- [ ] Dem Kommandanten vorführen — mit den Zahlen aus Phase D, nicht mit
      Versprechen
- [ ] Über die Kreisbrandinspektion an das Luftamt Nordbayern: Was braucht es
      für Einsatzflüge über A3 hinaus?
- [ ] Versicherung über den kommunalen Versicherer klären
- [ ] Einsatzablauf schriftlich festhalten (Abschnitt 7 im Konzept ist der
      Entwurf), zwei Leute einweisen

---

# Phase F — Optional: LTE nachrüsten

- [ ] SIM7600-Modem an den Pi, WLAN bleibt Rückfallebene (55 € + Tarif)
- [ ] Zugang absichern, bevor die Bodenstation aus dem Internet erreichbar ist
- [ ] Damit sehen Einsatzleitung und Leitstelle das Bild live mit

---

## Womit du **jetzt** anfängst

1. **Den Nachtversuch mit der Wärmebildkamera der Wehr machen** (A0) —
   kostet nichts, braucht keine Software und beantwortet die Frage, an der
   alles hängt. [messprotokoll.html](messprotokoll.html) ausdrucken und los.
2. **Kompetenznachweis A1/A3 online machen** — kostenlos, ein Nachmittag,
   und er gilt fünf Jahre
3. **Simulator einrichten und schweben üben** — jede Stunde dort spart später
   Propeller
4. **Halter in CAD konstruieren** — Maße aus den Datenblättern, zweiteilig
   bauen (Grundplatte plus wechselbare Kameraschale), dann blockiert eine
   unsichere Kameraabmessung nichts
5. Wenn du magst: Python installieren und die Simulation starten (A1) —
   `cd sensor`, dann `python3 suchkopf.py`, unter Windows `py suchkopf.py`

Das kostet zusammen keinen Cent und bringt dich bis an die Bestellung heran.
