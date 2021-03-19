from datetime import datetime
from notification import setNotification
from functions import string_to_date_object, add_days, add_months, add_years

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

    def getNotification(self):
        return [self.__notification, self.__datetime, self.__occure_gap, self.__repeat]

    def getNotificationDate(self) -> str:
        if self.__notification:
            string = f'Następne powiadomienie: {self.__datetime["day"]}-{self.__datetime["month"]}-{self.__datetime["year"]} {self.__datetime["hour"]}:{self.__datetime["minute"]}\n'
            string += f'{self.__occure_gap} ile jeszcze: {self.__repeat}'
        else:
            string = 'Brak powiadomień'
        return string

    def getDate(self) -> list:
        return [f'{self.__datetime["year"]}-{self.__datetime["month"]}-{self.__datetime["day"]}', f'{self.__datetime["hour"]}', f'{self.__datetime["minute"]}'] if self.__notification else None

    def checkTaskNotification(self) -> bool:
        return self.__notification

    def __str__(self) -> str:
        return f'{self.__title}: {self.__task} Przypomnienie: {self.__datetime["day"]}/{self.__datetime["month"]}/{self.__datetime["year"]} {self.__datetime["hour"]}:' \
            f'{self.__datetime["minute"]}' if self.__notification else f'{self.__title}: {self.__task}'

    def compareDatetime(self, callback: callable) -> bool:
        if self.__notification:
            stamp = datetime.now()
            if self.__datetime['year'] == str(stamp.strftime('%Y')) and self.__datetime['month'] == str(stamp.strftime('%m')) and self.__datetime['day'] == str(stamp.strftime('%d')) and \
               self.__datetime['hour'] == str(stamp.strftime('%H')) and self.__datetime['minute'] == str(stamp.strftime('%M')):
                self.update_notification()
                date_string = f'{self.__datetime["day"]}/{self.__datetime["month"]}/{self.__datetime["year"]}/{self.__datetime["hour"]}/{self.__datetime["minute"]}'
                callback(self.__title, date_string, self.__occure_gap, self.__repeat)
                setNotification(self.__title, self.__task, 10, './notification/icons/task_icon.ico')
                return True
        return False

    def delete_notification(self):
        self.__notification = False
        self.__datetime = None
        self.__occure_gap = None
        self.__repeat = None

    def update_notification(self):
        if self.__occure_gap == 'ONCE':
            self.delete_notification()
        else:
            if self.__repeat >= 0:
                if self.__repeat != 0:
                    self.__repeat = self.__repeat - 1 if self.__repeat > 1 else -1
                if self.__occure_gap == 'WEEK':
                    next_date = add_days(string_to_date_object(f'{self.getDate()[0]}'), 7)
                elif self.__occure_gap == 'MONTH':
                    next_date = add_months(string_to_date_object(f'{self.getDate()[0]}'), 1)
                elif self.__occure_gap == 'YEAR':
                    next_date = add_years(string_to_date_object(f'{self.getDate()[0]}'), 1)
                elif 'CUSTOM' in self.__occure_gap:
                    next_date = add_days(string_to_date_object(f'{self.getDate()[0]}'), int(self.__occure_gap[-1]))
                self.__datetime['year'] = next_date[0]
                self.__datetime['month'] = next_date[1]
                self.__datetime['day'] = next_date[2]
            else:
                self.delete_notification()
