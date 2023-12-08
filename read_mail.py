import socket
import base64
import json
import os, shutil
import data
from PyQt6 import QtWidgets, uic
from PyQt6.QtWidgets import *
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtCore import QUrl
import sys

save_to_folder = "debug/mailbox"
# duong dan den mailbox la data.inbox_dir

display_info = {}
current_mail_id = ''


class ReadMail(QDialog):
    def __init__(self):
        super(ReadMail, self).__init__()
        uic.loadUi('read_mail.ui', self)
        self.fromwho.setText(display_info['Headers']['From'])
        self.to.setText(display_info['Headers']['To'])
        self.cc.setText(display_info['Headers']['Cc'])
        self.subject.setText(display_info['Headers']['Subject'])
        self.content.setText(display_info['Text'])
        for file in display_info['Attachments']:
            item = QListWidgetItem(file['filename'])
            item.setData(1, current_mail_id + '_' + file['filename'])
            self.attachments.addItem(item)
        self.attachments.itemDoubleClicked.connect(self.doubleclick_attachments)
        self.closewindows.clicked.connect(self.close)
        self.openfolder.clicked.connect(self.openfolder_func)


    def doubleclick_attachments(self, item):
        if os.path.exists(f"{data.files_dir}/{item.data(1)}"):
            QDesktopServices.openUrl(QUrl.fromLocalFile(f"{data.files_dir}/{item.data(1)}"))
        else:
            QMessageBox.information(self, 'Error', 'File has been deleted !')


    def openfolder_func(self):
        QDesktopServices.openUrl(QUrl.fromLocalFile(data.files_dir))



def D3_receive_data(sock,s_condition=b'\r\n'):
    data = b""
    while True:
        chunk = sock.recv(8192)
        if not chunk:
            break
        data += chunk
        if s_condition in chunk:
            break
    return data

def D3_send_command(sock,command,s_condition=b'\r\n'):
    sock.sendall(command.encode('utf-8') + b'\r\n')
    return D3_receive_data(sock,s_condition)

"""def D3_receive_data_e(sock):
    data=b""
    while True:
        chunk = sock.recv(1024)
        if not chunk:
            break
        data += chunk
        if b'\r\n.\r\n' in chunk:
            break
    return data

def D3_send_command_e(sock,command):
    sock.sendall(command.encode('utf-8') + b'\r\n')
    return D3_receive_data_e(sock)"""

def D3_list_to_dict(list_mails):
    list_mails = list_mails.split('\r\n')[1:-2]
    data = {str(i): list_mails[i - 1].split()[1] for i in range(1, len(list_mails) + 1)}
    return data

def D3_save_list(data,filename):
    #write .json
    with open(filename,'w') as json_file:
        json_file.write(json.dumps(data))

    """with open(file_path,'r') as json_file:
        data = json.loads(json_file.read())
    for i in range(1,len(list_mails)+1):
        print(data[str(i)],end='\r\n')"""

def D3_read_json_file(file_path):
    with open(file_path,'r') as json_file:
        data=json.loads(json_file.read())
    return data

def D3_compare_UIDL(data_1):
    file_path="uidl_list.json"
    data = D3_read_json_file(file_path)
    add_mails={}
    remove_mails={}
    #test
    print(len(data),len(data_1),sep="-")
    list_key=list(data.keys())
    last_key=list_key[-1]
    for key,value in data_1.items():
        if key < last_key:
            if key not in list_key:
                remove_mails.update({key:value})
            else:
                continue
        else:
            if os.path.exists(f"Bin//mess_{value[0:-4]}.msg"):
                remove_mails.update({key:value})
            else:
                add_mails.update({key:value})

    """if len(data_1) != len(data):
        add_mails = {f"{i}":data_1[str(i)] for i in range(len(data)+1,len(data_1)+1,1)}
        with open(file_path,'w') as file:
            data.update(add_mails)
            file.write(json.dumps(data))"""
    return add_mails,remove_mails

"""def D3_get_mes_id(data_mail):
    tmp=data_mail
    lines=tmp.split('\r\n',3)
    for line in lines:
        if not "Message-ID:" in line:
            continue
        else :
            return line.split()[1][1:-1]"""


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
            if (check == True):
                return filters[i]['filter_dir']
    return data.inbox_dir


def D3_save_mails(email_info, data_mail, mes_id, filters):
    dir = D1_filter_mail(filters, email_info)
    if not os.path.exists(dir):
        os.makedirs(dir)
    #write file.msg
    file_path=os.path.join(dir,f"{mes_id}.msg")
    with open(file_path, 'w') as msg_file:
        msg_file.write(data_mail)

    """with open(file_path,'r') as msg_file:
        data = msg_file.read()
    print(data)"""

def D3_extract(str_1,str_2,part):
    if str_1 in part:
        return part.split(str_1,1)[1].split(str_2,1)[0].strip('"')
    else: return ' '
def D3_extract_headers(headers,string):
    data={}
    str_2=string
    data['From']=D3_extract("From: ",str_2,headers)
    data['To']=D3_extract("To: ",str_2,headers)
    data['Cc']=D3_extract("Cc: ",str_2,headers)
    data['Subject']=D3_extract("Subject: ",str_2,headers)
    data['Boundary']=D3_extract("Content-Type: multipart/mixed; boundary=",str_2,headers)
    return data

def D3_extract_body(parts,boundary,string):
    content=" "
    list_attachments=[]
    for part in parts[1:-1]:
        if "Content-Disposition: attachment" in part:
            attachment={
                'Content-Type': D3_extract('Content-Type: ',";",part),
                'filename':D3_extract("filename=",string,part),
                'content':D3_extract(string+string,string+string,part).encode('utf-8')
            }
            list_attachments.append(attachment)
        else:
            content=D3_extract(string+string,"--"+boundary,part).strip(string+string)
    return content,list_attachments

