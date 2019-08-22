from PyQt5 import QtWidgets, QtCore
import cv2
from PyQt5.QtCore import QDir, Qt, QUrl
from PyQt5.QtWidgets import (QApplication, QFileDialog, QHBoxLayout, QVBoxLayout, QLabel,
                             QPushButton, QSizePolicy, QSlider, QStyle, QVBoxLayout, QWidget)
from PyQt5 import QtGui
from VideoStream import VideoStream
from VideoPlayer import VideoPlayer


class MainWidget(QtWidgets.QWidget):
    def __init__(self, parent):
        super(MainWidget, self).__init__(parent)
        self.vbox = QVBoxLayout(self)

        self.video_player = VideoPlayer(self)
        self.vbox.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        self.vbox.addWidget(self.video_player)
        self.setLayout(self.vbox)
        self.video_file_name = None
        self.isVideoFileLoaded = False

    def load_video_file(self):
        self.video_file_name, _ = QFileDialog.getOpenFileName(self, "Open Movie", QDir.homePath())
        if not self.video_file_name == '':
            self.isVideoFileLoaded = True
            self.video_player.set_video_stream(VideoStream(self.video_file_name))

    def close(self):
        self.video_player.reset_video_stream()
