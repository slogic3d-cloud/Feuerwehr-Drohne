# Arbeitsplan

Was in welcher Reihenfolge zu tun ist, damit aus dem Code ein Gerät wird, das
im Einsatz wirklich hilft. Das **Warum** und die technischen Begründungen
stehen in [KONZEPT.md](KONZEPT.md) — hier steht das **Was, wann und womit**.

**Stand heute:** Software fertig und getestet (84 Tests, läuft im
Simulationsmodus). Hardware: nichts gekauft.

---

## Die Grundregel des Plans

> **Erst muss die Erkennung am Boden funktionieren, dann wird geflogen.**

Der Grund ist unbequem, aber wichtig: Wenn du zuerst die Drohne baust und die
Erkennung erst in der Luft ausprobierst, weißt du bei jedem Fehlschlag nicht,
ob es an der Kamera, an den Schwellen, an der Höhe, an den Vibrationen oder am
Wetter lag. Und jeder Testflug kostet Akku, Zeit und irgendwann Hardware.

Ein Aufbau, den du in der Hand über die Wiese trägst, kostet 260 € und
beantwortet die entscheidende Frage: **Erkennt das Ding einen Menschen?**
Wenn nicht, hast du 260 € statt 700 € ausgegeben.

---

## Etappe 0 — Heute Abend, ohne einen Cent

**Zeit:** 30 Minuten

- [ ] Simulation starten und die Bodenstation ansehen
      ```bash
      cd sensor && python3 suchkopf.py
      ```
      Dann `http://localhost:8080/` im Browser öffnen.
- [ ] Tests laufen lassen: `cd tests && python3 -m unittest discover -s .`
- [ ] [KONZEPT.md](KONZEPT.md) lesen — **besonders Abschnitt 2 (die ehrlichen
      Grenzen) und Abschnitt 8 (Recht)**
- [ ] Für dich klären: Hast du schon eine RC-Fernsteuerung und ein
      LiPo-Ladegerät? Das entscheidet, ob das Projekt 600 € oder 715 € kostet.

**Fertig, wenn:** Du das Wärmebild im Browser gesehen hast und dir klar ist,
was das Gerät kann — und was es nicht kann.

---

## Etappe 1 — Erkennung am Boden beweisen

**Zeit:** 2 Wochenenden · **Kosten:** 260 € · **Das ist der wichtigste Schritt**

### Einkaufen

| Teil | Preis |
|---|---:|
| InfiRay P2 Pro oder Topdon TC001 (256×192, USB-C) | 230 € |
| Raspberry Pi Zero 2 W + SD-Karte + OTG-Adapter | 30 € |

### Aufgaben

- [ ] **1.1** Raspberry Pi OS Lite (64 Bit) auf die Karte, WLAN und SSH schon
      beim Schreiben eintragen — der Pi Zero hat keinen brauchbaren
      Bildschirmanschluss für nebenbei
- [ ] **1.2** Repo auf den Pi holen, `sudo apt install python3-opencv`
      (nur der Kameratreiber braucht das)
- [ ] **1.3** Kamera über den OTG-Adapter anstecken, prüfen ob sie als
      `/dev/video0` auftaucht (`v4l2-ctl --list-devices`)
- [ ] **1.4** Erster echter Lauf:
      ```bash
      WAERMEBILD_TYP=infiray python3 suchkopf.py
      ```
      Vom Handy aus `http://<Pi-Adresse>:8080/` öffnen
- [ ] **1.5** **Messreihe im Garten:** Jemand legt sich hin, du hältst die
      Kamera aus 3, 5, 10 und 15 m Abstand drauf. Notieren: Welche Abhebung in
      Kelvin zeigt die Bodenstation? Wie viele Zellen hat der Fleck?
- [ ] **1.6** Schwellen in `sensor/konfig.py` nachziehen — vor allem
      `ABHEBUNG_K`, wenn dein Untergrund wärmer oder kälter ist als angenommen
- [ ] **1.7** Dasselbe **nachts** wiederholen. Der Unterschied wird dich
      überraschen — nachts ist alles viel deutlicher.
- [ ] **1.8** Optional: einen einfachen Handgriff mit Kamerahalter drucken,
      dann lässt sich bequemer messen

