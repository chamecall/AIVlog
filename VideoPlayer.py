import scipy.io as sio
from PyQt5 import QtWidgets, QtCore
import cv2
from PyQt5.QtCore import QDir, Qt, QUrl
from PyQt5.QtWidgets import (QApplication, QFileDialog, QHBoxLayout, QVBoxLayout, QLabel,
                             QPushButton, QSizePolicy, QSlider, QStyle, QVBoxLayout, QWidget)
from PyQt5 import QtGui
from Recognizer import Recognizer
import numpy as np

class VideoPlayer(QtWidgets.QWidget):
    frame_size = (600, 400)


    def __init__(self, parent):
        super(VideoPlayer, self).__init__(parent)
        # cache - {frame_num: detections}
        self.recognizer = None
        self.cache = {}

        self.exitFrame = QtWidgets.QFrame(self)
        self.exitFrame.setStyleSheet("background-color: #888899;")
        self.exitFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.exitFrame.setFrameShadow(QtWidgets.QFrame.Raised)

        self.vbox = QtWidgets.QVBoxLayout(self.exitFrame)
        self.video_frame = QtWidgets.QLabel()
        self.video_frame.setAlignment(Qt.AlignHCenter)

        self.video_stream = None

        self.play_button = QPushButton()
        self.play_button.setEnabled(False)
        self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.play_button.clicked.connect(self.switch_playing)

        self.position_slider = QSlider(Qt.Horizontal)
        self.position_slider.setRange(0, 0)

        self.slider_pressed = False
        self.vbox.addWidget(self.video_frame)

        self.hbox = QHBoxLayout()
        self.hbox.addWidget(self.play_button)
        self.hbox.addWidget(self.position_slider)
        self.vbox.addLayout(self.hbox)
        self.setLayout(QVBoxLayout(self))
        self.layout().addWidget(self.exitFrame)
        self.playing_before_rewind = False
        self.setFixedSize(self.frame_size[0], self.frame_size[1] + 20)

    def set_video_stream(self, video_stream):
        self.video_stream = video_stream
        self.video_stream.pix_signal.connect(self.np_arr_slot)
        self.play_button.setEnabled(True)
        self.position_slider.setRange(1, self.video_stream.frame_count)
        #self.position_slider.valueChanged.connect(self.change_slider_value)
        self.position_slider.sliderPressed.connect(self.press_slider)
        self.position_slider.sliderReleased.connect(self.release_slider)
        #print(self.video_stream.width, self.video_stream.height)
        self.recognizer = Recognizer(self.video_stream.width, self.video_stream.height)
        self.update_frame()

    def update_frame(self):
        self.np_arr_slot(self.video_stream.get_current_frame())


    @staticmethod
    def image_from_np_to_pix(frame: np.ndarray):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, VideoPlayer.frame_size, interpolation=cv2.INTER_AREA)
        img = QtGui.QImage(frame, frame.shape[1], frame.shape[0], QtGui.QImage.Format_RGB888)
        pix = QtGui.QPixmap.fromImage(img)
        return pix

    def np_arr_slot(self, np_arr_frame):
        if np_arr_frame is None:
            return

        proccessed_frame = self.recognizer.forward(np_arr_frame)
        pix = self.image_from_np_to_pix(proccessed_frame)
        self.set_pix(pix)

    def release_slider(self):
        self.slider_pressed = False
        if self.playing_before_rewind:
            self.video_stream.start()
            self.playing_before_rewind = False
        self.video_stream.set_position(self.position_slider.value())
        self.update_frame()

    def press_slider(self):
        self.slider_pressed = True
        if self.video_stream.playing:
            self.video_stream.pause()
            self.playing_before_rewind = True

    def change_slider_value(self):
        if self.slider_pressed:
            self.video_stream.set_position(self.position_slider.value())
            self.update_frame()

    def set_pix(self, pix):
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
        if self.video_stream:
            self.video_stream.stop()
            self.video_stream = None
