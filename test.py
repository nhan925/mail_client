import socket
import base64
import json
import os, shutil

def D3_receive_data(sock,s_condition=b'\r\n'):
    data = b""
    while True:
        chunk = sock.recv(1024)
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
    if not os.path.exists(mail_folder):
        os.makedirs(mail_folder)
    #write .json
    file_path = os.path.join(mail_folder, filename)
    with open(file_path,'w') as json_file:
        json.dump(data, json_file, indent=2)

    """with open(file_path,'r') as json_file:
        data = json.loads(json_file.read())
    for i in range(1,len(list_mails)+1):
        print(data[str(i)],end='\r\n')"""

def D3_read_json_file(file_path):
    with open(file_path,'r') as json_file:
        data=json.load(json_file)
    return data

def D3_compare_UIDL(data_1):
    file_path=mail_folder+"//uidl_list.json"
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
            if os.path.exists(mail_folder+f"//Bin//mess_{value[0:-4]}.msg"):
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

def D3_save_mails(data_mail,mes_id):
    if not os.path.exists(save_to_folder):
        os.makedirs(save_to_folder)
    #write file.msg
    file_path=os.path.join(save_to_folder,f"mess_{mes_id}.msg")
    with open(file_path,'w') as msg_file:
        msg_file.write(data_mail)

    """with open(file_path,'r') as msg_file:
        data = msg_file.read()
    print(data)"""

def D3_extract(str_1,str_2,part):
    if str_1 in part:
        return part.split(str_1,1)[1].split(str_2,1)[0].strip('"')
    else:
        return ' '
def D3_extract_headers(headers):
    data={}
    """data['From']=headers.split('From: ')[1].split('\r\n',1)[0]
    if 'To: ' in headers:
        data['To']=headers.split('To: ')[1].split('\r\n',1)[0]
    else : data['To']=" "
    if 'Cc: ' in headers:
        data['Cc']=headers.split('Cc: ')[1].split('\r\n',1)[0]
    else: data['Cc']=" "
    if 'Subject' in headers:
        data['Subject']=headers.split('Cc: ')[1].split('\r\n',1)[0]
    else: data['Subject']=" " """
    str_2="\r\n"
    data['From']=D3_extract("From: ",str_2,headers)
    data['To']=D3_extract("To: ",str_2,headers)
    data['Cc']=D3_extract("Cc: ",str_2,headers)
    data['Subject']=D3_extract("Subject: ",str_2,headers)
    data['Boundary']=D3_extract("Content-Type: multipart/mixed; boundary=",str_2,headers)
    return data

def D3_extract_body(parts,boundary):
    list_text=[]
    list_attachments=[]
    for part in parts[1:-1]:
        if "Content-Disposition: attachment" in part:
            attachment={
                'Content-Type': D3_extract('Content-Type: ',";",part),
                'filename':D3_extract("filename=","\r\n",part),
                'content':D3_extract("\r\n\r\n","\r\n\r\n",part).encode('utf-8')
            }
            list_attachments.append(attachment)
        else:
            content=D3_extract("\r\n\r\n","--"+boundary,part).strip("\r\n\r\n")
            list_text.append(content)
    return list_text,list_attachments

def D3_parse_mime_email(raw_email):
    email_info={}
    # Parsing email into head and bodys
    headers, body = raw_email.split('\r\n\r\n', 1)
    email_info['Headers']= D3_extract_headers(headers)

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
        email_info['Text'],email_info['Attachments'] = D3_extract_body(parts,boundary)
    else:
        list_text=[]
        list_text.append(body)
        email_info['Text']= list_text
        email_info['Attachments']=[]
    return email_info


def D3_save_attachments(list_attachments):
    if not os.path.exists(file_attachments):
        os.makedirs(file_attachments)
    for attachment in list_attachments:
        filename = attachment['filename']
        #file_path = os.path.join(file_attachments, filename)
        """with open(file_attachments + '/' + filename, 'wb') as file:
            _dat=attachment['content'].replace(b'\r\n', b'')
            decoded_dat = base64.b64decode(_dat)
            file.write(decoded_dat)"""


def D3_delete_on_client(mes_id):
    #Move mes_<id>.msg
    Bin=mail_folder+"//Bin"
    if not os.path.exists(Bin):
        os.makedirs(Bin)
    source=save_to_folder+f"//mess_{mes_id}.msg"
    destination=Bin
    if not os.path.exists(Bin+f"//mess_{mes_id}.msg"):
        dest=shutil.move(source,destination)
    #update uidl_list
    path_uidl=mail_folder+"//uidl_list.json"
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
    for key in add_mails:
        raw_email = D3_send_command(sock, f"RETR {key}",b'\r\n.\r\n').decode('utf-8')
        #print(raw_email)
        email_info=D3_parse_mime_email(raw_email)
        if email_info['Attachments'] != []:
            D3_save_attachments(email_info['Attachments'])
        D3_save_mails(raw_email, add_mails[key][0:-4])


def D3_reload_mails(pop3_server,pop3_port,username,password):
    with socket.create_connection((pop3_server,pop3_port)) as sock:
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
        D3_save_list(data,"List_bytes.json")

        #UIDL: get a list of unique identifiers assigned by the server to each message
        list_UIDL = D3_send_command(sock,"UIDL").decode('utf-8')
        data_1 = D3_list_to_dict(list_UIDL)
        add_mails={}
        remove_mails={}
        #D3_delete_on_client(20231203001421330)
        #D3_delete_on_client(20231202214856204)
        if not os.path.exists(mail_folder+"//uidl_list.json"):
            add_mails=data_1
        else:
            add_mails,remove_mails=D3_compare_UIDL(data_1)

        D3_delete_on_server(sock,remove_mails)
        D3_save_list(data_1, "uidl_list.json")#update fie_uidl
        D3_fetch_mail(sock,add_mails)

        """"#raw_mail=D3_send_command(sock,"RETR 15",b'\r\n.\r\n').decode('utf-8')
        raw_data=" "
        with open(save_to_folder+"//mess_20231204213644283.msg",'r')as file:
            raw_data=file.read()
        #print(raw_data)
        lines=raw_data.split("\r\n")
        print(lines)
        for line in lines:
            print("dong",line,sep="----",end="\n\n")
        email_info=D3_parse_mime_email(raw_data)
        #D3_save_attachments(email_info['Attachments'])
        print(email_info)"""




if __name__ == "__main__":
    pop3_server = "127.0.0.1"
    pop3_port="110"
    username = "newmail@new.com"
    password = "123456"
    save_to_folder="debug/mailbox"
    file_attachments="debug/file_attachments"
    mail_folder="debug/client_socket"


D3_reload_mails(pop3_server,pop3_port,username, password)





