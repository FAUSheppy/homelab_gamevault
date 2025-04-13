# in the background queue write filename in sqlite db
# get filename for sqlitedb
# get the size with info=1 from server
# only display for size>10M
# make a list of pregressbars

# start background thread with main list and main widget
# update list and widget

# update list and widget
import customtkinter as ctk
from tkinter import ttk
import threading
import random
import time
import string
import statekeeper
import os

class ProgressBarApp:
    def __init__(self, parent, data_backend):

        self.data_backend = data_backend
        self.parent = parent
        self.root = ctk.CTkFrame(parent)
        #self.root.title("Dynamic Progress Bars")

        self.delete_all_button = ctk.CTkLabel(self.root, text="Downloads")
        self.delete_all_button.pack(pady=5)

        self.delete_all_button = ctk.CTkButton(self.root, text="Delete All Finished", command=self.delete_all_finished, state=ctk.DISABLED)
        self.delete_all_button.pack(pady=5)

        self.frame = ctk.CTkFrame(self.root)
        self.frame.pack(pady=10)

        self.progress_bars = []  # Store tuples of (progressbar, frame, duration, delete_button)

        self.running = True
        self.root.after(0, self.start_tracking_progress_bars)

    def start_tracking_progress_bars(self):

        self.already_tracked = set()
        self.check_for_new_progress_bars()

    def check_for_new_progress_bars(self):

        downloads = set(statekeeper.get_download())
        new = downloads - self.already_tracked
        self.already_tracked |= downloads

        for element in new:
            frame = ctk.CTkFrame(self.frame)
            frame.pack(fill=ctk.X, pady=2)

            progress = ttk.Progressbar(frame, length=200, mode='determinate')
            progress.pack(side=ctk.LEFT, padx=5)

            delete_button = ctk.CTkButton(frame, text="Delete", command=lambda f=frame: self.delete_progress(f), state=ctk.DISABLED)
            delete_button.pack(side=ctk.LEFT, padx=5)

            label = ctk.CTkLabel(frame, text=os.path.basename(element.path))
            label.pack(side=ctk.LEFT, padx=5)

            self.progress_bars.insert(0, (progress, frame, delete_button))  # Insert at the top
            frame.pack(fill=ctk.X, pady=2, before=self.frame.winfo_children()[-1] if self.frame.winfo_children() else None)

            print("Starting tracker for", element.path)
            threading.Thread(target=self.fill_progress, args=(progress, element.path, frame, delete_button), daemon=True).start()

        # Schedule the next check in 2 seconds
        if self.running:
            self.root.after(2000, self.check_for_new_progress_bars)

    def fill_progress(self, progress, path, frame, delete_button):

        fail_count = 0
        same_size_count = 0
        prev_precent = 0
        while True:

            print("Checking download progress..")

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
            if percent_filled >= 99.9:
                self.root.after(0, progress.configure, { "value" : 100 })
                print("Finished", path)
                break
            else:
                self.root.after(0, progress.configure, { "value" : percent_filled })                
                time.sleep(0.5)

            # check for stuck downloads #
            print("same size count", same_size_count)
            if prev_precent == percent_filled:
                same_size_count += 1
            else:
                same_size_count = 0
            if same_size_count > 100:
                self.root.after(0, delete_button.configure, {"state": ctk.NORMAL, "text": "Failed - Delete file manually!"})
                self.progress_bars.append((progress, frame, path, delete_button))
                self.update_delete_all_button()
                statekeeper.log_end_download(path)
                self.data_backend.local_delete_cache_file(path)
                break
            prev_precent = percent_filled

        # handle finished download #
        self.root.after(0, delete_button.configure, {"state": ctk.NORMAL})
        self.progress_bars.append((progress, frame, path, delete_button))
        self.update_delete_all_button()

    def delete_progress(self, frame):
        frame.destroy()
        self.progress_bars = [(p, f, d) for p, f, d in self.progress_bars if f != frame]
        self.update_delete_all_button()

    def delete_all_finished(self):
        for _, frame, _, _ in self.progress_bars:
            frame.destroy()
        self.progress_bars.clear()
        self.update_delete_all_button()

    def update_delete_all_button(self):
        if self.progress_bars:
            self.delete_all_button.configure(state=ctk.NORMAL)
        else:
            self.delete_all_button.configure(state=ctk.DISABLED)

    def on_close(self):
        self.running = False
        self.root.destroy()