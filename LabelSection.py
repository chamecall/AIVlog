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
        add_button.clicked.connect(self.add_label)
        hbox.addWidget(self.text_box, 2)
        hbox.addWidget(add_button, 1)
        vbox.addLayout(hbox)
        self.dropped_list_box = LabelList(self)
        vbox.addWidget(self.dropped_list_box)

    def add_label(self):
        label = self.text_box.text()
        if label == '':
            return
        index = self.parent.add_label(label)
        if index >= 0:
            item = QtWidgets.QListWidgetItem(self.dropped_list_box)
            item_widget = SelfRemovingWidget(label, 'Delete the label', index)
            item.setSizeHint(item_widget.sizeHint())
            item_widget.button.clicked.connect(
                lambda checked, l=self.dropped_list_box, it=item: self.remove_item(l, it))
            self.dropped_list_box.setItemWidget(item, item_widget)
            self.text_box.clear()

    def remove_item(self, list_widget, item):
        item_widget = list_widget.itemWidget(item)
        self.label_removing.emit(item_widget.label.text(), item_widget.value)
        remove_item_from_list(list_widget, item)


