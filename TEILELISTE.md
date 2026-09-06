# Teileliste

Vollständige Einkaufsliste für die Suchdrohne. Die Übersicht in
[KONZEPT.md](KONZEPT.md) nennt nur die Hauptteile — hier steht alles, auch der
Kleinkram, an dem ein Aufbau sonst am Samstagabend scheitert.

**Reihenfolge:** Technik und Gehäuse zuerst, Software zum Schluss.

---

## Zwei Korrekturen gegenüber dem Konzept

Beim Durchrechnen der Einzelteile sind zwei Zahlen im Konzept nicht
haltbar geblieben:

1. **Der Akku war falsch angesetzt.** „6S2P, ca. 3 Ah, 90 €" stimmt nicht:
   Ein 6S2P-Pack aus P42A-Zellen hat **8,4 Ah** (12 Zellen, rund 180 Wh,
   840 g) und kostet fertig konfektioniert **110–130 €**. Die günstigere
   Alternative ist 6S1P — halbes Gewicht, halbe Flugzeit, 60–70 €.
2. **Die 600-€-Summe war die Hauptteileliste.** Mit Ladegerät, Steckern,
   Litze, Schrauben, Dämpfern und dem übrigen Kleinkram landet ein
   vollständiger Aufbau realistisch bei **700–760 €**, wenn Sender,
   Lötausrüstung und Filament vorhanden sind.

Beides steht unten in den Tabellen richtig.

---

## A · Flugzelle und Antrieb

| ✓ | Teil | Anz. | Was genau | Preis | Worauf achten |
|---|---|---|---|---:|---|
| ☐ | Rahmen | 1 | 7-Zoll-Langstreckenrahmen, Carbon, 5 mm Arme | 40 € | Platz für ein großes Akkupack **oben** und Montagefläche für die Kamera **unten**. Ersatzarme müssen einzeln nachkaufbar sein — du wirst welche brauchen. |
| ☐ | Motoren | 4 | 2807 oder 2806.5, ca. 1300 KV, 6S-tauglich | 60 € | Lochbild 16 × 16 mm, M5-Welle. KV nicht höher wählen — hohe Drehzahl kostet Flugzeit. |
| ☐ | Propeller | 3 Sätze | 7 × 4 Zoll, **zweiblatt** | 15 € | Zweiblatt ist deutlich effizienter als dreiblatt. Ersatz gleich mitbestellen. |
| ☐ | Regler | 1 | 4-in-1, 45–50 A, 6S, BLHeli_32 oder AM32 | 40 € | Lochbild 30,5 × 30,5 mm, passend zum Flugregler. |
| ☐ | Flugregler | 1 | **Matek F405-TE** oder H743-SLIM | 45–90 € | **Das wichtigste Teil zum Nachprüfen:** Es muss im ArduPilot-Firmwareverzeichnis ein Ziel für genau dieses Board geben. Matek-Boards sind bei ArduPilot am besten unterstützt. Der H743 kostet doppelt, hat aber Reserven — F405-Boards werden bei neueren ArduPilot-Versionen knapp im Speicher. |
| ☐ | GPS + Kompass | 1 | M10-Modul mit Kompass (z. B. QMC5883) | 28 € | Kompass muss dabei sein, sonst funktioniert Positionshalten nicht. Auf einen Mast setzen, weg von den Stromkabeln. |
| ☐ | Empfänger | 1 | ExpressLRS 2,4 GHz, Diversity (zwei Antennen) | 15 € | Muss zum Sender passen. Diversity, weil die Drohne sich beim Bahnenfliegen wegdreht. |
| ☐ | Summer | 1 | Piepser für ArduPilot, 5 V | 5 € | Klingt nach Kleinkram, ist es nicht: Damit findest du die Drohne nachts im hohen Gras wieder. |
| ☐ | Positionslicht | 1 | **grün blinkend** | 10 € | **Vorgeschrieben für Nachtflug.** Ohne das darfst du nachts nicht fliegen — und nachts ist die beste Suchzeit. |
| | | | | **258 €** | |

