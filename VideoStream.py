import scipy.io as sio
from PyQt5 import QtWidgets, QtCore
import cv2
from PyQt5.QtCore import QDir, Qt, QUrl
from PyQt5.QtWidgets import (QApplication, QFileDialog, QHBoxLayout, QVBoxLayout, QLabel,
                             QPushButton, QSizePolicy, QSlider, QStyle, QVBoxLayout, QWidget)
from PyQt5 import QtGui
import numpy as np


class VideoStream(QtWidgets.QWidget):
    pix_signal = QtCore.pyqtSignal(np.ndarray)

    def __init__(self, filename):
        super(QtWidgets.QWidget, self).__init__()
        self.cap = cv2.VideoCapture(filename)
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.frame_count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.duration = int(self.frame_count / self.fps)

        # frame counting starts from 1
        self.cur_frame_num = 1
        self.set_position(self.cur_frame_num)
        self.playing = False

    def nextFrameSlot(self):
        ret, frame = self.cap.read()
        if ret:
            self.cur_frame_num = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
            self.pix_signal.emit(frame)

    def seek_back(self):
        if not self.cur_frame_num == 1:
            self.set_position(self.cur_frame_num - 1)

    def seek_forward(self):
        if not self.cur_frame_num == self.frame_count:
            self.set_position(self.cur_frame_num + 1)

    def set_position(self, position):
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, position)
        self.cur_frame_num = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))

    def start(self):
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.nextFrameSlot)
        self.timer.start(1000.0 / 30)
        self.playing = True

    def pause(self):
        self.timer.stop()
        self.playing = False

    def stop(self):
        self.cap.release()

    def get_current_frame(self):
        ret, frame = self.cap.read()
        self.set_position(self.cur_frame_num)
        if ret:
            return frame
