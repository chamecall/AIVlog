from PyQt5 import QtWidgets, QtCore, QtGui
from CustomWidget import CustomWidget
from Utils import remove_item_from_list

class AssignmentList(QtWidgets.QListWidget):
    item_return = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super(AssignmentList, self).__init__(parent)
        self.setStyleSheet(
            ' QListWidget::item:hover { background-color: #e0e0e0;} QListWidget::item { padding: 5px; border: 1px solid gray;}'
            'QListWidget::item:selected { background-color: aqua; color: black}')

    def add_assignment(self, detection, label):
        item = QtWidgets.QListWidgetItem(self)
        item_widget = CustomWidget(f'{label} - {detection}', 'Delete the assignment')
        item.setSizeHint(item_widget.sizeHint())

        item_widget.button.clicked.connect(lambda checked, l=self, it=item: self.remove_item(l, item))
        self.setItemWidget(item, item_widget)

    def remove_item(self, list_widget, item):
        detection_num = self.itemWidget(item).label.text().split()[0]
        remove_item_from_list(list_widget, item)
        self.item_return.emit(detection_num)