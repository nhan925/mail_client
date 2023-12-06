import read_mail


with open('sent/20231206163122.msg', 'r') as file:
    dat = file.read()
    data = read_mail.D3_parse_mime_email(dat, '\n')
    print(data)
