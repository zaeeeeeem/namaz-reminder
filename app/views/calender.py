import customtkinter as ctk
import os
import json
from datetime import datetime, timedelta
from app.utils.config import PRAYER_NAMES

STATUS_OPTIONS = ["Completed", "Late", "Not Completed"]
STATUS_COLORS = {
    "Completed": "green",
    "Late": "orange",
    "Not Completed": "gray"
}
STATUS_FILE = "prayer_status.json"

def load_status_data():
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_status_data(data):
    with open(STATUS_FILE, "w") as f:
        json.dump(data, f, indent=2)

def get_day_name(date_obj):
    return date_obj.strftime("%A")

def open_calendar_view(root_frame, get_today_times_callback, switch_to_dashboard):
    frame = ctk.CTkFrame(root_frame, fg_color="transparent")
    frame.pack(fill="both", expand=True)

    title = ctk.CTkLabel(frame, text="7-Day Prayer Calendar", font=ctk.CTkFont(size=22, weight="bold"))
    title.pack(pady=10)

    content = ctk.CTkScrollableFrame(frame, fg_color="transparent", width=360, height=350)
    content.pack(pady=10, padx=20)

    today = datetime.now().date()
    all_status = load_status_data()
    today_times = get_today_times_callback()

    var_refs = {}

    for i in range(7):
        date = today + timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d")
        display_date = date.strftime("%d %B - ") + get_day_name(date)

        day_label = ctk.CTkLabel(content, text=display_date, font=ctk.CTkFont(size=16, weight="bold"))
        day_label.pack(pady=(10 if i > 0 else 5, 5), anchor="w", padx=10)

        for prayer in PRAYER_NAMES:
            key = f"{date_str}_{prayer}"
            status = all_status.get(key, "Not Completed")
            var = ctk.StringVar(value=status)
            var_refs[key] = var

            disable = False
            if date == today:
                now_time = datetime.now().time()
                prayer_time_str = today_times.get(prayer)
                if prayer_time_str:
                    prayer_time = datetime.strptime(prayer_time_str, "%H:%M").time()
                    disable = now_time < prayer_time
                else:
                    disable = True
            elif date > today:
                disable = True

            row = ctk.CTkFrame(content, fg_color="#2a2a2a")
            row.pack(fill="x", padx=10, pady=3)

            prayer_label = ctk.CTkLabel(row, text=prayer, width=60, anchor="w")
            prayer_label.pack(side="left", padx=10)

            btn = ctk.CTkButton(
                row,
                textvariable=var,
                fg_color=STATUS_COLORS[var.get()],
                state="disabled" if disable else "normal",
                width=140,
                command=lambda v=var, b=None: show_dropdown(v, b)
            )
            def bind_btn(v=var, b=btn):
                b.configure(command=lambda: show_dropdown(v, b))
            bind_btn()

            btn.pack(side="right", padx=10)

    def show_dropdown(var, btn):
        dropdown = ctk.CTkFrame(frame, fg_color="#222", corner_radius=8)
        x = btn.winfo_rootx() - root_frame.winfo_rootx()
        y = btn.winfo_rooty() - root_frame.winfo_rooty() + 30
        dropdown.place(x=x, y=y)

        for option in STATUS_OPTIONS:
            def select(opt=option):
                var.set(opt)
                btn.configure(fg_color=STATUS_COLORS[opt])
                dropdown.destroy()

            opt_btn = ctk.CTkButton(dropdown, text=option, width=120, command=select)
            opt_btn.pack(pady=2, padx=5)

    # Save + Back Button
    button_row = ctk.CTkFrame(frame, fg_color="transparent")
    button_row.pack(pady=15)

    def save_and_back():
        updated = {k: var.get() for k, var in var_refs.items()}
        save_status_data(updated)
        frame.pack_forget()
        switch_to_dashboard()

    back_btn = ctk.CTkButton(button_row, text="Back to Dashboard", command=save_and_back)
    back_btn.pack()

    return frame
