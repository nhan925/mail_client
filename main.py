from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6 import uic
import new_mail

class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        self.send_windows = None
        uic.loadUi('main.ui', self)
        self.newmail.clicked.connect(self.send_new_mail)


    def send_new_mail(self):
        self.send_windows = new_mail.NewMail()
        self.send_windows.exec()


