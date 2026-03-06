import time
import subprocess
from SimConnect import SimConnect, AircraftRequests

print("Warte auf MSFS...")

sm = None

# Warten bis MSFS läuft
while sm is None:
    try:
        sm = SimConnect()
    except:
        time.sleep(5)

print("MSFS gefunden")

aq = AircraftRequests(sm, _time=2000)

flug_geladen = False

while not flug_geladen:
    try:
        altitude = aq.get("PLANE ALTITUDE")

        if altitude is not None:
            flug_geladen = True
    except:
        pass

    time.sleep(2)

print("Flug geladen – starte Programm")

# Öffnet das Programm, wenn Flug geladen
subprocess.Popen(["mein_programm.exe"])
