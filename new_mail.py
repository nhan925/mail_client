import socket
import base64
from PyQt6 import QtWidgets, uic
from PyQt6.QtWidgets import *
import sys
import os

def send_email(smtp_server, smtp_port, smtp_username, recipient_email, subject, body, attachment_paths, cc_email, bcc_email):
    recipients = str(recipient_email).replace("'", "").removeprefix('[').removesuffix(']')
    cc_recipients = str(cc_email).replace("'", "").removeprefix('[').removesuffix(']')
    # Construct the MIME message manually
    message = f"""\
From: {smtp_username}
To: {recipients}
"""
    if cc_email[0] != '':
        message += f'Cc: {cc_recipients}\n'
        recipient_email = recipient_email + cc_email
    if bcc_email[0] != '':
        recipient_email = recipient_email + bcc_email
    continue_mes = f"""\
Subject: {subject}
MIME-Version: 1.0
Content-Type: multipart/mixed; boundary="dGhpc19pc190aGVfc2VwYXJhdGVkX3N0cmluZw=="

--dGhpc19pc190aGVfc2VwYXJhdGVkX3N0cmluZw==
Content-Type: text/plain; charset="utf-8"
Content-Transfer-Encoding: 7bit

{body}

"""
    message += continue_mes

    # Attach files
    for attachment_path in attachment_paths:
        with open(attachment_path, 'rb') as attachment_file:
            attachment_data = attachment_file.read()
            attachment_base64 = base64.b64encode(attachment_data).decode('utf-8')
            attachment_name = os.path.basename(attachment_path) # Extract the file name
            attachment_content_type = 'application/octet-stream'  # Binary content type
            attachment_part = f"""\
--dGhpc19pc190aGVfc2VwYXJhdGVkX3N0cmluZw==
Content-Type: {attachment_content_type}
MIME-Version: 1.0
Content-Disposition: attachment; filename="{attachment_name}"
Content-Transfer-Encoding: base64

"""

            # Split the base64 data into lines with a maximum line length
            max_line_length = 8192  # RFC 2045 suggests a maximum line length of 76 characters
            for i in range(0, len(attachment_base64), max_line_length):
                line = attachment_base64[i:i + max_line_length]
                # Escape lines starting with a dot
                if line.startswith('.'):
                    line = '.' + line
                attachment_part += line + '\r\n'

            message += attachment_part

    message += '--dGhpc19pc190aGVfc2VwYXJhdGVkX3N0cmluZw==--'

    # Connect to the SMTP server manually
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.connect((smtp_server, smtp_port))

        # Receive the server's greeting
        server.recv(1024)

        # Send EHLO
        server.sendall(f'EHLO {socket.gethostname()}\r\n'.encode('utf-8'))
        server.recv(1024)

        # Send MAIL FROM
        server.sendall(f'MAIL FROM: <{smtp_username}>\r\n'.encode('utf-8'))
        server.recv(1024)

        # Send RCPT TO
        for _to in recipient_email:
            server.sendall(f'RCPT TO: <{_to}>\r\n'.encode('utf-8'))
            server.recv(1024)

        # Send DATA
        server.sendall(f'DATA\r\n'.encode('utf-8'))
        server.recv(1024)

        # Send the email message
        server.sendall(message.encode('utf-8'))

        # Send end of data marker
        server.sendall(f'\r\n.\r\n'.encode('utf-8'))
        server.recv(1024)

        # Send QUIT
        server.sendall(f'QUIT\r\n'.encode('utf-8'))
        server.recv(1024)

#new_mail.ui
class NewMail(QDialog):
    def __init__(self):
        super(NewMail, self).__init__()
        uic.loadUi('new_mail.ui', self)
        self.attach.clicked.connect(self._attach)
        self.send.clicked.connect(self._send)
        self.clear.clicked.connect(self._clear_att)

    attached_files = []
    file_size_limit = 3 #in MB
    def _attach(self):
        choose_file = QFileDialog()
        success = choose_file.exec()
        if success:
            selectedfile = QFileDialog.selectedFiles(choose_file)[0]
            attachment_size = os.path.getsize(selectedfile)
            if (attachment_size > self.file_size_limit * 1024 * 1024):
                QMessageBox.warning(
                    None,
                    "File Size Exceeded",
                    f"The file size of '{os.path.basename(selectedfile)}' exceeds the limit of {self.file_size_limit} MB.",
                    QMessageBox.StandardButton.Ok
                )
                return
            self.attached_files.append(selectedfile)
            selectedfile = os.path.basename(selectedfile)
            if self.attachments.text():
                selectedfile = ", " + selectedfile
            self.attachments.setText(self.attachments.text() + selectedfile + ' (' + str(round(attachment_size/1024, 3)) + ' KB)')

    def _send(self):
        try:
            receiver = self.to.text()
            at_idx = receiver.find('@')
            if receiver == '' or at_idx == 0 or receiver[at_idx + 1] == '':
                QMessageBox.information(self, 'Mes', 'Fail !')
                return
            receiver_list = receiver.split(',')
            receiver_list = [tok.strip() for tok in receiver_list]
            cc = self.cc.text()
            cc_list = cc.split(',')
            cc_list = [tok.strip() for tok in cc_list]
            bcc = self.bcc.text()
            bcc_list = bcc.split(',')
            bcc_list = [tok.strip() for tok in bcc_list]
            sub = self.subject.text()
            cont = self.content.toPlainText()
            attachments = self.attached_files
            send_email(
                smtp_server='127.0.0.1',
                smtp_port=25,
                smtp_username='newmail@new.com',
                recipient_email=receiver_list,
                subject=sub,
                body=cont,
                attachment_paths=attachments,
                cc_email=cc_list,
                bcc_email=bcc_list
            )
            QMessageBox.information(self, 'Mes', 'Email sent successfully !')
            self.to.clear()
            self.cc.clear()
            self.bcc.clear()
            self.subject.clear()
            self.content.clear()
            self.attachments.clear()
            self.attached_files.clear()
        except:
            QMessageBox.information(self, 'Mes', 'Fail !')

    def _clear_att(self):
        self.attached_files.clear()
        self.attachments.clear()


app = QApplication(sys.argv)
widget = QtWidgets.QStackedWidget()
newmail_f = NewMail()
widget.addWidget(newmail_f)
widget.show()
app.exec()
