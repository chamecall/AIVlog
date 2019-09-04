import sys
import scipy.io as sio
from PyQt5 import QtWidgets, QtCore
import cv2
from PyQt5.QtCore import QDir, Qt, QUrl
from PyQt5.QtWidgets import (QApplication, QFileDialog, QHBoxLayout, QVBoxLayout, QLabel,
                             QPushButton, QSizePolicy, QSlider, QStyle, QVBoxLayout, QWidget)
from PyQt5 import QtGui
from AIVlog import AIVlog


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, screen_size: tuple):
        super(MainWindow, self).__init__()

        #self.showFullScreen()
        self.setWindowTitle("AIVlog")
        #self.setStyleSheet("background-color: #eeeeee; color: black; ")
        self.aivlog = AIVlog(self, screen_size)

        self.quit_action = QtWidgets.QAction("&Exit", self)
        self.quit_action.setShortcut("Ctrl+Q")
        self.quit_action.setStatusTip('Close The App')
        self.quit_action.triggered.connect(self.closeApplication)

        self.open_video_file = QtWidgets.QAction("&Open Video File", self)
        self.open_video_file.setShortcut("Ctrl+Shift+V")
        self.open_video_file.setStatusTip('Open .h264 File')
        self.open_video_file.triggered.connect(self.aivlog.load_video_file)

        self.save_project_as = QtWidgets.QAction('Save project as', self)
        self.save_project_as.triggered.connect(self.aivlog.save_as)

        self.open_project_from_db = QtWidgets.QAction('Open project', self)
        self.open_project_from_db.triggered.connect(self.aivlog.open_project_from_db)

        self.save_project = QtWidgets.QAction('Save project', self)
        self.save_project.triggered.connect(self.aivlog.save)

        self.mainMenu = self.menuBar()
        self.file_menu = self.mainMenu.addMenu('&File')
        self.file_menu.addAction(self.open_video_file)
        self.file_menu.addAction(self.open_project_from_db)
        self.file_menu.addAction(self.save_project)
        self.file_menu.addAction(self.save_project_as)
        self.file_menu.addAction(self.quit_action)

        self.setCentralWidget(self.aivlog)

    def closeApplication(self):
        choice = QtWidgets.QMessageBox.question(self, 'Message', 'Do you really want to exit?',
                                                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if choice == QtWidgets.QMessageBox.Yes:
            print("Closing....")
            self.aivlog.close()
            sys.exit()
        else:
            pass


