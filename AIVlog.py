from PyQt5 import QtWidgets, QtCore
import cv2
from PyQt5.QtCore import QDir, Qt, QUrl
from PyQt5.QtWidgets import (QApplication, QFileDialog, QHBoxLayout, QVBoxLayout, QLabel,
                             QPushButton, QSizePolicy, QSlider, QStyle, QVBoxLayout, QWidget)
from DetectionList import DetectionList
from VideoStream import VideoStream
from VideoPlayer import VideoPlayer
from LabelSection import LabelSection
from AssignmentList import AssignmentList
from Cache import Cache
from Utils import format_detections_to_print_out

class AIVlog(QtWidgets.QWidget):
    def __init__(self, parent, screen_size: tuple):
        super(AIVlog, self).__init__(parent)
        self.video_vbox = QVBoxLayout()
        self.detection_list = DetectionList(self)
        self.assignment_list = AssignmentList()
        self.label_section = LabelSection()

        self.label_section.dropped_list_box.assigning.connect(self.assign_label)
        self.label_section.label_creating.connect(self.save_label_to_cache)
        self.label_section.label_removing.connect(self.del_label_from_cache)

        self.assignment_list.item_return.connect(self.detection_list.add_item)
        self.list_hbox = QHBoxLayout()
        self.list_hbox.addWidget(self.detection_list)
        self.list_hbox.addWidget(self.label_section)
        self.list_hbox.addWidget(self.assignment_list)

        self.cache = Cache()

        self.main_vbox = QVBoxLayout(self)
        self.video_player = VideoPlayer(screen_size)
        self.video_player.detection_signal.connect(self.save_detections_to_cache)

        self.video_vbox.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.video_vbox.addWidget(self.video_player)
        self.main_vbox.addLayout(self.video_vbox)
        self.main_vbox.addLayout(self.list_hbox)
        self.main_vbox.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.video_file_name = None
        self.isVideoFileLoaded = False

    def assign_label(self, detection, label):
        self.assignment_list.add_assignment(detection, label)
        self.detection_list.del_dragged_item()
        self.del_unused_detection_from_cache(detection)
        self.save_assignment_to_cache()

    def save_assignment_to_cache(self, label, detection_box):
        pass

    def save_detections_to_cache(self, frame_num, detections):
        self.detection_list.set_detections(detections)
        self.cache.all_detections[frame_num] = detections
        self.cache.unused_detections[frame_num] = format_detections_to_print_out(detections)
        print(self.cache.unused_detections)


    def save_label_to_cache(self, label):
        self.cache.labels.append(label)

    def del_label_from_cache(self, label):
        self.cache.labels.remove(label)

    def del_unused_detection_from_cache(self, detection):
        cur_frame_num = self.get_cur_frame_num()
        self.cache.unused_detections[cur_frame_num].remove(detection)


    def load_video_file(self):
        #self.video_file_name, _ = QFileDialog.getOpenFileName(self, "Open Movie", QDir.homePath())
        self.video_file_name = '/home/algernon/sample.mkv'
        if not self.video_file_name == '':
            self.isVideoFileLoaded = True
            self.video_player.set_video_stream(VideoStream(self.video_file_name))

    def close(self):
        self.video_player.close()

    def get_cur_frame_num(self):
        return self.video_player.video_stream.cur_frame_num