import sqlite3 as sq
import threading
from task import Task

class MyDatabase:

    def __init__(self):
        self.lock = threading.Lock()
        self.__conn = sq.connect('./database/datafiles/todo.db', uri=True, check_same_thread=False)
        self.__conn.cursor().execute('CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY, title TEXT, task TEXT NOT NULL, readed INTEGER)')
        self.__conn.cursor().execute('CREATE TABLE IF NOT EXISTS notification (id INTEGER PRIMARY KEY, task_id INTEGER, date TEXT, occure_gap TEXT, repeat INTEGER)')
        self.__cur = None

    def get_cursor(self):
        return self.__cur

    def __enter__(self):
        self.lock.acquire()
        self.__cur = self.__conn.cursor()
        return self

    def __exit__(self, type, value, traceback):
        self.__conn.commit()
        if self.__cur is not None:
            self.__cur.close()
            self.__cur = None
        self.lock.release()

def update_readed_column():
    lsc = MyDatabase()
    with lsc:
        lsc.get_cursor().execute('UPDATE tasks SET readed = ? WHERE readed = ?', (0, 1,))

def addTask(title: str, task: str, date: str = '', occure_gap: str = '', repeat: int = 0):
    lsc = MyDatabase()
    with lsc:
        lsc.get_cursor().execute('INSERT INTO tasks (title, task, readed) VALUES (?, ?, ?)', (title, task, 0,))
        if date and occure_gap and repeat >= 0:
            result = lsc.get_cursor().execute('SELECT id FROM tasks WHERE title = ?', (title,))
            task_id = result.fetchone()[0]
            lsc.get_cursor().execute('INSERT INTO notification (task_id, date, occure_gap, repeat) VALUES (?, ?, ?, ?)', (task_id, date, occure_gap, repeat))

def deleteTask(title: str):
    lsc = MyDatabase()
    with lsc:
        lsc.get_cursor().execute('DELETE FROM notification WHERE task_id = (SELECT id FROM tasks WHERE title = ?)', (title,))
        lsc.get_cursor().execute('DELETE FROM tasks WHERE title = ?', (title,))

def update_notification(title, date, occure_gap, repeat):
    lsc = MyDatabase()
    with lsc:
        lsc.get_cursor().execute('UPDATE notification SET date = ?, occure_gap = ?, repeat = ? WHERE task_id = (SELECT id FROM tasks WHERE title = ?)', (date, occure_gap, repeat, title,))

def update_task(previous_title, title, task, date=None, occure_gap=None, repeat=None):
    lsc = MyDatabase()
    with lsc:
        result = lsc.get_cursor().execute('SELECT id FROM tasks WHERE title = ?', (previous_title,))
        task_id = result.fetchone()[0]
        lsc.get_cursor().execute('UPDATE tasks SET title = ?, task = ?, readed = ? WHERE id = ?', (title, task, 0, task_id,))
    if date:
        update_notification(title, date, occure_gap, repeat)


def checkTitle(title: str):
    lsc = MyDatabase()
    with lsc:
        result = lsc.get_cursor().execute('SELECT * FROM tasks WHERE title = ?', (title,))
        row = result.fetchall()
        if row:
            return True
        return False

def readDB() -> list:
    lsc = MyDatabase()
    with lsc:
        alltasks = list()
        result = lsc.get_cursor().execute('SELECT * FROM tasks WHERE readed = ?', (0,))
        rows = result.fetchall()
        for row in rows:
            task_id = row[0]
            title = row[1]
            task = row[2]
            notif_result = lsc.get_cursor().execute('SELECT * FROM notification WHERE task_id = ?', (task_id,))
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
        lsc.get_cursor().execute('UPDATE tasks SET readed = ? WHERE readed = ?', (1, 0,))
        return alltasks

# def saveChanges(self):
#     self.__conn.commit()

# def closeConnection(self):
#     self.__cur.close()
#     self.__conn.close()
