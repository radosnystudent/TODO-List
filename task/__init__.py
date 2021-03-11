from datetime import datetime
from notification import setNotification


class Task:

    def __init__(self, title: str, task: str, notification=False, datetime=None, occure_gap=None, repeat=None) -> None:
        self.__title = title
        self.__task = task
        self.__notification = notification
        self.__datetime = datetime
        self.__occure_gap = occure_gap
        self.__repeat = repeat

    def getTitle(self) -> str:
        return self.__title

    def getTask(self) -> str:
        return self.__task

    def getNotificationDate(self) -> str:
        return f'{self.__datetime["day"]}-{self.__datetime["month"]}-{self.__datetime["year"]} {self.__datetime["hour"]}:{self.__datetime["minute"]}'

    def getDate(self) -> list:
        return [f'{self.__datetime["year"]}-{self.__datetime["month"]}-{self.__datetime["day"]}', f'{self.__datetime["hour"]}', f'{self.__datetime["minute"]}'] if self.__notification else None

    def checkTaskNotification(self) -> bool:
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
