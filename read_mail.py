import socket
import base64
import json
import os
import shutil
import data
from PyQt6 import uic
from PyQt6.QtWidgets import *
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtCore import QUrl

display_info = {}
current_mail_id = ''


class ReadMail(QDialog):
    def __init__(self, main_windows):
        super(ReadMail, self).__init__(main_windows)
        uic.loadUi('read_mail.ui', self)
        self.main_windows = main_windows
        self.fromwho.setText(display_info['Headers']['From'])
        self.to.setText(display_info['Headers']['To'])
        self.cc.setText(display_info['Headers']['Cc'])
        self.subject.setText(display_info['Headers']['Subject'])
        self.content.setText(display_info['Text'])
        for file in display_info['Attachments']:
            item = QListWidgetItem(file['filename'])
            item.setData(1, current_mail_id + '_' + file['filename'])
            self.attachments.addItem(item)
        if not display_info['Attachments'] or self.main_windows.current_folder == data.sent_dir:
            self.openfolder.setEnabled(0)
        self.attachments.itemDoubleClicked.connect(self.doubleclick_attachments)
        self.closewindows.clicked.connect(self.close)
        self.openfolder.clicked.connect(self.openfolder_func)
        self.delete_2.clicked.connect(self.delete_mail)

    def doubleclick_attachments(self, item):
        if self.main_windows.current_folder == data.sent_dir:
            return
        if os.path.exists(f"{data.files_dir}/{item.data(1)}"):
            QDesktopServices.openUrl(QUrl.fromLocalFile(f"{data.files_dir}/{item.data(1)}"))
        else:
            QMessageBox.information(self, 'Error', 'File has been deleted !')

    def openfolder_func(self):
        QDesktopServices.openUrl(QUrl.fromLocalFile(data.files_dir))

    def delete_mail(self):
        if self.main_windows.current_folder == data.sent_dir:
            dest = shutil.move(f'{data.sent_dir}/{current_mail_id}.msg', data.trash_dir)
        elif self.main_windows.current_folder == data.trash_dir:
            file_path = f'{data.trash_dir}/{current_mail_id}.msg'
            if os.path.isfile(file_path):
                os.remove(file_path)
        else:
            D3_delete_on_client(current_mail_id, self.main_windows.current_folder)
        self.close()
        self.main_windows.load_mails(self.main_windows.current_folder, self.main_windows.current_endline)


def D3_receive_data(sock, s_condition=b'\r\n'):
    data = b""
    while True:
        chunk = sock.recv(8192)
        if not chunk:
            break
        data += chunk
        if s_condition in chunk:
            break
    return data


def D3_send_command(sock, command, s_condition=b'\r\n'):
    sock.sendall(command.encode('utf-8') + b'\r\n')
    return D3_receive_data(sock, s_condition)


def D3_list_to_dict(list_mails):
    list_mails = list_mails.split('\r\n')[1:-2]
    data = {str(i): list_mails[i - 1].split()[1] for i in range(1, len(list_mails) + 1)}
    return data


def D3_uidl_status_read(list_uidl):
    list_uidl = list_uidl.split('\r\n')[1:-2]
    data = {str(i): {'uidl': list_uidl[i - 1].split()[1], 'status': "unread"} for i in range(1, len(list_uidl) + 1)}
    return data


def D3_save_list(data, filename):
    # write .json
    with open(filename, 'w') as json_file:
        json.dump(data, json_file, indent=2)
        json_file.close()


def D3_read_json_file(file_path):
    with open(file_path, 'r') as json_file:
        data = json.loads(json_file.read())
        json_file.close()
    return data


def D3_compare_UIDL(data_1):
    file_path = "uidl_list.json"
    _data = D3_read_json_file(file_path)
    add_mails = {}
    remove_mails = {}
    # test
    # print(_data,"\n\n")
    print(len(_data), len(data_1), sep="-")
    list_key = list(_data.keys())
    if len(list_key) != 0:
        last_key = list_key[-1]
    else:
        last_key = 0
    for key, value in data_1.items():
        if int(key) < int(last_key):
            if key not in list_key:
                remove_mails.update({key: value})
            else:
                continue
        elif int(key) > int(last_key):
            if os.path.exists(f"{data.trash_dir}/{value['uidl'][0:-4]}.msg"):
                remove_mails.update({key: value})
            else:
                add_mails.update({key: value})
    if remove_mails != {} or add_mails != {}:
        if remove_mails != {}:
            _data.update(add_mails)
            a = list(f'{i}' for i in range(1, len(_data) + 1, 1))
            _data = dict(zip(a, list(_data.values())))
        else:
            _data.update(add_mails)
        data.mail_status = _data
        with open(file_path, 'w') as file:
            file.write(json.dumps(_data))
            file.close()
    return add_mails, remove_mails


def D1_filter_mail(filters, email_info):
    check = False
    for i in filters:
        filter_field = None
        if filters[i]['filter_by'] == "subject":
            filter_field = email_info['Headers']['Subject']
        elif filters[i]['filter_by'] == "content":
            filter_field = email_info['Text']
        else:
            filter_field = email_info['Headers']['From']

        for j in filters[i]['keywords']:
            check = j in filter_field
            if check == True:
                return filters[i]['filter_dir']
    return data.inbox_dir


def D3_save_mails(email_info, data_mail, mes_id, filters):
    dir = D1_filter_mail(filters, email_info)
    if not os.path.exists(dir):
        os.makedirs(dir)
    # write file.msg
    file_path = os.path.join(dir, f"{mes_id}.msg")
    with open(file_path, 'w') as msg_file:
        msg_file.write(data_mail)
        msg_file.close()


