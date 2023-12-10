import json
import os
import read_mail

username = ''
password = ''
smtp_server = ''
smtp_port = 25
pop3_server = ''
pop3_port = 110
auto_load_time = 10
inbox_dir = 'inbox'
sent_dir = 'sent'
spam_dir = 'spam'
trash_dir = 'trash'
filters = {}
files_dir = 'downloaded_files'
mail_status = {}
check_reset = 0


def import_config():
    with open('config.json', 'r') as config_file:
        config_dat = json.load(config_file)
        config_file.close()
    global username
    username = config_dat['username']
    global password
    password = config_dat['password']
    global smtp_server
    smtp_server = config_dat['smtp_server']
    global smtp_port
    smtp_port = config_dat['smtp_port']
    global pop3_server
    pop3_server = config_dat['pop3_server']
    global pop3_port
    pop3_port = config_dat['pop3_port']
    global auto_load_time
    auto_load_time = config_dat['auto_load_time']
    global filters
    filters = config_dat['filter']


def export_config():
    dat = {'username': username, 'password': password, 'smtp_server': smtp_server, 'smtp_port': smtp_port,
           'pop3_server': pop3_server, 'pop3_port': pop3_port, 'auto_load_time': auto_load_time, 'filter': filters}
    with open('config.json', 'w') as config_file:
        json.dump(dat, config_file, indent=2)
        config_file.close()


def uidl_list_export():
    global mail_status
    with open('uidl_list.json', 'w') as file:
        json.dump(mail_status, file, indent=2)
        file.close()


def uidl_list_import():
    global mail_status
    if os.path.exists("uidl_list.json"):
        mail_status = read_mail.D3_read_json_file("uidl_list.json")
