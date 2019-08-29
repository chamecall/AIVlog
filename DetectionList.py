from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QUrl
from Utils import format_detection_to_print_out
from DetectionLinkedQListWidgetItem import DetectionLinkedQListWidgetItem


class DetectionList(QtWidgets.QListWidget):
    def __init__(self, parent):
        super(DetectionList, self).__init__(parent)
        self.dragged_item = None
        self.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
        self.currentItemChanged.connect(self.item_clicked)
        self.setStyleSheet(
            ' QListWidget::item:hover { background-color: #e0e0e0;} QListWidget::item { padding: 5px; border: 1px solid gray;}'
            'QListWidget::item:selected { background-color: aqua; color: black}')

    def item_clicked(self, item):
        self.dragged_item = item

    def dragEnterEvent(self, event):
        event.mimeData().setText(self.dragged_item.detection_num)

    def del_dragged_item(self):
        row_num = self.row(self.dragged_item)
        self.takeItem(row_num)

    def set_detections(self, detection_list):
        self.clear()
        for i, detection in enumerate(detection_list):
            detection_str = format_detection_to_print_out(detection)
            self.add_item(i, detection_str)

    def add_item(self, detection_num, item_value):
        item = DetectionLinkedQListWidgetItem(detection_num, item_value)
        self.addItem(item)
        #self.sortItems()

