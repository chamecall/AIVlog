from PyQt5 import QtWidgets, QtCore, QtGui
from LabelList import LabelList
from CustomWidget import CustomWidget
from Utils import remove_item_from_list

class LabelSection(QtWidgets.QWidget):
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
        item_widget = CustomWidget(label, 'Delete the label')
        item.setSizeHint(item_widget.sizeHint())
        item_widget.button.clicked.connect(
            lambda checked, l=self.dropped_list_box, it=item: remove_item_from_list(l, it))
        self.dropped_list_box.setItemWidget(item, item_widget)
        self.text_box.clear()
