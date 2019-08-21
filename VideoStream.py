import scipy.io as sio
from PyQt5 import QtWidgets, QtCore
import cv2
from PyQt5.QtCore import QDir, Qt, QUrl
from PyQt5.QtWidgets import (QApplication, QFileDialog, QHBoxLayout, QVBoxLayout, QLabel,
                             QPushButton, QSizePolicy, QSlider, QStyle, QVBoxLayout, QWidget)
from PyQt5 import QtGui
import numpy as np


class VideoStream(QtWidgets.QWidget):
    pix_signal = QtCore.pyqtSignal(QtGui.QPixmap)

    def __init__(self, filename):
        super(QtWidgets.QWidget, self).__init__()
        self.cap = cv2.VideoCapture(filename)
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
            pix = self.image_from_np_to_pix(frame)
            self.pix_signal.emit(pix)

    @staticmethod
    def image_from_np_to_pix(frame: np.ndarray):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, (600, 400), interpolation=cv2.INTER_AREA)
        img = QtGui.QImage(frame, frame.shape[1], frame.shape[0], QtGui.QImage.Format_RGB888)
        pix = QtGui.QPixmap.fromImage(img)
        return pix

    def set_position(self, position):
        print(position)
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
            pix = self.image_from_np_to_pix(frame)
            return pix