## B · Energie

| ✓ | Teil | Anz. | Was genau | Preis | Worauf achten |
|---|---|---|---|---:|---|
| ☐ | Akku **Variante lang** | 1 | Li-Ion 6S2P, P42A oder Samsung 40T, 8,4 Ah, mit XT60 | 120 € | 12 Zellen, rund 840 g, 180 Wh. Damit sind **30–40 min** realistisch. Fertig konfektioniert kaufen, nicht selbst punktschweißen, solange du das nicht sicher kannst. |
| ☐ | Akku **Variante leicht** | 1 | Li-Ion 6S1P, 4,2 Ah | 65 € | Halbes Gewicht, rund **20–25 min**. Gute Wahl, um erst einmal anzufangen. |
| ☐ | Ladegerät | 1 | Balancer-Lader, 6S, mind. 100 W | 45 € | Muss **Li-Ion** können, nicht nur LiPo — das ist ein eigener Lademodus mit anderer Endspannung. |
| ☐ | Ladebeutel | 1 | LiPo-Safe-Beutel oder Munitionskiste | 10 € | Nicht optional. Li-Ion ist gutmütiger als LiPo, aber nicht harmlos. |
| ☐ | Spannungswarner | 1 | Piepser am Balancerstecker | 5 € | Zweite Ebene neben der Akkuwarnung im Flugregler. |
| ☐ | XT60-Stecker | 5 Paar | mit Gehäuse | 8 € | Immer ein paar mehr — die ersten Lötversuche werden nicht schön. |
| | | | | **123–178 €** | |

## C · Nutzlast

| ✓ | Teil | Anz. | Was genau | Preis | Worauf achten |
|---|---|---|---|---:|---|
| ☐ | Wärmebildkamera | 1 | InfiRay P2 Pro oder Topdon TC001, 256 × 192, USB-C | 230 € | **Die Handy-Variante mit USB-C-Stecker.** Sie muss echte Temperaturwerte liefern, nicht nur ein Falschfarbenbild. 9 g, das ist der Grund für genau dieses Modell. |
| ☐ | Rechner | 1 | Raspberry Pi Zero 2 W | 20 € | Version **2 W**, nicht die alte. Ohne Steckerleiste bestellen spart Gewicht. |
| ☐ | Speicherkarte | 1 | microSD 32 GB, A1 oder A2 | 8 € | Billige Karten sterben unter Dauerschreiben. Markenware nehmen. |
| ☐ | OTG-Adapter | 1 | USB-C-**Buchse** auf Micro-USB-**Stecker** | 6 € | Der Pi Zero hat nur Micro-USB. Muss OTG können, sonst erkennt er die Kamera nicht. Kurz halten. |
| ☐ | Spannungsregler | 1 | BEC 5 V / 3 A | 10 € | Versorgt den Pi aus dem Hauptakku. Der Pi zieht Spitzen um 0,7 A — 3 A ist Reserve, kein Luxus. |
| ☐ | *später* LTE-Modem | 1 | SIM7600G-H mit Antenne | 55 € | Erst nach Phase F. Vorher nicht kaufen. |
| | | | | **274 €** | |

## D · Gehäuse und Mechanik

Das meiste druckst du selbst — hier steht, was du **zusätzlich** brauchst.

