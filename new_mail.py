import socket
import base64
from PyQt6 import uic
from PyQt6.QtWidgets import *
import os
import data
from datetime import datetime


def generate_unique_name():
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    unique_name = f"{timestamp}"
    return unique_name


def save_sent_mail(msg):
    with open(data.sent_dir + '/' + generate_unique_name() + '.msg', 'w') as sent_mes:
        sent_mes.write(msg.replace('\n', '\n\n'))
        sent_mes.close()


# Send email with collected data
def send_mail(smtp_server, smtp_port, smtp_username, recipient_email, subject, body, attachment_paths, cc_email,
              bcc_email):
    recipients = str(recipient_email).replace("'", "").removeprefix('[').removesuffix(']')
    cc_recipients = str(cc_email).replace("'", "").removeprefix('[').removesuffix(']')
    boundary = base64.b64encode((generate_unique_name() + data.username).encode('utf-8')).decode('utf-8')
    # Construct MIME message
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
Content-Type: multipart/mixed; boundary="{boundary}"

--{boundary}
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
            attachment_name = os.path.basename(attachment_path)
            attachment_content_type = 'application/octet-stream'
            attachment_part = f"""\
--{boundary}
Content-Type: {attachment_content_type}
MIME-Version: 1.0
Content-Disposition: attachment; filename="{attachment_name}"
Content-Transfer-Encoding: base64

"""

            # Split base64 data into lines
            max_line_length = 8192
            for i in range(0, len(attachment_base64), max_line_length):
                line = attachment_base64[i:i + max_line_length]
                if line.startswith('.'):
                    line = '.' + line
                attachment_part += line + '\r\n'

            message += attachment_part
            attachment_file.close()

    message += f'--{boundary}--'

    # Send mail to server
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.settimeout(2)
        server.connect((smtp_server, smtp_port))
        server.recv(1024)

        # EHLO
        server.sendall(f'EHLO {socket.gethostname()}\r\n'.encode('utf-8'))
        server.recv(1024)

        # MAIL FROM
        server.sendall(f'MAIL FROM: <{smtp_username}>\r\n'.encode('utf-8'))
        server.recv(1024)

        # RCPT TO
        for _to in recipient_email:
            server.sendall(f'RCPT TO: <{_to}>\r\n'.encode('utf-8'))
            server.recv(1024)

        # DATA
        server.sendall(f'DATA\r\n'.encode('utf-8'))
        server.recv(1024)
        server.sendall(message.encode('utf-8'))
        server.sendall(f'\r\n.\r\n'.encode('utf-8'))
        server.recv(1024)

        # QUIT
        server.sendall(f'QUIT\r\n'.encode('utf-8'))
        server.recv(1024)

    # Save sent message
    save_sent_mail(message)


# new_mail.ui
class NewMail(QDialog):
    def __init__(self):
        self.attached_files = []
        self.file_size_limit = 3  # in MB
        super(NewMail, self).__init__()
        uic.loadUi('new_mail.ui', self)
        self.attach.clicked.connect(self._attach)
        self.send.clicked.connect(self._send)
        self.clear.clicked.connect(self._clear_att)
        self.clear_one.clicked.connect(self._clear_one_att)



    def _attach(self):
        choose_file = QFileDialog()
        success = choose_file.exec()
        if success:
            selectedfile = QFileDialog.selectedFiles(choose_file)[0]
            if selectedfile in self.attached_files:
                QMessageBox.warning(
                    None,
                    "Duplicate File",
                    f"The file is already attached !",
                    QMessageBox.StandardButton.Ok
                )
                return
            attachment_size = os.path.getsize(selectedfile)
            if (attachment_size > self.file_size_limit * 1024 * 1024):
                QMessageBox.warning(
                    None,
                    "File Size Exceeded",
                    f"The file size of '{os.path.basename(selectedfile)}' exceeds the limit of {self.file_size_limit} MB.",
                    QMessageBox.StandardButton.Ok
                )
                return
            if (attachment_size == 0):
                QMessageBox.warning(
                    None,
                    "Empty File",
                    f"The file '{os.path.basename(selectedfile)}' is empty. Please choose another file !",
                    QMessageBox.StandardButton.Ok
                )
                return
            self.attached_files.append(selectedfile)
            selectedfile = os.path.basename(selectedfile)
            self.attachments.addItem(selectedfile + ' (' + str(round(attachment_size / 1024, 3)) + ' KB)')

    def _send(self):
        try:
            receiver = self.to.text()
            at_idx = receiver.find('@')
            if receiver == '' or at_idx == 0 or at_idx == -1 or receiver[at_idx + 1] == '':
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

            send_mail(
                smtp_server=data.smtp_server,
                smtp_port=data.smtp_port,
                smtp_username=data.username,
                recipient_email=receiver_list,
                subject=sub,
                body=cont,
                attachment_paths=attachments,
                cc_email=cc_list,
                bcc_email=bcc_list
            )
            QMessageBox.information(self, 'Mes', 'Email sent successfully !')
            self.close()
        except:
            QMessageBox.information(self, 'Mes', 'Fail !')

    def _clear_att(self):
        self.attached_files.clear()
        self.attachments.clear()


    def _clear_one_att(self):
        selected_item = self.attachments.currentItem()
        if selected_item is not None:
            row = self.attachments.row(selected_item)
            self.attachments.takeItem(row)
            del self.attached_files[row]
