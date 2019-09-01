from PyQt5.QtWidgets import (QWidget, QLabel,
    QComboBox, QApplication)
from PyQt5 import QtWidgets, QtCore, QtGui
from CategoryList import CategoryList

class CategorySection(QtWidgets.QWidget):
    category_changing = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super(CategorySection, self).__init__(parent)
        self.vbox = QtWidgets.QVBoxLayout(self)
        self.setStyleSheet(
            'QListWidget::item:hover { background-color: #e0e0e0;} QListWidget::item { padding: 5px; border: 1px solid gray;}'
            'QListWidget::item:selected { background-color: aqua; color: black}')
        self.combo_box = QComboBox(self)
        self.category_list = CategoryList(self)
        self.vbox.addWidget(self.combo_box)
        self.vbox.addWidget(self.category_list)
        self.combo_box.currentIndexChanged.connect(self.current_index_changed)

    def add_label(self, label: str):
        self.combo_box.addItem(label)

    def current_index_changed(self, index):
        print('current text is', str(self.combo_box.currentText()))
        self.category_changing.emit(str(self.combo_box.currentText()))

    def check_cur_item_by_label(self, user_label):
        return str(self.combo_box.currentText()) == user_label

    def get_current_index(self):
        return str(self.combo_box.currentIndex())

    def del_item_by_text(self, text):
        index = self.combo_box.findText(text)
        self.combo_box.removeItem(index)

