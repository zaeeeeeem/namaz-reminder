import tkinter as tk
from tkinter import ttk


class MainWindow:
    """Primary application window showing prayer times and status."""

    def __init__(self, parent):
        self.root = tk.Toplevel(parent)
        self.setup_ui()

    def setup_ui(self):
        self.root.title("Namaz Reminder")
        self.root.geometry("600x400")

        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Prayer times display
        times_frame = ttk.LabelFrame(main_frame, text="Today's Prayer Times")
        times_frame.pack(fill=tk.X, pady=5)

        # Add prayer time labels
        prayers = ['Fajr', 'Dhuhr', 'Asr', 'Maghrib', 'Isha']
        for prayer in prayers:
            row = ttk.Frame(times_frame)
            row.pack(fill=tk.X, pady=2)

            ttk.Label(row, text=prayer, width=10).pack(side=tk.LEFT)
            ttk.Label(row, text="--:--", width=8).pack(side=tk.LEFT)
            ttk.Button(row, text="Mark Complete", width=12).pack(side=tk.RIGHT)