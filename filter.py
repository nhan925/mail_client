from PyQt6 import QtCore, QtWidgets, QtGui, uic
from PyQt6.QtWidgets import *

class Filters(QDialog):
    def __init__(self):
        super(Filters, self).__init__()
        uic.loadUi('filter.ui', self)