**Fertig, wenn:** Eine auf der Wiese liegende Person nachts zuverlässig als
Treffer gemeldet wird und ein Heizkörper oder eine Motorhaube nicht.

**Wenn es klemmt:** Die P2-Pro-Familie meldet sich als UVC-Kamera, aber nicht
alle Modelle liefern die Temperaturhälfte gleich. Wenn `WAERMEBILD_TYP=infiray`
nur Grütze zeigt: einmal das Rohformat prüfen (`v4l2-ctl --list-formats-ext`),
dann melden — der Treiber in `sensor/geraete/waermebild.py` ist eine
überschaubare Funktion, die sich anpassen lässt. Der Pi Zero 2 W ist bei
25 Bildern je Sekunde am Limit; deshalb läuft der Suchkopf mit 8 Hz. Reicht
das nicht, ist ein Pi 4 der Ausweg (+ 40 g, + 50 €).

---

## Etappe 2 — Flugzelle bauen und fliegen lernen

**Zeit:** 3–4 Wochenenden · **Kosten:** 325 € (+ 115 € falls Sender und
Ladegerät fehlen)

### Einkaufen

Rahmen 7 Zoll · 4 Motoren 2807/1300 KV · 4-in-1-Regler · F405-Stack ·
Propeller · GPS M10 · ELRS-Empfänger · Li-Ion 6S2P
(vollständige Liste mit Preisen in [KONZEPT.md](KONZEPT.md), Abschnitt 5)

### Aufgaben

- [ ] **2.1** Aufbauen und löten — Motoren, Regler, Flugregler, GPS, Empfänger
- [ ] **2.2** ArduPilot flashen und Erstkonfiguration (Rahmentyp,
      Motorreihenfolge, Drehrichtungen)
- [ ] **2.3** Kalibrieren: Beschleunigungsmesser, Kompass, Regler, Funk, Akku
- [ ] **2.4** **Failsafes setzen** — das ist keine Fleißaufgabe:
      Rückkehr zum Startpunkt bei Funkverlust, Akkuwarnung, Höhenbegrenzung
- [ ] **2.5** Erstflug ohne Nutzlast auf freier Fläche, weit weg von allem
- [ ] **2.6** **Zehn Akkus leerfliegen.** Schweben, Kreise, Rückkehrfunktion
      ausprobieren, Notfallabschaltung üben. Erst danach kommt die 230-€-Kamera
      an das Gerät.

**Fertig, wenn:** Zehn Flüge ohne Schaden, die Rückkehrfunktion funktioniert
und du dich beim Fliegen nicht mehr verkrampfst.

---

## Etappe 3 — Zusammenbau

**Zeit:** 1 Wochenende · **Kosten:** ca. 15 € (Druckmaterial, BEC, Kleinteile)

- [ ] **3.1** Halter für Kamera (nach unten blickend) und Pi konstruieren und
      in ABS oder ABS-CF drucken
- [ ] **3.2** Stromversorgung für den Pi: 5 V / 3 A BEC vom Hauptakku
- [ ] **3.3** Montieren, Schwerpunkt prüfen, Kabel gegen Vibration sichern
- [ ] **3.4** **Flugzeit mit Nutzlast messen** — die echte Zahl, nicht die
      gerechnete
- [ ] **3.5** Im Schwebeflug das Wärmebild ansehen: Ist es scharf? Was zeigt
      die Böigkeitsanzeige? Zu viel Vibration heißt: Dämpfung unter die
      Kamerahalterung

**Fertig, wenn:** Im Flug kommt ein brauchbares Bild auf dem Tablet an und du
kennst deine tatsächliche Flugzeit.

---

## Etappe 4 — Trefferquote messen und Modell trainieren

**Zeit:** laufend · **Kosten:** 0 € · **Das ist die Etappe, die zählt**

Ohne diese Zahlen ist das Gerät ein Bastelprojekt. Mit ihnen ist es ein
Einsatzmittel, über das man mit der Wehrführung reden kann.

- [ ] **4.1** Nachts auf eine abgemähte Wiese. Ein Helfer legt sich an eine
      Stelle, **die du nicht kennst** (jemand Drittes weist ihn ein)
