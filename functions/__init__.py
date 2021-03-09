import tkinter as tk
from datetime import datetime

def compare_dates(date: str, h: str, mn: str) -> bool:
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    mydate = datetime.strptime(f'{date} {h}:{mn}', "%Y-%m-%d %H:%M")
    return True if mydate >= datetime.strptime(stamp, "%Y-%m-%d %H:%M") else False

def create_entry(master, x: int, y: int, anchor: str, width: int, height: int):
    entry = tk.Text(master)
    entry.place(x=x, y=y, anchor=anchor, width=width, height=height)
    return entry

def create_new_window_object(title: str, geometry: str, resizable: bool):
    newWindow = tk.Toplevel()
    newWindow.title(title)
    newWindow.geometry(geometry + f'+{int(newWindow.winfo_screenwidth() / 3)}+{int(newWindow.winfo_screenheight() / 3)}')
    if resizable:
        newWindow.resizable(True, True)
    else:
        newWindow.resizable(False, False)
    return newWindow

def create_button(master, bg: str, text: str, font: str, command: callable, x: int, y: int, anchor: str, borderwidth: int, relief=tk.RAISED, activebackground='#5F9EA0'):
    button = tk.Button(
        master,
        activebackground=activebackground,
        bg=bg,
        text=text,
        font=font,
        borderwidth=borderwidth,
        relief=relief,
        command=command
    )
    button.place(x=x, y=y, anchor=anchor)
    return button

def create_radiobutton(master, text, variable, value, x, y, anchor):
    radiobutton = tk.Radiobutton(master, text=text, variable=variable, value=value)
    radiobutton.place(x=x, y=y, anchor=anchor)
    return radiobutton

def create_label(master, text: str, font: str, anchor, x: int, y: int, placeAnchor: str, wraplength=0):
    label = tk.Label(
        master,
        text=text,
        font=font,
        anchor=anchor,
        wraplength=wraplength
    )
    label.place(x=x, y=y, anchor=placeAnchor)
    return label
