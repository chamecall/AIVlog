from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import QPointF

class LabelList(QtWidgets.QListWidget):
    assigning = QtCore.pyqtSignal(str, int, int)

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
            detection_num = event.mimeData().text()
            selected_widget = self.itemWidget(selected_item)
            label = selected_widget.label.text()
            label_num = selected_widget.value
            event.setDropAction(QtCore.Qt.MoveAction)
            if detection_num == '':
                return
            else:
                self.assigning.emit(label, label_num, int(detection_num))