- [ ] **4.2** In 20, 30, 40, 50 und 60 m Höhe überfliegen. Notieren:
      gefunden ja/nein, nach wie vielen Sekunden, welches Vertrauen
- [ ] **4.3** Jede Fundstelle am Tablet als „Person" oder „Fehlalarm" bewerten
- [ ] **4.4** Nach jedem Abend trainieren: `python3 lernen.py`
- [ ] **4.5** Wiederholen unter anderen Bedingungen: Stoppelfeld, hohes Gras,
      Waldrand, leichter Regen, tagsüber
- [ ] **4.6** Eine Tabelle führen: **Höhe → Trefferquote → Fehlalarme je Flug**

**Fertig, wenn:** Du den Satz sagen kannst: „Bei 40 m Höhe über abgemähter
Wiese finde ich nachts 9 von 10 Personen, mit im Schnitt 2 Fehlalarmen je Flug."

---

## Etappe 5 — Aus dem Bastelprojekt wird ein Einsatzmittel

**Zeit:** je nach Behörde · **Kosten:** gering, aber Zeit

- [ ] **5.1** Kompetenznachweis A1/A3 beim Luftfahrt-Bundesamt — Online-Test,
      kostenlos, ein Nachmittag. **Das kannst du schon in Etappe 1 machen.**
- [ ] **5.2** Betreiberregistrierung beim LBA (e-ID), Plakette ans Gerät
- [ ] **5.3** Dem Kommandanten vorführen — mit den Zahlen aus Etappe 4, nicht
      mit Versprechen
- [ ] **5.4** Über die Kreisbrandinspektion an das Luftamt Nordbayern:
      Was braucht es für Einsatzflüge über A3 hinaus?
- [ ] **5.5** Versicherung klären. Die private Drohnenversicherung deckt
      Einsatzflüge in der Regel **nicht**.
- [ ] **5.6** Einsatzablauf schriftlich festhalten (Abschnitt 7 im Konzept ist
      der Entwurf dafür), zwei Leute einweisen — ein Gerät, das nur einer
      bedienen kann, ist im Einsatz nicht verfügbar

---

## Etappe 6 — Optional: LTE nachrüsten

**Zeit:** 1 Wochenende · **Kosten:** 55 € + Tarif

- [ ] SIM7600-Modem an den Pi, WLAN bleibt als Rückfallebene
- [ ] Zugang absichern, bevor die Bodenstation aus dem Internet erreichbar ist
- [ ] Damit sehen Einsatzleitung und Leitstelle das Bild live mit

---

## Einkaufen in der richtigen Reihenfolge

Geld erst ausgeben, wenn die vorige Etappe steht:

| Wann | Was | Betrag |
|---|---|---:|
| jetzt | Wärmebildkamera + Pi Zero 2 W | 260 € |
| nach Etappe 1 | Flugzelle, Akku, (Sender, Ladegerät) | 325–440 € |
| nach Etappe 2 | BEC, Druckmaterial, Kleinteile | 15 € |
| später | LTE-Modem | 55 € |

---

## Was noch offen ist

| Frage | Warum sie zählt |
|---|---|
| Hast du RC-Sender und Ladegerät? | Entscheidet über 600 € oder 715 € |
| 3D-Drucker mit geschlossener Kammer? | ABS zieht sich sonst beim Drucken krumm — sonst PETG nehmen und auf die 80 °C verzichten |
| Wo darfst du üben? | Für A3 brauchst du 150 m Abstand zu Wohngebieten. Feld hinter dem Ort? Modellflugplatz? |
| Wer macht mit? | Alleine ist es machbar, aber ein zweiter Bediener wird für Etappe 5 sowieso gebraucht |

---

## Womit du **jetzt** anfängst

1. **Simulation starten** (`cd sensor && python3 suchkopf.py`, dann
   `localhost:8080`) — 10 Minuten, kostet nichts, und du siehst, worauf das
   Ganze hinausläuft.
2. **Kamera und Pi bestellen** — 260 €. Das ist die Ausgabe, die die
   entscheidende Frage beantwortet.
3. **Kompetenznachweis A1/A3 online machen** — kostenlos, ein Nachmittag, und
   er läuft im Hintergrund, während die Teile unterwegs sind.

Alles andere kann warten, bis die Kamera da ist.
