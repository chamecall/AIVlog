from PyQt5.QtWidgets import (QWidget, QLabel,
    QComboBox, QApplication)
from PyQt5 import QtWidgets, QtCore, QtGui
from CategoryList import CategoryList

class CategorySection(QtWidgets.QWidget):
    category_changing = QtCore.pyqtSignal(int)

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

    def add_label(self, label: str, label_index: int):
        self.combo_box.addItem(label, label_index)

    def current_index_changed(self, index):
        user_label_index = self.get_user_data_by_index(index)
        self.category_changing.emit(user_label_index)

    def get_user_data_by_index(self, index):
        model_index = self.combo_box.model().index(index, 0)
        user_label_index = self.combo_box.model().data(model_index, QtCore.Qt.UserRole)
        return user_label_index

    def get_current_index(self):
        return self.currentIndex()

    def del_item_by_text(self, text):
        index = self.category_section.combo_box.findText(text)
        self.category_section.combo_box.removeItem(index)

