import sqlite3 as sq

class MyDatabase:

    def __init__(self):
        self.conn = sq.connect('./datafiles/todo.db')
        self.cur = self.conn.cursor()
        self.cur.execute('create table if not exists tasks (title text PRIMARY KEY, task text NOT NULL, datenotification text)')
        print('cute')

    def update(self, title, task, date):
        print(title)
        print(task)
        print(date)
        self.cur.execute('insert into tasks values (?, ?, ?)', (title, task, date,))

    def delete(self, title):
        self.cur.execute('delete from tasks where title = ?', (title,))

    def readDB(self):
        alltasks = list()
        for row in self.cur.execute('select * from tasks'):
            alltasks.append(row[0])
        return alltasks
