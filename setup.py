from PyQt6 import QtCore, QtWidgets, QtGui, uic
from PyQt6.QtWidgets import *
import socket
import data
import main

#setup.ui
class Setup(QDialog):
    def __init__(self):
        super(Setup, self).__init__()
        self.main_windows = None
        uic.loadUi('setup.ui', self)
        self.continue_2.clicked.connect(self.login)

    def login(self):
        un = self.usernamein.text()
        pa = self.passwordin.text()
        smtp_sv = self.hostnamein_2.text()
        smtp_p = int(self.portin_2.text())
        pop3_sv = self.hostnamein.text()
        pop3_p = int(self.portin.text())
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(3)
            s.connect((smtp_sv, smtp_p))
            rcv = s.recv(1024).decode("utf8")
            msg = 'EHLO ' + '[' + smtp_sv + ']\r\n'
            s.sendall(bytes(msg, "utf8"))
            rcv = s.recv(1024).decode("utf8")
            msg = 'QUIT\r\n'
            s.sendall(bytes(msg, "utf8"))
            s.close()

            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(3)
            s.connect((pop3_sv, pop3_p))
            rcv = s.recv(1024).decode("utf8")
            msg = 'CAPA\r\n'
            s.sendall(bytes(msg, "utf8"))
            rcv = s.recv(1024).decode("utf8")
            msg = 'USER ' + un + '\r\n'
            s.sendall(bytes(msg, "utf8"))
            rcv = s.recv(1024).decode("utf8")
            if (rcv[:3] != '+OK'):
                QMessageBox.information(self, 'Login', 'Fail')
                s.sendall(bytes('QUIT\r\n', "utf8"))
                s.close()
                return
            msg = 'PASS ' + pa + '\r\n'
            s.sendall(bytes(msg, "utf8"))
            rcv = s.recv(1024).decode("utf8")
            if (rcv[:3] != '+OK'):
                QMessageBox.information(self, 'Login', 'Fail')
                s.sendall(bytes('QUIT\r\n', "utf8"))
                s.close()
                return
            msg = 'QUIT\r\n'
            s.sendall(bytes(msg, "utf8"))
            s.close()
            data.username = un
            data.password = pa
            data.smtp_server = smtp_sv
            data.smtp_port = smtp_p
            data.pop3_server = pop3_sv
            data.pop3_port = pop3_p
            QMessageBox.information(self, 'Login', 'Success !')
            self.close()
            self.main_windows = main.Main()
            self.main_windows.show()
        except:
            QMessageBox.information(self, 'Login', 'Fail')