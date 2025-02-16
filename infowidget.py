# in the background queue write filename in sqlite db
# get filename for sqlitedb
# get the size with info=1 from server
# only display for size>10M
# make a list of pregressbars

# start background thread with main list and main widget
# update list and widget

# update list and widget
import tkinter as tk
from tkinter import ttk
import threading
import random
import time
import string
import statekeeper
import os

class ProgressBarApp:
    def __init__(self, parent):

        self.root = tk.Toplevel(parent)
        self.root.title("Dynamic Progress Bars")

        self.delete_all_button = tk.Button(self.root, text="Delete All Finished", command=self.delete_all_finished, state=tk.DISABLED)
        self.delete_all_button.pack(pady=5)

        self.frame = tk.Frame(self.root)
        self.frame.pack(pady=10)

        self.progress_bars = []  # Store tuples of (progressbar, frame, duration, delete_button)

        self.running = True
        threading.Thread(target=self.add_progress_bars, daemon=True).start()

    def add_progress_bars(self):

        already_tracked = set()
        while self.running:

            downloads = set(statekeeper.get_download())
            new = downloads - already_tracked
            already_tracked |= set(downloads)

            for element in new:

                frame = tk.Frame(self.frame)
                frame.pack(fill=tk.X, pady=2)

                progress = ttk.Progressbar(frame, length=200, mode='determinate')
                progress.pack(side=tk.LEFT, padx=5)

                delete_button = tk.Button(frame, text="Delete", command=lambda f=frame: self.delete_progress(f), state=tk.DISABLED)
                delete_button.pack(side=tk.LEFT, padx=5)

                label = tk.Label(frame, text=os.path.basename(element.path))
                label.pack(side=tk.LEFT, padx=5)

                self.progress_bars.insert(0, (progress, frame, delete_button))  # Insert at the top
                frame.pack(fill=tk.X, pady=2, before=self.frame.winfo_children()[-1] if self.frame.winfo_children() else None)

                print("Starting tracker for", element.path)
                threading.Thread(target=self.fill_progress, args=(progress, element.path, frame, delete_button), daemon=True).start()

            time.sleep(2)  # Wait before adding a new progress bar

    def fill_progress(self, progress, path, frame, delete_button):

        fail_count = 0
        while True:

            if not progress.winfo_exists():  # Check if progress bar still exists
                return

            try:
                percent_filled = statekeeper.get_percent_filled(path)
            except OSError as e:
                fail_count += 1
                if fail_count > 6:
                    raise e
                else:
                    time.sleep(1)
                    continue

            print("Percent filled:", percent_filled, path)
            if not percent_filled or percent_filled >= 99.9:
                self.root.after(0, progress.config, { "value" : 100 })
                break
            else:
                self.root.after(0, progress.config, { "value" : percent_filled })                
                time.sleep(0.5)

        # handle finished download #
        self.root.after(0, delete_button.config, {"state": tk.NORMAL})
        self.progress_bars.append((progress, frame, path, delete_button))
        self.update_delete_all_button()

    def delete_progress(self, frame):
        frame.destroy()
        self.progress_bars = [(p, f, d, b) for p, f, d, b in self.progress_bars if f != frame]
        self.update_delete_all_button()

    def delete_all_finished(self):
        for _, frame, _, _ in self.progress_bars:
            frame.destroy()
        self.progress_bars.clear()
        self.update_delete_all_button()

    def update_delete_all_button(self):
        if self.progress_bars:
            self.delete_all_button.config(state=tk.NORMAL)
        else:
            self.delete_all_button.config(state=tk.DISABLED)

    def on_close(self):
        self.running = False
        self.root.destroy()