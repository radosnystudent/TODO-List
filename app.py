import tkinter as tk
import tkinter.scrolledtext as tkst
from tkinter import messagebox
from tkcalendar import DateEntry
from datetime import datetime
import threading as th
from time import sleep
from database import MyDatabase

def compare_dates(date: str, h: str, mn: str) -> bool:
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    mydate = datetime.strptime(f'{date} {h}:{mn}', "%Y-%m-%d %H:%M")
    return True if mydate >= datetime.strptime(stamp, "%Y-%m-%d %H:%M") else False

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

def do_nothing():
    pass

class App(tk.Frame):

    def __init__(self):
        self.__root = tk.Tk()
        tk.Frame.__init__(self, self.__root)
        self.__db = MyDatabase()
        self.__allTask = list()
        self.__appRunning = True
        self.__root.overrideredirect(True)

        self.__root.protocol = ("WM_DELETE_WINDOW", do_nothing)
        self.__trayMenu = None
        self.__thread = th.Thread(target=self.check_notification, args=())
        self.__thread.start()
        self.init_window()

    def on_closing(self):
        select = messagebox.askyesnocancel("Ostrzeżenie", "Wyłączenie aplikacji spowoduje, że nie będzie ona wyświetlała powiadomień."
                                           "\nCzy na pewno chcesz ją zamknąć?\nTak - zamknij aplikację.\nNie - zminimalizuj do zasobnika systemu.")
        if select:
            self.destroy_app()
        elif select is False:
            self.__root.withdraw()

            if not self.__trayMenu:
                self.tk.call('package', 'require', 'Winico')  # use the tcl "winico", make sure the folder of "winico" is in the same path.
                icon = self.tk.call('winico', 'createfrom', './notification/icons/preferences__icon.ico')  # this is the icon on the system tray.
                self.tk.call(
                    'winico', 'taskbar', 'add', icon,  # set the icon
                    '-callback', (self.register(self.menu_func), '%m', '%x', '%y'),  # refer to winico documentation.
                    '-pos', 0,
                    '-text', u'Lista zadań'
                )

                self.__trayMenu = tk.Menu(self.__root, tearoff=False)
                self.__trayMenu.add_command(label="Przywróć aplikację", command=self.restore_app)
                self.__trayMenu.add_command(label="Zamknij aplikację", command=self.destroy_app)
        else:
            pass

    def restore_app(self):
        self.__root.deiconify()

    def menu_func(self, event, x, y):
        if event == 'WM_RBUTTONDOWN':  # Mouse event, Right click on the tray.Mostly we will show it.
            self.__trayMenu.tk_popup(x, y)  # pop it up on this postion
        if event == 'WM_LBUTTONDOWN':  # Mouse event, Left click on the tray,Mostly we will show the menu.
            self.restore_app()

    def get_root(self):
        return self.__root

    def init_window(self):
        self.__root.title('TO-DO List')
        self.__root.resizable(False, False)
        self.__root.geometry(f'{800}x{600}+{int(self.__root.winfo_screenwidth() / 4)}+{int(self.__root.winfo_screenheight() / 4)}')

        self.__frame = tk.Frame(self.__root)
        self.__frame.place(x=10, y=40)
        self.__titleBox = tk.Listbox(self.__frame, width=18, height=20, font=('Helvetica', 16, 'bold'), selectmode='SINGLE')
        self.__titleBox.pack(side='left', fill='y')

        create_label(self.__root, 'Zadania', ('Helvetica', 20, 'bold'), tk.S, 10, 18, 'w')
        scrollbar = tk.Scrollbar(self.__frame, orient='vertical')
        scrollbar.place(x=550, y=300, anchor='center')
        scrollbar.pack(side='right', fill='y')
        self.__titleBox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.__titleBox.yview)

        self.__taskBoxTitle = create_label(self.__root, '', ('Helvetica', 20, 'bold'), tk.CENTER, 260, 1, 'nw')
        self.__taskBox = create_label(self.__root, '', ('Helvetica', 12, 'bold'), tk.CENTER, 260, 63, 'nw', 300)
        self.__titleBox.bind("<<ListboxSelect>>", self.callback)

        self.__notificationTitle = create_label(self.__root, '', ('Helvetica', 20, 'bold'), tk.CENTER, 260, 500, 'nw')
        self.__notificationBox = create_label(self.__root, '', ('Helvetica', 20, 'bold'), tk.CENTER, 260, 550, 'nw')

        create_button(self.__root, '#6fdaed', "Dodaj nowe zadanie", ("Helvetica", 12, 'bold'), self.new_window, 600, 50, 'nw', 3)
        create_button(self.__root, '#6fdaed', "Usuń wybrane zadanie", ("Helvetica", 12, 'bold'), self.delete_task, 600, 100, 'nw', 3)

        create_button(self.__root, '#6fdaed', "Zamknij okno", ("Helvetica", 12, 'bold'), self.on_closing, 600, 560, 'nw', 3)

        self.update_task_box()

    def callback(self, event):
        selection = event.widget.curselection()
        if selection:
            index = selection[0]
            data = event.widget.get(index)
            data = data[data.index(')') + 1:].lstrip()
            for task in self.__allTask:
                if task.getTitle() == data:
                    self.__taskBoxTitle.configure(text='Treść zadania')
                    self.__taskBox.configure(text=task.getTask(), borderwidth=2, relief='sunken')
                    if task.checkTaskNotification():
                        self.__notificationTitle.configure(text='Powiadomienie:')
                        self.__notificationBox.configure(text=task.getNotificationDate(), borderwidth=2, relief='sunken')
        else:
            self.__taskBoxTitle.configure(text='')
            self.__taskBox.configure(text='', borderwidth=0, relief='flat')
            self.__notificationTitle.configure(text='')
            self.__notificationBox.configure(text='', borderwidth=0, relief='flat')

    def delete_task(self):
        try:
            if messagebox.askyesno('Usunięcie zadania.', 'Czy na pewno chcesz usunąć to zadanie?'):
                value = self.__titleBox.get(self.__titleBox.curselection())
                value = value[value.index(')') + 1:].lstrip()
                index = None
                for task in self.__allTask:
                    if task.getTitle() == value:
                        index = self.__allTask.index(task)
                self.__allTask.remove(self.__allTask[index])
                self.__db.delete(value)
                self.update_task_box()
        except Exception as ex:
            messagebox.showerror('Błąd. Nieprawidłowe dane.', 'Nie wybrałeś żadnego zadania do usunięcia!')

    def update_task_box(self):
        self.__titleBox.delete(0, 'end')
        if not self.__allTask:
            self.__allTask = self.__db.readDB()
        else:
            self.__allTask += self.__db.readDB()

        for task in self.__allTask:
            getDate = task.getDate()
            self.__titleBox.insert('end', str(self.__allTask.index(task) + 1) + ') ' + task.getTitle())
            if getDate is None or compare_dates(getDate[0], getDate[1], getDate[2]) is False:
                self.__titleBox.itemconfig(self.__allTask.index(task), foreground='red')

    def destroy_app(self):
        self.__appRunning = False
        messagebox.showinfo('Zamykanie', 'Poczekaj na zapisanie zmian..\nProgram wyłączy się sam po zapisaniu wszystkich zmian.')
        self.__thread.join()
        self.__db.saveChanges()
        self.__db.closeConnection()
        self.__root.destroy()

    def new_window(self):
        self.__newWindow = tk.Toplevel(self.__root)
        self.__newWindow.title('Dodaj zadanie')
        self.__newWindow.geometry(f'{300}x{400}+{int(self.__newWindow.winfo_screenwidth() / 3)}+{int(self.__newWindow.winfo_screenheight() / 3)}')
        self.__newWindow.resizable(False, False)

        create_label(self.__newWindow, 'Nazwa zadania', ("Helvetica", 12, 'bold'), tk.CENTER, 150, 15, 'center')
        self.__title_entry = tk.Entry(self.__newWindow)
        self.__title_entry.place(x=150, y=45, anchor="center", width=100, height=30)

        create_label(self.__newWindow, 'Treść', ("Helvetica", 12, 'bold'), tk.CENTER, 150, 81, 'center')
        self.__task_entry = tk.Text(self.__newWindow)
        self.__task_entry.place(x=150, y=135, anchor="center", width=200, height=90)

        create_label(self.__newWindow, 'Przypomnienie', ("Helvetica", 12, 'bold'), tk.CENTER, 150, 200, 'center')
        self.__option = tk.StringVar(self.__newWindow, 'TAK')

        tk.Radiobutton(self.__newWindow, text="Tak", variable=self.__option, value='TAK').place(x=130, y=240, anchor='center')
        tk.Radiobutton(self.__newWindow, text="Nie", variable=self.__option, value='NIE').place(x=170, y=240, anchor='center')

        self.time_picker(self.__newWindow)

        self.__date = DateEntry(self.__newWindow, width=30, bg="black", fg="white", year=datetime.now().year)
        self.__date.place(x=150, y=280, anchor="center")

        create_button(self.__newWindow, '#6fdaed', 'Zatwierdź', ("Helvetica", 12, 'bold'), self.submit_task, 120, 380, 'e', 3)
        create_button(self.__newWindow, '#6fdaed', 'Anuluj', ("Helvetica", 12, 'bold'), self.__newWindow.destroy, 280, 380, 'e', 3)

    def time_picker(self, window):
        self.__hourstr = tk.StringVar(window, str(datetime.now().hour))
        self.__hour = tk.Spinbox(window, from_=0, to=23, wrap=True, textvariable=self.__hourstr, width=2, state='readonly').place(x=130, y=320, anchor='center')

        self.__minstr = tk.StringVar(window, str(datetime.now().minute))
        self.__minstr.trace("w", self.check_time)
        self.__last_value = ""
        self.__min = tk.Spinbox(window, from_=0, to=59, wrap=True, textvariable=self.__minstr, width=2, state="readonly").place(x=170, y=320, anchor='center')

    def check_time(self, *args):
        if self.__last_value == "59" and self.__minstr.get() == "0":
            self.__hourstr.set(int(self.__hourstr.get()) + 1 if self.__hourstr.get() != "23" else 0)
        elif self.__last_value == "0" and self.__minstr.get() == "59":
            self.__hourstr.set(int(self.__hourstr.get()) - 1 if self.__hourstr.get() != "0" else 23)
        self.__last_value = self.__minstr.get()

    def submit_task(self):
        title = self.__title_entry.get()
        task = self.__task_entry.get("1.0", tk.END).rstrip()
        notification = True if self.__option.get() == 'TAK' else False
        date = str(self.__date.get_date()).split('-')
        hour = self.__hourstr.get() if int(self.__hourstr.get()) >= 10 else "0" + self.__hourstr.get()
        minute = self.__minstr.get() if int(self.__minstr.get()) >= 10 else "0" + self.__minstr.get()

        if title and task:
            if title[0].isalpha() or title[0].isdigit():
                if self.__db.checkTitle(title):
                    messagebox.showerror('Nieprawidłowe dane', 'Istnieje już zadanie o takim tytule!')
                else:
                    if notification and compare_dates(self.__date.get_date(), hour, minute):
                        self.__db.update(title, task, f'{date[2]}/{date[1]}/{date[0]}/{hour}/{minute}')
                    else:
                        self.__db.update(title, task, '')
                    self.update_task_box()
                    self.__newWindow.destroy()
            else:
                messagebox.showerror('Nieprawidłowe dane', 'Tytuł zadania musi zaczynać się cyfrą lub literą')
        else:
            messagebox.showerror('Niepełne dane', 'Musisz podać tytuł i treść zadania.')

    def check_notification(self):
        while self.__appRunning:
            if self.__allTask:
                for task in self.__allTask:
                    task.compareDatetime()
            sleep(5)

app = App()
app.get_root().mainloop()
