from PyQt5 import QtWidgets, QtCore, QtGui
from LabelList import LabelList
from SelfRemovingWidget import SelfRemovingWidget
from Utils import remove_item_from_list

class LabelSection(QtWidgets.QWidget):
    label_removing = QtCore.pyqtSignal(str, int)

    def __init__(self, parent=None):
        super(LabelSection, self).__init__(parent)
        self.parent = parent
        vbox = QtWidgets.QVBoxLayout(self)

        hbox = QtWidgets.QHBoxLayout()
        self.text_box = QtWidgets.QLineEdit(self)
        add_button = QtWidgets.QPushButton('Add label')
        add_button.setStyleSheet("* {background-color: green;}")
        add_button.clicked.connect(self.add_entered_label)
        hbox.addWidget(self.text_box, 2)
        hbox.addWidget(add_button, 1)
        vbox.addLayout(hbox)
        self.label_list = LabelList(self)
        vbox.addWidget(self.label_list)

    def add_entered_label(self):
        label = self.text_box.text()
        if label == '':
            return
        index = self.parent.add_label(label)
        if index >= 0:
            self.add_item(label, index)

    def add_item(self, label, index):
        self.text_box.clear()
        item = QtWidgets.QListWidgetItem(self.label_list)
        item_widget = SelfRemovingWidget(label, 'Delete the label', index)
        item.setSizeHint(item_widget.sizeHint())
        item_widget.button.clicked.connect(
            lambda checked, l=self.label_list, it=item: self.remove_item(l, it))
        self.label_list.setItemWidget(item, item_widget)

    def remove_item(self, list_widget, item):
        item_widget = list_widget.itemWidget(item)
        self.label_removing.emit(item_widget.label.text(), item_widget.value)
        remove_item_from_list(list_widget, item)


