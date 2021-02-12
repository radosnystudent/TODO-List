import tkinter as tk
import tkinter.scrolledtext as tkst


class App(tk.Frame):

    def __init__(self):
        self.root = tk.Tk()
        self.root.geometry('800x600')

        tk.Frame.__init__(self, self.root)

        self.init_window()

    def init_window(self):
        self.root.title('TO-DO List')

        addTaskButton = tk.Button(self.root,
                                  text="Dodaj nowe zadanie",
                                  font=("Helvetica", 12, 'bold'),
                                  command=self.new_window
                                  ).place(x=720, y=50, anchor='center')
        closeBtn = tk.Button(self.root,
                             text='Zamknij okno',
                             font=("Helvetica", 12, 'bold'),
                             command=self.root.destroy).place(x=780, y=580, anchor='e')

    def new_window(self):
        newWindow = tk.Toplevel(self.root)
        newWindow.title('Dodaj zadanie')
        newWindow.geometry('200x400')
        tk.Label(newWindow,
                 text='Nazwa zadania',
                 font=("Helvetica", 12, 'bold'),
                 anchor=tk.CENTER).place(x=100, y=15, anchor='center')

        title_entry = tk.Entry(newWindow)
        title_entry.place(x=100, y=45, anchor="center", width=100, height=30)

        closeBtn = tk.Button(newWindow,
                             text='Zamknij okno',
                             command=newWindow.destroy).place(x=180, y=380, anchor='e')

app = App()
app.root.mainloop()
