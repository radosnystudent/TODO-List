from datetime import datetime
from notification import setNotification


class Task:

    def __init__(self, title, task, notification=False, datetime=None) -> None:
        self.title = title
        self.task = task
        self.notification = notification
        self.datetime = datetime

    def __str__(self) -> str:
        return f'{self.title}: {self.task} Przypomnienie: {self.datetime["day"]}/{self.datetime["month"]}/{self.datetime["year"]} {self.datetime["hour"]}:' \
            f'{self.datetime["minute"]}' if self.notification else f'{self.title}: {self.task}'

    def compareDatetime(self):
        if self.notification:
            stamp = datetime.now()
            if self.datetime['year'] == str(stamp.strftime('%Y')) and self.datetime['month'] == str(stamp.strftime('%m')) and self.datetime['day'] == str(stamp.strftime('%d')) and \
               self.datetime['hour'] == str(stamp.strftime('%H')) and self.datetime['minute'] == str(stamp.strftime('%M')):
                setNotification(self.title, self.task, 20, './notification/icons/task_icon.ico')
                self.notification = False
                self.datetime = None
