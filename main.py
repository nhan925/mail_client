from PyQt6.QtWidgets import QApplication, QMainWindow, QCommandLinkButton,  QListWidgetItem
from PyQt6.QtGui import QFont, QIcon
from PyQt6 import uic
import new_mail
import read_mail
import os
import data

class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        self.send_windows = None
        self.current_folder = data.inbox_dir
        self.current_endline = '\n\n'
        uic.loadUi('main.ui', self)
        self.load_mails(data.inbox_dir, '\n\n')
        self.inbox.setChecked(True)
        self.inbox.clicked.connect(lambda: self.select_a_button(data.inbox_dir, '\n\n'))
        self.sent.clicked.connect(lambda: self.select_a_button(data.sent_dir, '\n'))
        self.spam.clicked.connect(lambda: self.select_a_button(data.spam_dir, '\n\n'))
        self.trash.clicked.connect(lambda: self.select_a_button(data.trash_dir, '\n\n'))
        self.newmail.clicked.connect(self.send_new_mail)
        self.reload.clicked.connect(self._reload)


    def load_mails(self, folder_path, endline):
        self.contentlist.clear()
        files = os.listdir(folder_path)
        email_list = {}
        for filename in files:
            file_path = os.path.join(folder_path, filename)
            if os.path.isfile(file_path):
                with open(file_path, 'r') as file:
                    dat = file.read()
                    email_list.update({filename[0:-5]: read_mail.D3_parse_mime_email(dat, endline)})

        for key, data in email_list.items():
            sender = f"[{data['Headers']['From']}]"
            subject = data['Headers']['Subject']
            item = QListWidgetItem(f"{sender}\n{subject}")
            item.setData(1, key)
            font = QFont('Segoe UI', 10, QFont.Weight.Medium)
            item.setFont(font)
            item.setIcon(QIcon('icon/double_arrow.png'))
            self.contentlist.addItem(item)


    def select_a_button(self, load_dir, endline):
        self.current_folder = load_dir
        self.current_endline = endline
        clicked_button = self.sender()
        for button in self.findChildren(QCommandLinkButton):
            button.setChecked(False)
        clicked_button.setChecked(True)
        self.load_mails(load_dir, endline)

    def send_new_mail(self):
        self.send_windows = new_mail.NewMail()
        self.send_windows.exec()


    def _reload(self):
        read_mail.D3_reload_mails(data.pop3_server, data.pop3_port, data.username, data.password)
        print(self.current_folder, self.current_endline)
        self.load_mails(self.current_folder, self.current_endline)


