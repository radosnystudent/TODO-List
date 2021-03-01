import sqlite3 as sq
from task import Task

class MyDatabase:

    def __init__(self):
        self.__conn = sq.connect('./database/datafiles/todo.db')
        self.__cur = self.__conn.cursor()
        self.__cur.execute('CREATE TABLE IF NOT EXISTS tasks (title TEXT PRIMARY KEY, task TEXT NOT NULL, datenotification TEXT, readed INT)')
        self.__cur.execute('UPDATE tasks SET readed = ? WHERE readed = ?', (0, 1,))

    def update(self, title, task, date):
        self.__cur.execute('INSERT INTO tasks VALUES (?, ?, ?, ?)', (title, task, date, 0,))

    def delete(self, title):
        self.__cur.execute('DELETE FROM tasks WHERE title = ?', (title,))

    def checkTitle(self, title):
        result = self.__cur.execute('SELECT * FROM tasks WHERE title = ?', (title,))
        row = result.fetchall()
        if row:
            return True
        return False

    def readDB(self):
        alltasks = list()
        result = self.__cur.execute('SELECT * FROM tasks WHERE readed = ?', (0,))
        rows = result.fetchall()
        for row in rows:
            title = row[0]
            task = row[1]
            if row[2]:
                datestring = row[2].split('/')
                datetime = {
                    'year': datestring[2],
                    'month': datestring[1],
                    'day': datestring[0],
                    'hour': datestring[3],
                    'minute': datestring[4]
                }
                alltasks.append(Task(title, task, True, datetime))
            else:
                alltasks.append(Task(title, task))

        self.__cur.execute('UPDATE tasks SET readed = ? WHERE readed = ?', (1, 0,))
        return alltasks

    def saveChanges(self):
        self.__conn.commit()

    def closeConnection(self):
        self.__cur.close()
        self.__conn.close()
