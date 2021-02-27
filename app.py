import tkinter as tk
import tkinter.scrolledtext as tkst
from tkinter import messagebox
from tkcalendar import DateEntry
from datetime import datetime
import threading as th
from time import sleep
from database import MyDatabase

# appRunning = True
# allTask = list()

def compareDates(date, h, mn):
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    mydate = datetime.strptime(f'{date} {h}:{mn}', "%Y-%m-%d %H:%M")
    if mydate >= datetime.strptime(stamp, "%Y-%m-%d %H:%M"):
        return True
    return False

def createButton(master, bg, text, font, command, x, y, anchor):
    return tk.Button(master,
                     bg=bg,
                     text=text,
                     font=font,
                     command=command
                     ).place(x=x, y=y, anchor=anchor)

def createLabel(master, text, bg, font, anchor, x, y, placeAnchor):
    tk.Label(master,
             text=text,
             bg=bg,
             font=font,
             anchor=anchor
             ).place(x=x, y=y, anchor=placeAnchor)

class App(tk.Frame):

    def __init__(self):
        self.root = tk.Tk()
        tk.Frame.__init__(self, self.root)
        self.db = MyDatabase()
        self.allTask = list()
        self.appRunning = True
        self.thread = th.Thread(target=self.checkNotification, args=())
        self.thread.start()
        self.init_window()

    def init_window(self):
        self.root.title('TO-DO List')
        self.root.resizable(False, False)
        self.root.geometry('800x600')
        self.root.configure(background='#894bb3')

        self.frame = tk.Frame(self.root)
        self.frame.place(x=10, y=10)
        self.taskBox = tk.Listbox(self.frame, width=80, height=30, selectmode='SINGLE')
        self.taskBox.pack(side='left', fill='y')

        scrollbar = tk.Scrollbar(self.frame, orient='vertical')
        scrollbar.place(x=550, y=300, anchor='center')
        scrollbar.pack(side='right', fill='y')
        self.taskBox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.taskBox.yview)

        createButton(self.root, '#6fdaed', "Dodaj nowe zadanie", ("Helvetica", 12, 'bold'), self.new_window, 700, 50, 'center')

        createButton(self.root, '#6fdaed', "Zamknij okno", ("Helvetica", 12, 'bold'), self.destroyApp, 780, 580, 'e')

        self.updateTaskBox()

    def updateTaskBox(self):
        self.taskBox.delete(0, 'end')
        if not self.allTask:
            self.allTask = self.db.readDB()
        else:
            self.allTask += self.db.readDB()

        for task in self.allTask:
            self.taskBox.insert('end', task.__str__())

    def destroyApp(self):
        self.appRunning = False
        self.db.saveChanges()
        self.db.closeConnection()
        messagebox.showinfo('Zamykanie', 'Poczekaj na zapisanie zmian..\nProgram wyłączy się sam po zapisaniu wszystkich zmian.')
        self.thread.join()
        self.root.destroy()

    def new_window(self):
        self.newWindow = tk.Toplevel(self.root)
        self.newWindow.title('Dodaj zadanie')
        self.newWindow.geometry('300x400')
        self.newWindow.configure(background='#894bb3')
        self.newWindow.resizable(False, False)

        createLabel(self.newWindow, 'Nazwa zadania', '#894bb3', ("Helvetica", 12, 'bold'), tk.CENTER, 150, 15, 'center')
        self.title_entry = tk.Entry(self.newWindow)
        self.title_entry.place(x=150, y=45, anchor="center", width=100, height=30)

        createLabel(self.newWindow, 'Treść', '#894bb3', ("Helvetica", 12, 'bold'), tk.CENTER, 150, 81, 'center')
        self.task_entry = tk.Text(self.newWindow)
        self.task_entry.place(x=150, y=135, anchor="center", width=200, height=90)

        createLabel(self.newWindow, 'Przypomnienie', '#894bb3', ("Helvetica", 12, 'bold'), tk.CENTER, 150, 200, 'center')
        self.option = tk.StringVar(self.newWindow, 'TAK')

        tk.Radiobutton(self.newWindow, text="Tak", variable=self.option, value='TAK', bg='#894bb3').place(x=130, y=240, anchor='center')
        tk.Radiobutton(self.newWindow, text="Nie", variable=self.option, value='NIE', bg='#894bb3').place(x=170, y=240, anchor='center')

        self.timePicker(self.newWindow)

        self.date = DateEntry(self.newWindow, width=30, bg="black", fg="white", year=datetime.now().year)
        self.date.place(x=150, y=280, anchor="center")

        createButton(self.newWindow, '#6fdaed', 'Zatwierdź', ("Helvetica", 12, 'bold'), self.submitTask, 120, 380, 'e')
        createButton(self.newWindow, '#6fdaed', 'Anuluj', ("Helvetica", 12, 'bold'), self.newWindow.destroy, 280, 380, 'e')

    def timePicker(self, window):
        self.hourstr = tk.StringVar(window, str(datetime.now().hour))
        self.hour = tk.Spinbox(window, from_=0, to=23, wrap=True, textvariable=self.hourstr, width=2, state='readonly').place(x=120, y=320, anchor='center')

        self.minstr = tk.StringVar(window, str(datetime.now().minute))
        self.minstr.trace("w", self.checkTime)
        self.last_value = ""
        self.min = tk.Spinbox(window, from_=0, to=59, wrap=True, textvariable=self.minstr, width=2, state="readonly").place(x=150, y=320, anchor='center')

    def checkTime(self, *args):
        if self.last_value == "59" and self.minstr.get() == "0":
            self.hourstr.set(int(self.hourstr.get()) + 1 if self.hourstr.get() != "23" else 0)
        elif self.last_value == "0" and self.minstr.get() == "59":
            self.hourstr.set(int(self.hourstr.get()) - 1 if self.hourstr.get() != "0" else 23)
        self.last_value = self.minstr.get()

    def submitTask(self):
        title = self.title_entry.get()
        task = self.task_entry.get("1.0", tk.END).rstrip()
        notification = True if self.option.get() == 'TAK' else False
        date = str(self.date.get_date()).split('-')
        hour = self.hourstr.get() if int(self.hourstr.get()) >= 10 else "0" + self.hourstr.get()
        minute = self.minstr.get() if int(self.minstr.get()) >= 10 else "0" + self.minstr.get()

        if title and task:
            if self.db.checkTitle(title):
                messagebox.showerror('Nieprawidłowe dane', 'Istnieje już zadanie o takim tytule!')
            else:
                if notification and compareDates(self.date.get_date(), hour, minute):
                    self.db.update(title, task, f'{date[2]}/{date[1]}/{date[0]}/{hour}/{minute}')
                else:
                    self.db.update(title, task, '')
                self.updateTaskBox()
                self.newWindow.destroy()
        else:
            messagebox.showerror('Niepełne dane', 'Musisz podać tytuł i treść zadania.')

    def checkNotification(self):
        while self.appRunning:
            if self.allTask:
                for task in self.allTask:
                    task.compareDatetime()
            sleep(10)

app = App()
app.root.mainloop()
