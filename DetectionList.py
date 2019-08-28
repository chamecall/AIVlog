from PyQt5 import QtWidgets, QtCore


class DetectionList(QtWidgets.QListWidget):
    def __init__(self, parent):
        super(DetectionList, self).__init__(parent)
        self.dragged_value = None
        self.dragged_item = None
        self.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
        self.currentItemChanged.connect(self.item_clicked)
        self.setStyleSheet(
            ' QListWidget::item:hover { background-color: #e0e0e0;} QListWidget::item { padding: 5px; border: 1px solid gray;}'
            'QListWidget::item:selected { background-color: aqua; color: black}')

    def item_clicked(self, item):
        self.dragged_item = item

    def dragEnterEvent(self, event):
        event.mimeData().setText(self.dragged_item.text())

    def del_dragged_item(self):
        row_num = self.row(self.dragged_item)
        self.takeItem(row_num)

    def set_detections(self, detections_list):
        self.clear()
        for i, detection in enumerate(detections_list, 1):
            self.add_item(str(i))

    def add_item(self, item_value):
        item = QtWidgets.QListWidgetItem(item_value)
        self.addItem(item)
        self.sortItems()

