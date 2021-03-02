from win10toast import ToastNotifier
import time


def setNotification(title: str, msg: str, duration: int, icon=None):
    toaster = ToastNotifier()
    toaster.show_toast(title, msg, icon_path=icon, duration=duration)

    while toaster.notification_active():
        time.sleep(0.1)
