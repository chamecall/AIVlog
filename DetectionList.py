from PyQt5 import QtWidgets, QtCore
import cv2
from PyQt5.QtCore import QDir, Qt, QUrl
from PyQt5.QtWidgets import (QApplication, QFileDialog, QHBoxLayout, QVBoxLayout, QLabel,
                             QPushButton, QSizePolicy, QSlider, QStyle, QVBoxLayout, QWidget)
from PyQt5 import QtGui
from VideoStream import VideoStream
from VideoPlayer import VideoPlayer


class DetectionList(QtWidgets.QListWidget):
    def __init__(self, parent):
        super(DetectionList, self).__init__(parent)
        self.dragged_value = None
        self.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
        self.currentItemChanged.connect(self.item_clicked)
        self.setStyleSheet(
            ' QListWidget::item:hover { background-color: #e0e0e0;} QListWidget::item { padding: 5px; border: 1px solid gray;}'
            'QListWidget::item:selected { background-color: aqua; color: black}')

    def item_clicked(self, arg):
        self.dragged_value = arg.text()

    def dragEnterEvent(self, event):
        event.mimeData().setText(self.dragged_value)

    def set_detections(self, detections_list):
        self.clear()
        for i, detection in enumerate(detections_list, 1):
            #item = QtWidgets.QListWidgetItem(f'{i} - {detection[0]}')
            item = QtWidgets.QListWidgetItem(f'{i}')
            self.addItem(item)