| ✓ | Teil | Anz. | Was genau | Preis | Worauf achten |
|---|---|---|---|---:|---|
| ☐ | Filament | 1 kg | ABS oder ABS-CF | 30 € | Nur wenn dein Drucker eine geschlossene Kammer hat. Sonst PETG nehmen — dann fällt die 80-°C-Festigkeit weg, was für reine Suchflüge kein Problem ist. |
| ☐ | Schrauben M3 | Sortiment | 6–20 mm, Innensechskant, Nylonmuttern | 10 € | Für Rahmen und Halter. |
| ☐ | Schrauben M2,5 | Sortiment | 6–12 mm | 5 € | Für den Raspberry Pi: Lochbild **58 × 23 mm**, Platine 65 × 30 mm. |
| ☐ | Abstandshalter | 1 Satz | Nylon, M2,5, 5–10 mm | 5 € | Nylon, nicht Metall — spart Gewicht und schließt Kurzschlüsse aus. |
| ☐ | Dämpferkugeln | 4–8 | Gummi-Dämpfer für Kameraaufhängung | 5 € | Gegen Motorvibration. Ohne die verschmiert das Wärmebild. |
| ☐ | Klettband | 1 Rolle | breit, für den Akku | 5 € | |
| ☐ | Kabelbinder | 100 | klein, 2,5 mm | 3 € | |
| ☐ | Schaumklebeband | 1 Rolle | doppelseitig, dick | 4 € | Zum Entkoppeln von Flugregler und GPS. |
| ☐ | Schrumpfschlauch | Sortiment | 2–10 mm | 6 € | |
| ☐ | Silikonlitze | je 1 m | 14 AWG rot/schwarz, 22 AWG bunt | 10 € | **Silikon**, nicht PVC — bleibt bei Kälte biegsam und verträgt den Lötkolben. |
| ☐ | Schraubensicherung | 1 | mittelfest (blau) | 7 € | Auf jede Motorschraube. Vibration dreht sonst alles auf. |
| | | | | **60–90 €** | |

## E · Fernsteuerung

| ✓ | Teil | Anz. | Was genau | Preis | Worauf achten |
|---|---|---|---|---:|---|
| ☐ | Sender | 1 | RadioMaster Pocket oder Boxer, **ELRS-Version** | 70–110 € | Nur nötig, wenn du noch keinen hast. Muss zum Empfänger passen (beide ELRS). Der Pocket reicht völlig. |
| ☐ | Senderakku | 2 | 18650-Zellen, falls nicht dabei | 12 € | |

## F · Werkzeug

Nur, was du wahrscheinlich noch nicht hast:

| ✓ | Teil | Was genau | Preis | Worauf achten |
|---|---|---|---:|---|
| ☐ | **Smoke Stopper** | Strombegrenzer für den ersten Einschaltversuch | 12 € | **Das billigste Teil auf dieser Liste und das mit dem besten Verhältnis.** Bei einer Lötbrücke stirbt sonst der komplette Stack für 85 €. |
| ☐ | Lötstation | mind. 60 W, mit Temperaturregelung | 45 € | Ein 30-W-Kolben schafft die Massefläche eines 4-in-1-Reglers nicht. |
| ☐ | Lötzinn | 0,8 mm, mit Flussmittelseele | 10 € | |
| ☐ | Messschieber | digital | 15 € | Brauchst du fürs Konstruieren der Halter. |
| ☐ | Multimeter | einfaches Gerät | 20 € | Durchgangsprüfer reicht, um Kurzschlüsse zu finden, bevor Strom fließt. |

---

## Summen

| Fall | Betrag |
|---|---:|
| **Deine Bestellung** — 6S1P, mit Sender und Ladegerät, vorhandenes Werkzeug abgezogen | **805 €** |
| Mit dem langen Akku 6S2P statt 6S1P (30–40 statt 20–25 min) | 860 € |
| Dasselbe ohne vorhandenes Werkzeug gerechnet | 939 € |
| Nur Phase C1 vorab: Kamera, Pi, Karte, Adapter | **264 €** |
| Nur der Sender, um früh im Simulator üben zu können | **82 €** |

Die letzte Zeile ist die wichtige: Auch wenn alles zusammen bestellt wird —
**Kamera und Pi zuerst auspacken und die Bodenmessreihe machen**, bevor an der
Flugzelle gelötet wird. Solange nichts angelötet ist, lässt sich der Rest noch
zurückschicken.

---

## Bestandsaufnahme

