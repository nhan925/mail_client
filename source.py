import data
import main
import new_mail
import setup
from PyQt6.QtWidgets import *
import sys

data.import_config()
app = QApplication(sys.argv)
startup = None
if data.username == '':
    startup = setup.Setup()
else:
    startup = main.Main()
startup.show()
app.exec()
data.export_config()