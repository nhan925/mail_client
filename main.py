from PyQt6.QtWidgets import QMainWindow, QCommandLinkButton,  QListWidgetItem
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtWidgets import *
from PyQt6 import uic
import new_mail
import read_mail
import os
import data
import filter
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtCore import QUrl


class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        self.read_mail_windows = None
        self.send_windows = None
        self.filter_windows = None
        self.current_folder = data.inbox_dir
        self.current_endline = '\n\n'
        uic.loadUi('main.ui', self)
        self.create_default_folders()
        self._reload()
        self.load_filters()
        self.load_mails(data.inbox_dir, '\n\n')
        self.inbox.setChecked(True)
        self.inbox.clicked.connect(lambda: self.select_a_button(data.inbox_dir, '\n\n'))
        self.sent.clicked.connect(lambda: self.select_a_button(data.sent_dir, '\n'))
        self.spam.clicked.connect(lambda: self.select_a_button(data.spam_dir, '\n\n'))
        self.trash.clicked.connect(lambda: self.select_a_button(data.trash_dir, '\n\n'))
        self.newmail.clicked.connect(self.send_new_mail)
        self.reload.clicked.connect(self._reload)
        self.files.clicked.connect(self.load_files)
        self.contentlist.itemDoubleClicked.connect(self.double_click_item)
        self.addfilters.clicked.connect(self.add_filter)
        self.deleteall.clicked.connect(self.clean_trash)
        self.filterlist.itemClicked.connect(self.open_filter)


    def create_default_folders(self):
        folders = [data.inbox_dir, data.sent_dir, data.spam_dir, data.trash_dir, data.files_dir]
        for folder in folders:
            if not os.path.exists(folder):
                os.makedirs(folder)

    def load_mails(self, folder_path, endline):
        self.contentlist.clear()
        files = os.listdir(folder_path)
        email_list = {}
        for filename in files:
            file_path = os.path.join(folder_path, filename)
            if os.path.isfile(file_path):
                with open(file_path, 'r') as file:
                    dat = file.read()
                    email_list.update({filename[0:-4]: read_mail.D3_parse_mime_email(dat, endline)})

        for key, data in email_list.items():
            sender = f"[{data['Headers']['From']}]"
            subject = data['Headers']['Subject']
            item = QListWidgetItem(f"{sender}\n{subject}")
            font = QFont('Segoe UI', 10, QFont.Weight.Medium)
            item.setFont(font)
            item.setData(1, key)
            self.contentlist.addItem(item)


    def select_a_button(self, load_dir, endline):
        self.filterlist.clearSelection()
        if (load_dir == data.trash_dir):
            self.deleteall.setEnabled(1)
        else:
            self.deleteall.setEnabled(0)
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
        if self.current_folder == data.files_dir:
            self.load_files()
        else:
            self.load_mails(self.current_folder, self.current_endline)



    def load_files(self):
        self.deleteall.setEnabled(0)
        self.current_folder = data.files_dir
        clicked_button = self.sender()
        for button in self.findChildren(QCommandLinkButton):
            button.setChecked(False)
        clicked_button.setChecked(True)
        self.contentlist.clear()
        files = os.listdir(data.files_dir)
        for file in files:
            item = QListWidgetItem(f"{file}")
            font = QFont('Segoe UI', 10, QFont.Weight.Medium)
            item.setFont(font)
            item.setData(1, file)
            self.contentlist.addItem(item)

    def double_click_item(self, item):
        if (self.current_folder == data.files_dir):
            if os.path.exists(f"{data.files_dir}/{item.data(1)}"):
                QDesktopServices.openUrl(QUrl.fromLocalFile(f"{data.files_dir}/{item.data(1)}"))
            else:
                QMessageBox.information(self, 'Error', 'File has been deleted !')
                self.contentlist.clear()
                file_list = os.listdir(data.files_dir)
                for file in file_list:
                    item = QListWidgetItem(f"{file}")
                    font = QFont('Segoe UI', 10, QFont.Weight.Medium)
                    item.setFont(font)
                    item.setData(1, file)
                    self.contentlist.addItem(item)
        else:
            raw_mail = ''
            file_path = f"{self.current_folder}/{item.data(1)}.msg"
            if os.path.exists(file_path):
                with open(file_path, 'r') as file:
                    raw_mail = file.read()
                read_mail.display_info = read_mail.D3_parse_mime_email(raw_mail, self.current_endline)
                read_mail.current_mail_id = item.data(1)
                self.read_mail_windows = read_mail.ReadMail()
                self.read_mail_windows.exec()
                return
            else:
                QMessageBox.information(self, 'Error', 'Mail has been deleted !')
                self.load_mails(self.current_folder, self.current_endline)

    def load_filters(self):
        self.filterlist.clear()
        for key, value in data.filters.items():
            if key == 'spam' or key == 'spam1':
                continue
            item = QListWidgetItem(QIcon('icon/folder.png'), key.capitalize())
            font = QFont('Segoe UI', 11, QFont.Weight.Bold)
            item.setFont(font)
            self.filterlist.addItem(item)

    def open_filter(self, item):
        self.current_folder = item.text().lower()
        self.current_endline = '\n\n'
        for button in self.findChildren(QCommandLinkButton):
            button.setChecked(False)
        self.load_mails(self.current_folder, self.current_endline)


    def add_filter(self):
        self.filter_windows = filter.Filters(self)
        self.filter_windows.exec()


    def clean_trash(self):
        for filename in os.listdir(data.trash_dir):
            file_path = os.path.join(data.trash_dir, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
        self.load_mails(self.current_folder, self.current_endline)