import tkinter as tk
import tkinter.scrolledtext as tkst
from tkinter import messagebox
from tkcalendar import DateEntry
from datetime import datetime
import threading as th
from time import sleep
# ---------------------------- #
from database import MyDatabase
from functions import create_button, create_entry, create_label, create_new_window_object, create_radiobutton, compare_dates

class App(tk.Frame):

    def __init__(self):
        self.__root = tk.Tk()
        tk.Frame.__init__(self, self.__root)
        self.__db = MyDatabase()
        self.__allTask = list()
        self.__appRunning = True
        self.__root.overrideredirect(True)
        # self.__root.attributes('-topmost', True)
        # self.__root.attributes('-topmost', False)
        self.__helveticaTwelve = ('Helvetica', 12, 'bold')
        self.__helveticaTwenty = ('Helvetica', 20, 'bold')
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

        create_label(self.__root, 'Zadania', self.__helveticaTwenty, tk.S, 10, 18, 'w')
        scrollbar = tk.Scrollbar(self.__frame, orient='vertical')
        scrollbar.place(x=550, y=300, anchor='center')
        scrollbar.pack(side='right', fill='y')
        self.__titleBox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.__titleBox.yview)

        self.__taskBoxTitle = create_label(self.__root, '', self.__helveticaTwenty, tk.CENTER, 260, 1, 'nw')
        self.__taskBox = create_label(self.__root, '', self.__helveticaTwelve, tk.CENTER, 260, 63, 'nw', 300)
        self.__titleBox.bind("<<ListboxSelect>>", self.callback)

        self.__notificationTitle = create_label(self.__root, '', self.__helveticaTwenty, tk.CENTER, 260, 500, 'nw')
        self.__notificationBox = create_label(self.__root, '', self.__helveticaTwenty, tk.CENTER, 260, 550, 'nw')

        create_button(self.__root, '#6fdaed', "Dodaj nowe zadanie", self.__helveticaTwelve, self.new_window, 590, 50, 'nw', 3)
        create_button(self.__root, '#6fdaed', "Usuń wybrane zadanie", self.__helveticaTwelve, self.delete_task, 590, 100, 'nw', 3)
        create_button(self.__root, '#6fdaed', 'Edytuj wybrane zadanie', self.__helveticaTwelve, self.edit_task, 590, 150, 'nw', 3)
        create_button(self.__root, '#6fdaed', "Zamknij okno", self.__helveticaTwelve, self.on_closing, 590, 560, 'nw', 3)

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

    def edit_task(self):
        self.__editWindow = tk.Toplevel(self.__root)
        self.__editWindow.title('Edytuj zadanie')
        self.__editWindow.geometry(f'{300}x{400}+{int(self.__editWindow.winfo_screenwidth() / 3)}+{int(self.__editWindow.winfo_screenheight() / 3)}')
        self.__editWindow.resizable(False, False)
        # create_button(self.__editWindow, '#6fdaed', 'Edytuj tytuł', self.__helveticaTwelve, print(':)'), 20, 10, 'nw', 3)
        # create_button(self.__editWindow, '#6fdaed', 'Edytuj treść', self.__helveticaTwelve, print(':)'), 20, 50, 'nw', 3)
        # create_button(self.__editWindow, '#6fdaed', 'Edytuj powiadomienie', self.__helveticaTwelve, print(':)'), 20, 90, 'nw', 3)

    def destroy_app(self):
        self.__appRunning = False
        messagebox.showinfo('Zamykanie', 'Poczekaj na zapisanie zmian..\nProgram wyłączy się sam po zapisaniu wszystkich zmian.')
        self.__thread.join()
        self.__db.saveChanges()
        self.__db.closeConnection()
        self.__root.destroy()

    def new_window(self, edit=None):
        self.__newWindow = create_new_window_object('Dodaj zadanie', f'{300}x{400}', False)
        self.__notifWindow = create_new_window_object('Ustaw przypomnienie', f'{300}x{400}', False)

        self.__notifWindow.iconify()

        create_label(self.__newWindow, 'Nazwa zadania', self.__helveticaTwelve, tk.CENTER, 150, 15, 'center')
        self.__title_entry = create_entry(self.__newWindow, 150, 45, 'center', 100, 30)

        create_label(self.__newWindow, 'Treść', self.__helveticaTwelve, tk.CENTER, 150, 81, 'center')
        self.__task_entry = create_entry(self.__newWindow, 150, 135, 'center', 200, 90)

        create_label(self.__newWindow, 'Przypomnienie', self.__helveticaTwelve, tk.CENTER, 150, 200, 'center')
        self.__option = tk.StringVar(self.__newWindow, 'TAK')

        create_radiobutton(self.__newWindow, "Tak", self.__option, 'TAK', 130, 240, 'center')
        create_radiobutton(self.__newWindow, "Nie", self.__option, 'NIE', 170, 240, 'center')

        create_button(self.__newWindow, '#6fdaed', 'Ustaw przypomnienie', self.__helveticaTwelve, self.__notifWindow.deiconify, 150, 300, 'center', 3)

        create_button(self.__newWindow, '#6fdaed', 'Zatwierdź', self.__helveticaTwelve, self.submit_task, 120, 380, 'e', 3)
        create_button(self.__newWindow, '#6fdaed', 'Anuluj', self.__helveticaTwelve, self.destroy_task_windows, 280, 380, 'e', 3)
        self.notification_window()

    def notification_window(self):
        if self.__option.get() == 'TAK':
            self.__date = DateEntry(self.__notifWindow, width=30, bg="black", fg="white", year=datetime.now().year)
            self.__date.place(x=150, y=40, anchor="center")
            self.time_picker(self.__notifWindow)
            self.__notification_gap = tk.StringVar(self.__notifWindow, 'ONCE')

            create_radiobutton(self.__notifWindow, "Jeden raz", self.__notification_gap, 'ONCE', 50, 200, 'center')
            create_radiobutton(self.__notifWindow, "Co tydzień", self.__notification_gap, 'WEEK', 150, 200, 'center')
            create_radiobutton(self.__notifWindow, "Co miesiąc", self.__notification_gap, 'MONTH', 250, 200, 'center')
            create_radiobutton(self.__notifWindow, "Co rok", self.__notification_gap, 'YEAR', 100, 230, 'center')
            create_radiobutton(self.__notifWindow, "Co ile dni", self.__notification_gap, 'CUSTOM', 200, 230, 'center')
            self.__repeatNotif = create_entry(self.__notifWindow, 270, 230, 'center', 20, 20)
            create_label(self.__notifWindow, 'Ilość powtórzeń (0, jeśli w nieskończoność):', ('Helvetica', 8), tk.NW, 20, 250, 'nw')
            self.__howManyRepeats = create_entry(self.__notifWindow, 270, 260, 'center', 30, 20)

            create_button(self.__notifWindow, '#6fdaed', 'Zatwierdź', self.__helveticaTwelve, self.submit_task, 120, 380, 'e', 3)
            create_button(self.__notifWindow, '#6fdaed', 'Anuluj', self.__helveticaTwelve, self.__notifWindow.iconify, 280, 380, 'e', 3)
        else:
            messagebox.showinfo('Ostrzeżenie', 'Aby ustawić przypomnienie zaznacz opcje \"TAK\" w opcji \"Przypomnienie\"')

    def destroy_task_windows(self):
        self.__notifWindow.destroy()
        self.__newWindow.destroy()
        self.__root.lift()
        self.__root.attributes('-topmost', True)
        self.__root.attributes('-topmost', False)

    def time_picker(self, window):
        self.__hourstr = tk.StringVar(window, str(datetime.now().hour))
        self.__hour = tk.Spinbox(window, from_=0, to=23, wrap=True, textvariable=self.__hourstr, width=2, state='readonly').place(x=130, y=100, anchor='center')

        self.__minstr = tk.StringVar(window, str(datetime.now().minute))
        self.__minstr.trace("w", self.check_time)
        self.__last_value = ""
        self.__min = tk.Spinbox(window, from_=0, to=59, wrap=True, textvariable=self.__minstr, width=2, state="readonly").place(x=170, y=100, anchor='center')

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
