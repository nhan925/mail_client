from PyQt6 import QtCore, QtWidgets, QtGui, uic
from PyQt6.QtWidgets import *
from PyQt6.uic import loadUi
import sys
import socket
import base64

#setup.ui
class Setup(QDialog):
    def __init__(self):
        super(Setup, self).__init__()
        uic.loadUi('setup.ui', self)
        self.continue_2.clicked.connect(self.login)

    def login(self):
        global un
        un = self.usernamein.text()
        global qa
        pa = self.passwordin.text()

        global smtp_sv
        smtp_sv = self.hostnamein_2.text()
        global smtp_p
        smtp_p = int(self.portin_2.text())
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect((smtp_sv, smtp_p))
            rcv = s.recv(1024).decode("utf8")
            msg = 'EHLO ' + '[' + smtp_sv + ']\r\n'
            s.sendall(bytes(msg, "utf8"))
            rcv = s.recv(1024).decode("utf8")
            msg = 'QUIT\r\n'
            s.sendall(bytes(msg, "utf8"))
            s.close()
        except:
            QMessageBox.information(self, 'Login', 'Fail')

        global pop3_sv
        pop3_sv = self.hostnamein.text()
        global pop3_p
        pop3_p = int(self.portin.text())
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
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
        except:
            QMessageBox.information(self, 'Login', 'Fail')

app = QApplication(sys.argv)
widget = QtWidgets.QStackedWidget()
setup_f = Setup()
widget.addWidget(setup_f)
widget.show()
app.exec()