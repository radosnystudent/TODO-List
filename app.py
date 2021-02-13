import tkinter as tk
import tkinter.scrolledtext as tkst
from tkcalendar import DateEntry
from datetime import datetime
from task import Task, readCSV

class App(tk.Frame):

    def __init__(self):
        self.root = tk.Tk()
        tk.Frame.__init__(self, self.root)

        self.init_window()

    def init_window(self):
        self.root.title('TO-DO List')
        self.root.resizable(False, False)
        self.root.geometry('800x600')
        self.root.configure(background='#894bb3')

        addTaskButton = tk.Button(self.root,
                                  bg='#6fdaed',
                                  text="Dodaj nowe zadanie",
                                  font=("Helvetica", 12, 'bold'),
                                  command=self.new_window
                                  ).place(x=700, y=50, anchor='center')
        closeBtn = tk.Button(self.root,
                             bg='#6fdaed',
                             text='Zamknij okno',
                             font=("Helvetica", 12, 'bold'),
                             command=self.root.destroy).place(x=780, y=580, anchor='e')

    def new_window(self):
        self.newWindow = tk.Toplevel(self.root)
        self.newWindow.title('Dodaj zadanie')
        self.newWindow.geometry('300x400')
        self.newWindow.configure(background='#894bb3')
        self.newWindow.resizable(False, False)

        tk.Label(self.newWindow,
                 text='Nazwa zadania',
                 bg='#894bb3',
                 font=("Helvetica", 12, 'bold'),
                 anchor=tk.CENTER).place(x=150, y=15, anchor='center')
        self.title_entry = tk.Entry(self.newWindow)
        self.title_entry.place(x=150, y=45, anchor="center", width=100, height=30)

        tk.Label(self.newWindow,
                 text='Treść',
                 bg='#894bb3',
                 font=("Helvetica", 12, 'bold'),
                 anchor=tk.CENTER).place(x=150, y=81, anchor='center')
        self.task_entry = tk.Text(self.newWindow)
        self.task_entry.place(x=150, y=135, anchor="center", width=200, height=90)

        tk.Label(self.newWindow,
                 text='Przypomnienie',
                 bg='#894bb3',
                 font=("Helvetica", 12, 'bold'),
                 anchor=tk.CENTER).place(x=150, y=200, anchor='center')

        self.option = tk.StringVar(self.newWindow, 'TAK')

        tk.Radiobutton(self.newWindow, text="Tak", variable=self.option, value='TAK', bg='#894bb3').place(x=130, y=240, anchor='center')
        tk.Radiobutton(self.newWindow, text="Nie", variable=self.option, value='NIE', bg='#894bb3').place(x=170, y=240, anchor='center')

        self.timePicker(self.newWindow)

        self.date = DateEntry(self.newWindow, width=30, bg="black", fg="white", year=datetime.now().year)
        self.date.place(x=150, y=280, anchor="center")

        acceptBtn = tk.Button(self.newWindow,
                              text='Zatwierdź',
                              bg='#6fdaed',
                              font=("Helvetica", 12, 'bold'),
                              command=self.submitTask).place(x=120, y=380, anchor='e')

        closeBtn = tk.Button(self.newWindow,
                             text='Anuluj',
                             bg='#6fdaed',
                             font=("Helvetica", 12, 'bold'),
                             command=self.newWindow.destroy).place(x=280, y=380, anchor='e')

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
        newTask = Task(title, task, notification, datetime)
        newTask.writeToCsv()
        readCSV()
        self.newWindow.destroy()

app = App()
app.root.mainloop()
