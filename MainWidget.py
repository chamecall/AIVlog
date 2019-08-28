from PyQt5 import QtWidgets, QtCore
import cv2
from PyQt5.QtCore import QDir, Qt, QUrl
from PyQt5.QtWidgets import (QApplication, QFileDialog, QHBoxLayout, QVBoxLayout, QLabel,
                             QPushButton, QSizePolicy, QSlider, QStyle, QVBoxLayout, QWidget)
from DetectionList import DetectionList
from VideoStream import VideoStream
from VideoPlayer import VideoPlayer
from LabelSection import LabelSection
from AssigningList import AssigningList

class MainWidget(QtWidgets.QWidget):
    def __init__(self, parent, screen_size: tuple):
        super(MainWidget, self).__init__(parent)
        self.video_vbox = QVBoxLayout()
        self.detection_list = DetectionList(self)
        self.assigning_list = AssigningList()
        self.label_section = LabelSection()
        self.label_section.dropped_list_box.assigning.connect(self.assigning_list.add_assigning)
        self.label_section.dropped_list_box.assigning.connect(self.detection_list.del_dragged_item)
        self.assigning_list.item_return.connect(self.detection_list.add_item)
        self.list_hbox = QHBoxLayout()
        self.list_hbox.addWidget(self.detection_list)
        self.list_hbox.addWidget(self.label_section)
        self.list_hbox.addWidget(self.assigning_list)

        self.main_vbox = QVBoxLayout(self)
        self.video_player = VideoPlayer(screen_size)
        self.video_player.detection_signal.connect(self.detection_list.set_detections)
        self.video_vbox.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.video_vbox.addWidget(self.video_player)
        self.main_vbox.addLayout(self.video_vbox)
        self.main_vbox.addLayout(self.list_hbox)
        self.main_vbox.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.video_file_name = None
        self.isVideoFileLoaded = False

    def load_video_file(self):
        #self.video_file_name, _ = QFileDialog.getOpenFileName(self, "Open Movie", QDir.homePath())
        self.video_file_name = '/home/algernon/sample.mkv'
        if not self.video_file_name == '':
            self.isVideoFileLoaded = True
            self.video_player.set_video_stream(VideoStream(self.video_file_name))

    def close(self):
        self.video_player.close()
