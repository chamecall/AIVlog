from PyQt5 import QtWidgets, QtCore
import cv2
from PyQt5.QtCore import QDir, Qt, QUrl
from PyQt5.QtWidgets import (QApplication, QFileDialog, QHBoxLayout, QVBoxLayout, QLabel,
                             QPushButton, QSizePolicy, QSlider, QStyle, QVBoxLayout, QWidget)
from ObjectListBox import ObjectListBox
from VideoStream import VideoStream
from VideoPlayer import VideoPlayer


class MainWidget(QtWidgets.QWidget):
    def __init__(self, parent, screen_size: tuple):
        super(MainWidget, self).__init__(parent)
        self.video_vbox = QVBoxLayout()
        self.list_hbox = QHBoxLayout()
        self.object_list_box = ObjectListBox(self)
        self.list_hbox.addWidget(self.object_list_box)
        self.main_vbox = QVBoxLayout(self)
        self.video_player = VideoPlayer(screen_size)
        self.video_player.detection_signal.connect(self.object_list_box.set_detections)
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
        self.video_player.reset_video_stream()
