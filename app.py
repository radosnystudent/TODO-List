import tkinter as tk
import tkinter.scrolledtext as tkst
from tkinter import messagebox
from tkcalendar import DateEntry
from datetime import datetime
from task import Task, readCSV
import _thread as th
from time import sleep
from database import MyDatabase

appRunning = True

class App(tk.Frame):

    def __init__(self):
        self.root = tk.Tk()
        tk.Frame.__init__(self, self.root)
        self.allTask = list()

        self.db = MyDatabase()
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

        self.createButton(self.root, '#6fdaed', "Dodaj nowe zadanie", ("Helvetica", 12, 'bold'), self.new_window, 700, 50, 'center')

        self.createButton(self.root, '#6fdaed', "Zamknij okno", ("Helvetica", 12, 'bold'), self.destroyApp, 780, 580, 'e')

        self.updateTaskBox()

    def updateTaskBox(self):
        if not self.allTask:
            self.allTask = readCSV()
        else:
            readTask = readCSV()
            for task in readTask:
                if task not in self.allTask:
                    self.allTask.append(task)

        for task in self.allTask:
            self.taskBox.insert('end', task.__str__())

        print(self.db.readDB())

    def destroyApp(self):
        global appRunning
        appRunning = False
        self.root.destroy()

    def createButton(self, master, bg, text, font, command, x, y, anchor):
        return tk.Button(master,
                         bg=bg,
                         text=text,
                         font=font,
                         command=command).place(x=x, y=y, anchor=anchor)

    def createLabel(self, master, text, bg, font, anchor, x, y, placeAnchor):
        tk.Label(master,
                 text=text,
                 bg=bg,
                 font=font,
                 anchor=anchor
                 ).place(x=x, y=y, anchor=placeAnchor)

    def new_window(self):
        self.newWindow = tk.Toplevel(self.root)
        self.newWindow.title('Dodaj zadanie')
        self.newWindow.geometry('300x400')
        self.newWindow.configure(background='#894bb3')
        self.newWindow.resizable(False, False)

        self.createLabel(self.newWindow, 'Nazwa zadania', '#894bb3', ("Helvetica", 12, 'bold'), tk.CENTER, 150, 15, 'center')
        self.title_entry = tk.Entry(self.newWindow)
        self.title_entry.place(x=150, y=45, anchor="center", width=100, height=30)

        self.createLabel(self.newWindow, 'Treść', '#894bb3', ("Helvetica", 12, 'bold'), tk.CENTER, 150, 81, 'center')
        self.task_entry = tk.Text(self.newWindow)
        self.task_entry.place(x=150, y=135, anchor="center", width=200, height=90)

        self.createLabel(self.newWindow, 'Przypomnienie', '#894bb3', ("Helvetica", 12, 'bold'), tk.CENTER, 150, 200, 'center')
        self.option = tk.StringVar(self.newWindow, 'TAK')

        tk.Radiobutton(self.newWindow, text="Tak", variable=self.option, value='TAK', bg='#894bb3').place(x=130, y=240, anchor='center')
        tk.Radiobutton(self.newWindow, text="Nie", variable=self.option, value='NIE', bg='#894bb3').place(x=170, y=240, anchor='center')

        self.timePicker(self.newWindow)

        self.date = DateEntry(self.newWindow, width=30, bg="black", fg="white", year=datetime.now().year)
        self.date.place(x=150, y=280, anchor="center")

        self.createButton(self.newWindow, '#6fdaed', 'Zatwierdź', ("Helvetica", 12, 'bold'), self.submitTask, 120, 380, 'e')
        self.createButton(self.newWindow, '#6fdaed', 'Anuluj', ("Helvetica", 12, 'bold'), self.newWindow.destroy, 280, 380, 'e')

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
        if notification:
            datetime = {'year': date[0],
                        'month': date[1],
                        'day': date[2],
                        'hour': self.hourstr.get(),
                        'minute': self.minstr.get()}
        else:
            datetime = None

        if title and task:
            newTask = Task(title, task, notification, datetime)
            newTask.writeToCsv()
            readCSV()
            self.updateTaskBox()
            if notification:
                self.db.update(title, task, f'{date[2]}/{date[1]}/{date[0]} {self.hourstr.get()}:{self.minstr.get()}')
            else:
                self.db.update(title, task, '')
            self.newWindow.destroy()
        else:
            messagebox.showerror('Niepełne dane', 'Musisz podać tytuł i treść zadania.')

app = App()

def checkNotification():
    global appRunning
    allTasks = list()
    while appRunning:
        readedTasks = readCSV()
        if readedTasks:
            for task in readedTasks:
                if task not in allTasks:
                    allTasks.append(task)

        if allTasks:
            for task in allTasks:
                task.compareDatetime()
        sleep(20)

th.start_new_thread(checkNotification, ())

app.root.mainloop()
