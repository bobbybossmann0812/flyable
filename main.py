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

    def select_program(self):
        path = filedialog.askopenfilename()
        if path:
            self.program_path = path
            self.gui.log("Programm gewählt: " + path)

    def start_watching(self):
        if not self.program_path:
            self.gui.log("Bitte zuerst ein Programm auswählen")
            return

        self.running = True
        thread = threading.Thread(target=self.watch_sim)
        thread.start()

    def watch_sim(self):

        self.gui.set_status("Warte auf MSFS...")

        sm = None

        while sm is None and self.running:
            try:
                sm = SimConnect()
            except:
                time.sleep(5)

        if not self.running:
            return

        self.gui.set_status("MSFS erkannt")

        aq = AircraftRequests(sm, _time=2000)

        loaded = False

        while not loaded and self.running:
            try:
                altitude = aq.get("PLANE ALTITUDE")

                if altitude is not None:
                    loaded = True
            except:
                pass

            time.sleep(2)

        if loaded:
            self.gui.set_status("Flug geladen")
            self.gui.log("Starte Programm...")

            subprocess.Popen(self.program_path)


class GUI:

    def __init__(self):

        self.root = tk.Tk()
        self.root.title("Flyable - the MSFS Auto Launcher")
        self.root.geometry("500x350")

        self.status_label = tk.Label(self.root, text="Status: Inaktiv", font=("Arial", 12))
        self.status_label.pack(pady=10)

        self.start_button = tk.Button(self.root, text="Überwachung starten")
        self.start_button.pack(pady=5)

        self.select_button = tk.Button(self.root, text="Programm auswählen")
        self.select_button.pack(pady=5)

        self.log_box = tk.Text(self.root, height=10)
        self.log_box.pack(fill="both", padx=10, pady=10)

        self.watcher = MSFSWatcher(self)

        self.start_button.config(command=self.watcher.start_watching)
        self.select_button.config(command=self.watcher.select_program)

    def set_status(self, text):
        self.status_label.config(text="Status: " + text)

    def log(self, text):
        self.log_box.insert(tk.END, text + "\n")
        self.log_box.see(tk.END)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = GUI()
    app.run()
