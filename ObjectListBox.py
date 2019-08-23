from PyQt5 import QtWidgets, QtCore
import cv2
from PyQt5.QtCore import QDir, Qt, QUrl
from PyQt5.QtWidgets import (QApplication, QFileDialog, QHBoxLayout, QVBoxLayout, QLabel,
                             QPushButton, QSizePolicy, QSlider, QStyle, QVBoxLayout, QWidget)
from PyQt5 import QtGui
from VideoStream import VideoStream
from VideoPlayer import VideoPlayer


class ObjectListBox(QtWidgets.QListWidget):
    def __init__(self, parent):
        super(ObjectListBox, self).__init__(parent)

    def set_detections(self, detections_list):
        self.clear()
        for i, detection in enumerate(detections_list, 1):
            item = QtWidgets.QListWidgetItem(f'{i} - {detection[0]}')
            self.addItem(item)