| Vorhanden | Fehlt noch |
|---|---|
| Lötstation, Lötzinn, Entlötlitze | RC-Sender mit ELRS |
| Innensechskantschlüssel, Torx | Balancer-Ladegerät für Li-Ion |
| Messschieber, Multimeter | |
| Filament für den Drucker | |
| Schrumpfschlauch, Kabelbinder, Klettband | |

Das vorhandene Werkzeug spart rund **134 €** — vor allem Lötstation und
Messwerkzeug.

---

## Die konkrete Bestellung

Mit dem 6S1P-Akku und dem oben aufgeführten Bestand. Alles, was gestrichen ist,
brauchst du nicht mehr zu kaufen.

| Block | Inhalt | Betrag |
|---|---|---:|
| A · Flugzelle | Rahmen, 4 Motoren, Regler, Flugregler, Propeller, GPS, Empfänger, Summer, Positionslicht | 258 € |
| B · Energie | Akku 6S1P, **Ladegerät**, Ladebeutel, Spannungswarner, XT60-Set | 133 € |
| C · Nutzlast | Wärmebildkamera, Pi Zero 2 W, SD-Karte, OTG-Adapter, BEC | 274 € |
| D · Mechanik | Schrauben M3 und M2,5, Abstandshalter, Dämpferkugeln, Schaumband, Silikonlitze, Schraubensicherung | 46 € |
| E · Fernsteuerung | **RadioMaster Pocket ELRS + 2 × 18650** | 82 € |
| F · Werkzeug | Smoke Stopper | 12 € |
| | **Summe** | **805 €** |

~~Filament, Schrumpfschlauch, Kabelbinder, Klettband, Lötstation, Lötzinn,
Messschieber, Multimeter~~ — vorhanden.

### Achtung beim Ladegerät

Die meisten günstigen Ladegeräte sind **Gleichstromgeräte**: Sie brauchen ein
separates 12-V-Netzteil, das nicht dabei ist. Das kostet noch einmal 25 € und
wird beim Kauf gern übersehen.

**Nimm ein Gerät mit eingebautem Netzteil** („AC/DC" oder „mit Netzanschluss").
Und es muss ausdrücklich **Li-Ion** können — das ist ein eigener Lademodus mit
4,2 V je Zelle Endspannung, nicht dasselbe wie LiPo. Ein Gerät, das nur LiPo
kann, lädt das Pack falsch.

### Der Sender ist das Teil, das sich früh lohnt

Der RadioMaster Pocket lässt sich per USB als Gamepad am Rechner benutzen. Damit
kannst du das Simulatortraining aus Phase A2 mit **genau den Knüppeln** machen,
mit denen du später fliegst — das ist deutlich mehr wert als Üben mit einem
Xbox-Controller.

Wenn du also **ein** Teil vorziehen willst, dann dieses: 82 €, und du kannst
sofort mit dem Fliegenlernen anfangen, während der Rest der Bestellung noch
wartet. Muss aber nicht sein — der Plan funktioniert auch, wenn alles zusammen
kommt.

Alternative, die nichts kostet: Im Modellflugverein oder bei einem FPV-Flieger
in der Umgebung nach einem ausgemusterten Sender fragen. ELRS-Sender werden oft
weitergereicht, wenn jemand aufrüstet.

---

## Was bewusst **nicht** auf der Liste steht

| Nicht dabei | Warum |
|---|---|
| Radar | 6 m Reichweite — aus 40 m Höhe nutzlos. War die Idee für die verworfene Innenraumvariante. |
| Schutzkäfig | Kostet Gewicht und Flugzeit. Draußen fliegst du nicht gegen Wände. |
| Gasmessung | Gehört zum Innenangriff, nicht zur Flächensuche. |
| Gimbal | Die Kamera blickt starr nach unten. Ein Gimbal wäre 80 g und ein weiteres Teil, das ausfallen kann. |
| FPV-Videosystem | Du fliegst nach Sicht und nach Kartendarstellung, nicht im FPV-Brillenmodus. |
| Fallschirm | Erst relevant, wenn über Menschen geflogen wird — das ist in A3 ohnehin verboten. |
