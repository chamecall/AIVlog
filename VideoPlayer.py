import scipy.io as sio
from PyQt5 import QtWidgets, QtCore
import cv2
from PyQt5.QtCore import QDir, Qt, QUrl
from PyQt5.QtWidgets import (QApplication, QFileDialog, QHBoxLayout, QVBoxLayout, QLabel,
                             QPushButton, QSizePolicy, QSlider, QStyle, QVBoxLayout, QWidget)
from PyQt5 import QtGui


class VideoPlayer(QtWidgets.QWidget):

    def __init__(self, parent):
        super(VideoPlayer, self).__init__(parent)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addStretch(1)
        self.video_frame = QtWidgets.QLabel()
        self.video_stream = None
        self.play_button = QPushButton()
        self.play_button.setEnabled(False)
        self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.play_button.clicked.connect(self.switch_playing)
        self.position_slider = QSlider(Qt.Horizontal)
        self.position_slider.setRange(0, 0)
        self.slider_pressed = False
        self.layout.addWidget(self.video_frame)
        control_layout = QHBoxLayout()
        control_layout.addWidget(self.play_button)
        control_layout.addWidget(self.position_slider)
        self.layout.addLayout(control_layout)
        self.setLayout(self.layout)
        self.playing_before_rewind = False

    def set_video_stream(self, video_stream):
        self.video_stream = video_stream
        self.video_stream.pix_signal.connect(self.pix_slot)
        self.play_button.setEnabled(True)
        self.position_slider.setRange(1, self.video_stream.frame_count)
        self.position_slider.valueChanged.connect(self.change_slider_value)
        self.position_slider.sliderPressed.connect(self.press_slider)
        self.position_slider.sliderReleased.connect(self.release_slider)
        self.update_frame()

    def update_frame(self):
        self.pix_slot(self.video_stream.get_current_frame())


    def release_slider(self):
        self.slider_pressed = False
        if self.playing_before_rewind:
            self.video_stream.start()
            self.playing_before_rewind = False

    def press_slider(self):
        self.slider_pressed = True
        if self.video_stream.playing:
            self.video_stream.pause()
            self.playing_before_rewind = True

    def change_slider_value(self):
        if self.slider_pressed:
            self.video_stream.set_position(self.position_slider.value())
            self.update_frame()

    def pix_slot(self, pix):
        if not pix:
            return
        self.video_frame.setPixmap(pix)
        self.position_slider.setValue(self.video_stream.cur_frame_num)

    def switch_playing(self):
        if self.video_stream.playing:
            self.video_stream.pause()
            self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))


        else:
            self.video_stream.start()
            self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))

    def reset_video_stream(self):
        self.video_stream.stop()
        self.video_stream = None