def D3_extract(str_1, str_2, part):
    if str_1 in part:
        return part.split(str_1, 1)[1].split(str_2, 1)[0].strip('"')
    else:
        return ' '


def D3_extract_headers(headers, string):
    data = {}
    str_2 = string
    data['From'] = D3_extract("From: ", str_2, headers)
    data['To'] = D3_extract("To: ", str_2, headers)
    data['Cc'] = D3_extract("Cc: ", str_2, headers)
    data['Subject'] = D3_extract("Subject: ", str_2, headers)
    data['Boundary'] = D3_extract("Content-Type: multipart/mixed; boundary=", str_2, headers)
    return data


def D3_extract_body(parts, boundary, string):
    content = " "
    list_attachments = []
    for part in parts[1:-1]:
        if "Content-Disposition: attachment" in part:
            attachment = {
                'Content-Type': D3_extract('Content-Type: ', ";", part),
                'filename': D3_extract("filename=", string, part),
                'content': D3_extract(string + string, string + string, part).encode('utf-8')
            }
            list_attachments.append(attachment)
        else:
            content = D3_extract(string + string, "--" + boundary, part).strip(string + string)
    return content, list_attachments


def D3_parse_mime_email(raw_email, string):
    email_info = {}
    # Parsing email into head and bodys
    headers, body = raw_email.split(string + string, 1)
    email_info['Headers'] = D3_extract_headers(headers, string)

    boundary = email_info['Headers']['Boundary']
    if boundary != " ":
        parts = body.split('--' + boundary)
        email_info['Text'], email_info['Attachments'] = D3_extract_body(parts, boundary, string)
    else:
        email_info['Text'] = body
        email_info['Attachments'] = []
    return email_info


def D3_save_attachments(list_attachments, mes_id):
    if not os.path.exists(data.files_dir):
        os.makedirs(data.files_dir)
    for attachment in list_attachments:
        filename = mes_id + '_' + attachment['filename']
        file_path = os.path.join(data.files_dir, filename)
        # if os.path.exists(file_path): return
        with open(file_path, 'wb') as file:
            _dat = attachment['content'].replace(b'\r\n', b' ')
            decoded_dat = base64.b64decode(_dat)
            file.write(decoded_dat)
            file.close()


def D3_delete_on_client(mes_id, current_folder):
    # Move mes_<id>.msg
    bin = data.trash_dir
    source = f"{current_folder}/{mes_id}.msg"
    destination = bin
    if not os.path.exists(bin + f"/{mes_id}.msg"):
        dest = shutil.move(source, destination)
    # update uidl_list
    path_uidl = "uidl_list.json"
    _data = {}
    with open(path_uidl, 'r') as file:
        _data = json.loads(file.read())
        file.close()
    for key, value in _data.items():
        if value['uidl'] == f"{mes_id}.msg":
            key_remove = key
    del _data[str(key_remove)]
    data.mail_status = _data
    with open(path_uidl, 'w') as file:
        file.write(json.dumps(_data))
        file.close()


# if delete on interface user call this function
def D3_delete_on_server(sock, remove_mails):
    for key in remove_mails.keys():
        response = D3_send_command(sock, f"DELE {key}")


def D3_fetch_mail(sock, add_mails):
    # Read raw mail
    for key, value in add_mails.items():
        raw_email = D3_send_command(sock, f"RETR {key}", b'\r\n.\r\n').decode('utf-8')
        # print(raw_email)
        email_info = D3_parse_mime_email(raw_email, "\r\n")
        if email_info['Attachments'] != []:
            D3_save_attachments(email_info['Attachments'], value['uidl'][0:-4])
        D3_save_mails(email_info, raw_email, value['uidl'][0:-4], data.filters)


def D3_reload_mails(pop3_server, pop3_port, username, password):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(1)
        try:
            sock.connect((pop3_server, pop3_port))
        except:
            return

        D3_receive_data(sock)
        D3_send_command(sock, "CAPA")
        D3_send_command(sock, f"USER {username}")
        D3_send_command(sock, f"PASS {password}")

        # Stat: get the number of emails and their total size
        response = D3_send_command(sock, "STAT")
        num_emails, total_size = map(int, response.split()[1:3])

        # LIST: get list of mails and their size
        # list_mails=map(str,D3_send_command(sock,'LIST').split(b'\r\n')[1:-2])
        list_mails_bytes = D3_send_command(sock, "LIST").decode('utf-8')
        _data = D3_list_to_dict(list_mails_bytes)
        D3_save_list(_data, "list_bytes.json")

        # UIDL: get a list of unique identifiers assigned by the server to each message
        list_UIDL = D3_send_command(sock, "UIDL").decode('utf-8')
        print(list_UIDL)
        # if list_UIDL != {}:
        data_1 = D3_uidl_status_read(list_UIDL)
        add_mails = {}
        remove_mails = {}

        if not os.path.exists("uidl_list.json"):
            add_mails = data_1
            data.mail_status = data_1
            D3_save_list(data_1, "uidl_list.json")
        else:
            add_mails, remove_mails = D3_compare_UIDL(data_1)
        D3_delete_on_server(sock, remove_mails)
        D3_fetch_mail(sock, add_mails)
        D3_send_command(sock, 'QUIT')


def D3_status_index(email_uidl, data):
    for key, value in data.items():
        if (value['uidl'] == email_uidl + ".msg"):
            return str(key)
