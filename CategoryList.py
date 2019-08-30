from PyQt5 import QtWidgets, QtCore, QtGui


class CategoryList(QtWidgets.QListWidget):
    def __init__(self, parent=None):
        super(CategoryList, self).__init__(parent)
        self.setStyleSheet(
            'QListWidget::item:hover { background-color: #e0e0e0;} QListWidget::item { padding: 5px; border: 1px solid gray;}'
            'QListWidget::item:selected { background-color: aqua; color: black}')

    def add_item(self, value):
        self.addItem(value)