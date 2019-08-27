from PyQt5 import QtWidgets, QtCore, QtGui
from CustomWidget import CustomWidget
from Utils import remove_item_from_list

class AssigningList(QtWidgets.QListWidget):
    def __init__(self, parent=None):
        super(AssigningList, self).__init__(parent)
        self.setStyleSheet(
            ' QListWidget::item:hover { background-color: #e0e0e0;} QListWidget::item { padding: 5px; border: 1px solid gray;}'
            'QListWidget::item:selected { background-color: aqua; color: black}')

    def add_assigning(self, assigning: list):
        item = QtWidgets.QListWidgetItem(self)
        item_widget = CustomWidget(f'{assigning[0]} - {assigning[1]}', 'Delete the assigning')
        item.setSizeHint(item_widget.sizeHint())
        item_widget.button.clicked.connect(
            lambda checked, l=self, it=item: remove_item_from_list(l, it))
        self.setItemWidget(item, item_widget)