from datetime import datetime
from notification import setNotification


class Task:

    def __init__(self, title, task, notification=False, datetime=None) -> None:
        self.__title = title
        self.__task = task
        self.__notification = notification
        self.__datetime = datetime

    def getTitle(self):
        return self.__title

    def getTask(self):
        return self.__task

    def getNotificationDate(self):
        return f'{self.__datetime["day"]}-{self.__datetime["month"]}-{self.__datetime["year"]} {self.__datetime["hour"]}:{self.__datetime["minute"]}'

    def getDate(self):
        return [f'{self.__datetime["year"]}-{self.__datetime["month"]}-{self.__datetime["day"]}', f'{self.__datetime["hour"]}', f'{self.__datetime["minute"]}'] if self.__notification else None

    def checkTaskNotification(self):
        return self.__notification

    def __str__(self) -> str:
        return f'{self.__title}: {self.__task} Przypomnienie: {self.__datetime["day"]}/{self.__datetime["month"]}/{self.__datetime["year"]} {self.__datetime["hour"]}:' \
            f'{self.__datetime["minute"]}' if self.__notification else f'{self.__title}: {self.__task}'

    def compareDatetime(self):
        if self.__notification:
            stamp = datetime.now()
            if self.__datetime['year'] == str(stamp.strftime('%Y')) and self.__datetime['month'] == str(stamp.strftime('%m')) and self.__datetime['day'] == str(stamp.strftime('%d')) and \
               self.__datetime['hour'] == str(stamp.strftime('%H')) and self.__datetime['minute'] == str(stamp.strftime('%M')):
                setNotification(self.__title, self.__task, 20, './notification/icons/task_icon.ico')
                self.__notification = False
                self.__datetime = None
