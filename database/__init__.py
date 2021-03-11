import sqlite3 as sq
from task import Task

class MyDatabase:

    def __init__(self):
        self.__conn = sq.connect('./database/datafiles/todo.db')
        self.__cur = self.__conn.cursor()
        self.__cur.execute('CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY, title TEXT, task TEXT NOT NULL, readed INTEGER)')
        self.__cur.execute('CREATE TABLE IF NOT EXISTS notification (id INTEGER PRIMARY KEY, task_id INTEGER, date TEXT, occure_gap TEXT, repeat INTEGER)')
        self.__cur.execute('UPDATE tasks SET readed = ? WHERE readed = ?', (0, 1,))

    def addTask(self, title: str, task: str, date: str = '', occure_gap: str = '', repeat: int = 0):
        self.__cur.execute('INSERT INTO tasks (title, task, readed) VALUES (?, ?, ?)', (title, task, 0,))
        if date and occure_gap and repeat >= 0:
            result = self.__cur.execute('SELECT id FROM tasks WHERE title = ?', (title,))
            task_id = result.fetchone()[0]
            self.__cur.execute('INSERT INTO notification (task_id, date, occure_gap, repeat) VALUES (?, ?, ?, ?)', (task_id, date, occure_gap, repeat))

    def delete(self, title: str):
        self.__cur.execute('DELETE FROM notification WHERE task_id = (SELECT id FROM tasks WHERE title = ?)', (title,))
        self.__cur.execute('DELETE FROM tasks WHERE title = ?', (title,))

    def update_notification(self, title, date, occure_gap, repeat):
        self.__cur.execute('UPDATE notification SET date = ?, occure_gap = ?, repeat = ? WHERE task_id = (SELECT id FROM tasks WHERE title = ?)', (date, occure_gap, repeat, title,))

    def checkTitle(self, title: str):
        result = self.__cur.execute('SELECT * FROM tasks WHERE title = ?', (title,))
        row = result.fetchall()
        if row:
            return True
        return False

    def readDB(self) -> list:
        alltasks = list()
        result = self.__cur.execute('SELECT * FROM tasks WHERE readed = ?', (0,))
        rows = result.fetchall()
        for row in rows:
            task_id = row[0]
            title = row[1]
            task = row[2]
            notif_result = self.__cur.execute('SELECT * FROM notification WHERE task_id = ?', (task_id,))
            notification_row = notif_result.fetchone()
            if notification_row:
                datestring = notification_row[2].split('/')
                datetime = {
                    'year': datestring[2],
                    'month': datestring[1],
                    'day': datestring[0],
                    'hour': datestring[3],
                    'minute': datestring[4]
                }
                occure_gap = notification_row[3]
                repeat = notification_row[4]
                alltasks.append(Task(title, task, True, datetime, occure_gap, repeat))
            else:
                alltasks.append(Task(title, task))
        self.__cur.execute('UPDATE tasks SET readed = ? WHERE readed = ?', (1, 0,))
        return alltasks

    def saveChanges(self):
        self.__conn.commit()

    def closeConnection(self):
        self.__cur.close()
        self.__conn.close()
