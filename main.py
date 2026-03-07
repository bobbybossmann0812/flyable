import tkinter as tk
from tkinter import filedialog
import threading
import subprocess
import time

from SimConnect import SimConnect, AircraftRequests


class MSFSWatcher:

    def __init__(self, gui):
        self.gui = gui
        self.program_path = None
        self.running = False
        self.started_program = False

    def select_program(self):
        path = filedialog.askopenfilename()
        if path:
            self.program_path = path
            self.gui.log("Programm gewählt: " + path)

    def start_watching(self):

        if not self.program_path:
            self.gui.log("Bitte zuerst ein Programm auswählen")
            return

        if self.running:
            self.gui.log("Überwachung läuft bereits")
            return

        self.running = True

        thread = threading.Thread(target=self.watch_sim, daemon=True)
        thread.start()

    def watch_sim(self):

        self.gui.safe_status("Warte auf MSFS...")

        sm = None

        while sm is None and self.running:

            try:
                sm = SimConnect()
                self.gui.safe_log("SimConnect verbunden")

            except Exception as e:
                self.gui.safe_log("MSFS noch nicht gestartet...")
                time.sleep(5)

        if not self.running:
            return

        self.gui.safe_status("MSFS erkannt")

        try:
            aq = AircraftRequests(sm, _time=2000)
        except Exception as e:
            self.gui.safe_log("AircraftRequests Fehler: " + str(e))
            return

        loaded = False

        while not loaded and self.running:

            try:

                altitude = aq.get("PLANE_ALTITUDE")

                if altitude is not None:

                    loaded = True
                    self.gui.safe_status("Flug geladen")
                    self.gui.safe_log("Altitude erkannt: " + str(altitude))

            except Exception as e:
                self.gui.safe_log("SimConnect Fehler: " + str(e))

            time.sleep(2)

        if loaded and not self.started_program:

            self.started_program = True

            try:
                subprocess.Popen(self.program_path)
                self.gui.safe_log("Programm gestartet")

            except Exception as e:
                self.gui.safe_log("Fehler beim Starten: " + str(e))

    def stop_watching(self):
        self.running = False
        self.gui.safe_status("Überwachung gestoppt")
        self.gui.safe_log("Überwachung beendet")

class GUI:

    def __init__(self):

        self.root = tk.Tk()
        self.root.title("MSFS Auto Launcher")
        self.root.geometry("520x360")

        self.status_label = tk.Label(
            self.root,
            text="Status: Inaktiv",
            font=("Arial", 12)
        )
        self.status_label.pack(pady=10)

        self.select_button = tk.Button(
            self.root,
            text="Programm auswählen",
            width=25
        )
        self.select_button.pack(pady=5)

        self.start_button = tk.Button(
            self.root,
            text="Überwachung starten",
            width=25
        )

        self.stop_button = tk.Button(
            self.root,
            text="Überwachung stoppen",
            width=25
        )
        self.stop_button.pack(pady=5)

        self.start_button.pack(pady=5)

        self.log_box = tk.Text(
            self.root,
            height=12
        )
        self.log_box.pack(fill="both", padx=10, pady=10)

        self.watcher = MSFSWatcher(self)

        self.select_button.config(command=self.watcher.select_program)
        self.start_button.config(command=self.watcher.start_watching)
        self.stop_button.config(command=self.watcher.stop_watching)

    def set_status(self, text):
        self.status_label.config(text="Status: " + text)

    def log(self, text):
        self.log_box.insert(tk.END, text + "\n")
        self.log_box.see(tk.END)

    def safe_status(self, text):
        self.root.after(0, self.set_status, text)

    def safe_log(self, text):
        self.root.after(0, self.log, text)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = GUI()
    app.run()