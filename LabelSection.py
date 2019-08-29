from PyQt5 import QtWidgets, QtCore, QtGui
from LabelList import LabelList
from SelfRemovingWidget import SelfRemovingWidget
from Utils import remove_item_from_list

class LabelSection(QtWidgets.QWidget):
    label_creating = QtCore.pyqtSignal(str)
    label_removing = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super(LabelSection, self).__init__(parent)

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
        item = QtWidgets.QListWidgetItem(self.dropped_list_box)
        item_widget = SelfRemovingWidget(label, 'Delete the label')
        item.setSizeHint(item_widget.sizeHint())
        item_widget.button.clicked.connect(
            lambda checked, l=self.dropped_list_box, it=item: self.remove_item(l, it))
        self.dropped_list_box.setItemWidget(item, item_widget)
        self.text_box.clear()

        self.label_creating.emit(label)

    def remove_item(self, list_widget, item):
        self.label_removing.emit(list_widget.itemWidget(item).label.text())
        remove_item_from_list(list_widget, item)
