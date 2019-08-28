from PyQt5 import QtWidgets, QtCore, QtGui
from CustomWidget import CustomWidget
from Utils import remove_item_from_list

class AssigningList(QtWidgets.QListWidget):
    item_return = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super(AssigningList, self).__init__(parent)
        self.setStyleSheet(
            ' QListWidget::item:hover { background-color: #e0e0e0;} QListWidget::item { padding: 5px; border: 1px solid gray;}'
            'QListWidget::item:selected { background-color: aqua; color: black}')

    def add_assigning(self, assigning: list):
        def remove_item(list_widget, item):
            detection_num = self.itemWidget(item).label.text().split()[0]
            remove_item_from_list(list_widget, item)
            self.item_return.emit(detection_num)

        item = QtWidgets.QListWidgetItem(self)
        item_widget = CustomWidget(f'{assigning[0]} - {assigning[1]}', 'Delete the assigning')
        item.setSizeHint(item_widget.sizeHint())

        item_widget.button.clicked.connect(lambda checked, l=self, it=item: remove_item(l, item))
        self.setItemWidget(item, item_widget)