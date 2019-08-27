from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import QPointF

class LabelList(QtWidgets.QListWidget):
    assigning = QtCore.pyqtSignal(list)

    def __init__(self, type, parent=None):
        super(LabelList, self).__init__(parent)
        self.setAcceptDrops(True)
        self.setMouseTracking(True)
        self.setStyleSheet(' QListWidget::item:hover { background-color: #e0e0e0; padding: 0px;} QListWidget::item { padding: 5px; border: 1px solid black;}'
                           'QListWidget::item:selected { background-color: aqua; color: black}')

    def dropEvent(self, event):
        position = QPointF(event.pos()).toPoint()
        selected_item = self.itemAt(position)
        if selected_item:
            parent_list = selected_item.listWidget()
            detection_num = event.mimeData().text()
            label = parent_list.itemWidget(selected_item).label.text()
            self.assigning.emit([label, detection_num])
            event.setDropAction(QtCore.Qt.MoveAction)


