from PyQt5 import QtWidgets, QtCore, QtGui
from SelfRemovingWidget import SelfRemovingWidget
from Utils import remove_item_from_list

class AssignmentList(QtWidgets.QListWidget):
    item_removing = QtCore.pyqtSignal(int)

    def __init__(self, parent=None):
        super(AssignmentList, self).__init__(parent)
        self.setStyleSheet(
            ' QListWidget::item:hover { background-color: #e0e0e0;} QListWidget::item { padding: 5px; border: 1px solid gray;}'
            'QListWidget::item:selected { background-color: aqua; color: black}')

    def add_assignment(self, dnn_label, label, box, detection_num):
        item = QtWidgets.QListWidgetItem(self)
        item_widget = SelfRemovingWidget(f'{label} {box} {dnn_label}', 'Delete the assignment', detection_num)
        item.setSizeHint(item_widget.sizeHint())

        item_widget.button.clicked.connect(lambda checked, l=self, it=item: self.remove_item(l, item))
        self.setItemWidget(item, item_widget)

    def remove_item(self, list_widget, item):
        detection_num = self.itemWidget(item).detection_num
        remove_item_from_list(list_widget, item)
        self.item_removing.emit(detection_num)
