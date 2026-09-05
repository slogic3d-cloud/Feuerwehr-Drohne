"""Legt den Suchkopf-Ordner in den Suchpfad, damit die Tests ihn finden."""

import os
import sys

WURZEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SENSOR = os.path.join(WURZEL, "sensor")
if SENSOR not in sys.path:
    sys.path.insert(0, SENSOR)
