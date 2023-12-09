import os.path
from PyQt6.QtGui import QFont, QIcon
from PyQt6 import uic
from PyQt6.QtWidgets import *
import data


class Filters(QDialog):
    def __init__(self, main_windows):
        super(Filters, self).__init__()
        uic.loadUi('filter.ui', self)
        self.main_window = main_windows
        self.addbutton.clicked.connect(self.create_filter)

    def create_filter(self):
        filter_name = self.filtername.text()
        filter_by = self.by.currentText()
        filter_keywords = self.keyword.text()
        if (not filter_name) or (not filter_keywords):
            QMessageBox.information(self, 'Filter', 'Fail !')
            return
        filter_keywords_list = filter_keywords.split(',')
        filter_keywords_list = [tok.strip().lower() for tok in filter_keywords_list]
        if not os.path.exists(filter_name):
            os.makedirs(filter_name.lower())
        else:
            QMessageBox.information(self, 'Filter', 'Filter already exists !')
            return
        filter_dict = {'filter_by': filter_by.lower(), 'keywords': filter_keywords_list,
                       'filter_dir': filter_name.lower()}
        data.filters[filter_name] = filter_dict
        item = QListWidgetItem(QIcon('icon/folder.png'), filter_name.capitalize())
        font = QFont('Segoe UI', 11, QFont.Weight.Bold)
        item.setFont(font)
        self.main_window.filterlist.addItem(item)
        self.close()