def D3_parse_mime_email(raw_email,string):
    email_info={}
    # Parsing email into head and bodys
    headers, body = raw_email.split(string+string, 1)
    email_info['Headers']= D3_extract_headers(headers,string)

    boundary= email_info['Headers']['Boundary']
    if boundary!= " ":
        parts = body.split('--' + boundary)
        """#test
        for part in parts[1:-1]:
            print(part,end="\r\n")
        for i in range(0,len(parts)):
            print(i,parts[i],sep="---",end="\r\n")
        lines=parts[1].split("\r\n")
        for i in range(0,len(lines)):
            print(i,lines[i],sep="---",end="\r\n")"""
        email_info['Text'],email_info['Attachments'] = D3_extract_body(parts,boundary,string)
    else:
        email_info['Text']= body
        email_info['Attachments']=[]
    return email_info


def D3_save_attachments(list_attachments, mes_id):
    if not os.path.exists(data.files_dir):
        os.makedirs(data.files_dir)
    for attachment in list_attachments:
        filename = mes_id + '_' + attachment['filename']
        file_path = os.path.join(data.files_dir, filename)
        #if os.path.exists(file_path): return
        with open(file_path, 'wb') as file:
            _dat=attachment['content'].replace(b'\r\n',b' ')
            decoded_dat = base64.b64decode(_dat)
            file.write(decoded_dat)


def D3_delete_on_client(mes_id):
    #Move mes_<id>.msg
    Bin="Bin"
    if not os.path.exists(Bin):
        os.makedirs(Bin)
    source=save_to_folder+f"//mess_{mes_id}.msg"
    destination=Bin
    if not os.path.exists(Bin+f"//mess_{mes_id}.msg"):
        dest=shutil.move(source,destination)
    #update uidl_list
    path_uidl="uidl_list.json"
    data={}
    with open(path_uidl,'r') as file:
        data=json.loads(file.read())
    for key,value in data.items():
        if(value ==f"{mes_id}.msg"):
            key_remove=key
    del data[str(key_remove)]
    with open(path_uidl,'w') as file:
        file.write(json.dumps(data))

#if delete on interface user call this function
def D3_delete_on_server(sock,remove_mails):
    for key in remove_mails.keys():
        response=D3_send_command(sock,f"DELE {key}")

def D3_fetch_mail(sock,add_mails):
    # Read raw mail
    for key, value in add_mails.items():
        raw_email = D3_send_command(sock, f"RETR {key}",b'\r\n.\r\n').decode('utf-8')
        #print(raw_email)
        email_info=D3_parse_mime_email(raw_email,"\r\n")
        if email_info['Attachments'] !=[]:
            D3_save_attachments(email_info['Attachments'], value[0:-4])
        D3_save_mails(email_info, raw_email, value[0:-4], data.filters)


def D3_reload_mails(pop3_server,pop3_port,username,password):
    with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as sock:
        sock.settimeout(1)
        try:
            sock.connect((pop3_server,pop3_port))
        except:
            return
        D3_receive_data(sock)
        D3_send_command(sock,"CAPA")
        D3_send_command(sock,f"USER {username}")
        D3_send_command(sock,f"PASS {password}")

        #Stat: get the number of emails and their total size
        response=D3_send_command(sock,"STAT")
        num_emails, total_size = map(int, response.split()[1:3])

        #LIST: get list of mails and their size
        #list_mails=map(str,D3_send_command(sock,'LIST').split(b'\r\n')[1:-2])
        list_mails_bytes = D3_send_command(sock,"LIST").decode('utf-8')
        data = D3_list_to_dict(list_mails_bytes)
        D3_save_list(data,"list_bytes.json")

        #UIDL: get a list of unique identifiers assigned by the server to each message
        list_UIDL = D3_send_command(sock,"UIDL").decode('utf-8')
        data_1 = D3_list_to_dict(list_UIDL)
        add_mails = {}
        remove_mails={}

        """D3_delete_on_client(20231203001421330)
        D3_delete_on_client(20231202214856204)"""
        if not os.path.exists("uidl_list.json"):
            add_mails=data_1
        else:
            add_mails,remove_mails=D3_compare_UIDL(data_1)

        #D3_delete_on_server(sock,remove_mails)
        D3_save_list(data_1, "uidl_list.json")#update fie_uidl
        D3_fetch_mail(sock,add_mails)

        #raw_mail=D3_send_command(sock,"RETR 15",b'\r\n.\r\n').decode('utf-8')
        raw_data=" "
        # thay doi cai ma ngay dong duoi thanh ma mail bat ki trong may roi test nha
        """with open(save_to_folder+"//mess_20231204230258134.msg",'r')as file:
            raw_data=file.read()
        #print(raw_data)
        raw_data=raw_data.split("\n\n",1)[1].split(".\n\n\n\n")[0]
        print(raw_data)
        file_path=os.path.join(save_to_folder+"test.msg")
        with open(file_path,'w') as file:
            file.write(raw_data)
        with open(file_path,'r') as file:
            _data=file.read()
        for line in lines:
            print("dong",line,sep="----",end="\n\n")
        email_info=D3_parse_mime_email(_data,"\n\n")
        #D3_save_attachments(email_info['Attachments'])
        print(email_info)"""



"""app = QApplication(sys.argv)
read_mail = ReadMail()
read_mail.show()
app.exec()"""





