import csv

def readCSV() -> list:
    allTasks = []
    with open('./datafiles/datafile.csv', 'r') as csfile:
        reader = csv.reader(csfile, delimiter=',')
        for line in reader:
            notification = True if line[2] == 'Tak' else False
            if line[3] == 'empty':
                datetime = None
            else:
                datetime = {line[3].split(':')[0]: line[3].split(':')[1],
                            line[4].split(':')[0]: line[4].split(':')[1],
                            line[5].split(':')[0]: line[5].split(':')[1],
                            line[6].split(':')[0]: line[6].split(':')[1],
                            line[7].split(':')[0]: line[7].split(':')[1]}
            newTask = Task(line[0], line[1], notification, datetime)
            allTasks.append(newTask)

    return allTasks

class Task:

    def __init__(self, title, task, notification=False, datetime=None) -> None:
        self.title = title
        self.task = task
        self.notification = notification
        self.datetime = datetime

    def __str__(self) -> str:
        return f'{self.title}\n{self.task}\n{self.notification}\n{self.datetime}'

    def writeToCsv(self):
        with open('./datafiles/datafile.csv', 'a', newline='', encoding='utf-8') as csfile:
            writer = csv.writer(csfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            notification = 'Tak' if self.notification else 'Nie'
            date = []
            if self.datetime is not None:
                for key, value in self.datetime.items():
                    date.append(f'{key}:{value}')
            else:
                date.append('empty')

            writer.writerow([self.title, self.task, notification] + date)
