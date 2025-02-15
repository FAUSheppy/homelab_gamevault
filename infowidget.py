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

class ProgressBarApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Dynamic Progress Bars")
        
        self.delete_all_button = tk.Button(root, text="Delete All Finished", command=self.delete_all_finished, state=tk.DISABLED)
        self.delete_all_button.pack(pady=5)
        
        self.frame = tk.Frame(root)
        self.frame.pack(pady=10)
        
        self.progress_bars = []  # Store tuples of (progressbar, frame, duration, delete_button)
        
        self.running = True
        threading.Thread(target=self.add_progress_bars, daemon=True).start()

    def add_progress_bars(self):
        while self.running:
            time.sleep(3)  # Wait before adding a new progress bar
            
            frame = tk.Frame(self.frame)
            frame.pack(fill=tk.X, pady=2)
            
            progress = ttk.Progressbar(frame, length=200, mode='determinate')
            progress.pack(side=tk.LEFT, padx=5)
            
            delete_button = tk.Button(frame, text="Delete", command=lambda f=frame: self.delete_progress(f), state=tk.DISABLED)
            delete_button.pack(side=tk.LEFT, padx=5)
            
            random_letter = random.choice(string.ascii_uppercase)
            label = tk.Label(frame, text=random_letter)
            label.pack(side=tk.LEFT, padx=5)
            
            duration = random.randint(1, 10)  # Random fill time
            threading.Thread(target=self.fill_progress, args=(progress, duration, frame, delete_button), daemon=True).start()

    def fill_progress(self, progress, duration, frame, delete_button):
        for i in range(101):  # Fill progress bar over 'duration' seconds
            time.sleep(duration / 100)
            if not progress.winfo_exists():  # Check if progress bar still exists
                return
            self.root.after(0, progress.config, {"value": i})
        
        self.root.after(0, delete_button.config, {"state": tk.NORMAL})
        
        self.progress_bars.append((progress, frame, duration, delete_button))
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

if __name__ == "__main__":
    root = tk.Tk()
    app = ProgressBarApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
