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
from CategorySection import CategorySection
from Utils import format_detection_to_print_out, extract_detection_data


class AIVlog(QtWidgets.QWidget):
    def __init__(self, parent, screen_size: tuple):
        super(AIVlog, self).__init__(parent)
        self.top_hbox = QHBoxLayout()
        self.detection_list = DetectionList(self)
        self.assignment_list = AssignmentList()
        self.label_section = LabelSection(self)

        self.label_section.dropped_list_box.assigning.connect(self.assign_label)
        self.label_section.label_removing.connect(self.del_label_from_cache)

        self.assignment_list.item_removing.connect(self.del_assignment_by_detection_num)
        self.list_hbox = QHBoxLayout()
        self.list_hbox.addWidget(self.detection_list)
        self.list_hbox.addWidget(self.label_section)
        self.list_hbox.addWidget(self.assignment_list)

        self.cache = Cache()
        self.main_vbox = QVBoxLayout(self)
        self.video_player = VideoPlayer(self.cache, screen_size)
        self.video_player.detection_signal.connect(self.save_detections_to_cache)
        self.video_player.cache_signal.connect(self.extract_data_from_cache)

        self.category_section = CategorySection(self)
        self.category_section.category_changing.connect(self.change_category)

        self.top_hbox.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.top_hbox.addWidget(self.video_player)
        self.top_hbox.addWidget(self.category_section)
        self.main_vbox.addLayout(self.top_hbox)
        self.main_vbox.addLayout(self.list_hbox)
        self.main_vbox.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.video_file_name = None
        self.isVideoFileLoaded = False

    def change_category(self, user_label_index):
        self.category_section.category_list.clear()
        assignments = self.get_data_by_label(user_label_index)
        data = self.get_category_data_from_cach_by_specified_data(assignments)
        self.update_category_list(data)

    def update_category_list(self, data):
        for frame_num, bouding_box, dnn_label in data:
            self.category_section.category_list.add_item(f'{frame_num}\t{bouding_box}\t{dnn_label}')

    def get_category_data_from_cach_by_specified_data(self, assignments):
        # return list of items of the following form: (frame_num, bounding_box, dnn_label)
        ret_list = []
        for frame_num, _, detection_num in assignments:
            dnn_label, box = extract_detection_data(self.cache.all_detections[frame_num][detection_num])
            ret_list.append([frame_num, box, dnn_label])
        return ret_list



    def get_data_by_label(self, user_label_index):
        # return list of items of the following form: (frame_num, assignment_num_on_this_frame, detection_num_on_this_frame)
        ret_data = []
        for frame_num, assignments in self.cache.assignments.items():
            for i, assignment in enumerate(assignments):
                if assignment[1] == user_label_index:
                    ret_data.append([frame_num, i, assignment[0]])
        return ret_data

    def del_assignment_by_detection_num(self, detection_num):
        cur_frame_num = self.get_cur_frame_num()
        detection_str = format_detection_to_print_out(self.cache.all_detections[cur_frame_num][detection_num])
        self.detection_list.add_item(detection_num, detection_str)
        self.cache.unused_detections[cur_frame_num].append(detection_num)
        self.del_assignment_from_cache(detection_num, cur_frame_num)

    def assign_label(self, user_label_num, detection_num):
        cur_frame_num = self.get_cur_frame_num()
        dnn_label, box = extract_detection_data(self.cache.all_detections[cur_frame_num][detection_num])
        self.save_assignment_to_cache(detection_num, user_label_num)
        user_label = self.cache.labels[user_label_num]
        self.assignment_list.add_assignment(dnn_label, user_label, box, detection_num)

        self.detection_list.del_dragged_item()
        self.del_unused_detection_from_cache(detection_num)
        self.change_category(user_label_num)


    def save_assignment_to_cache(self, detection_num, label):
        cur_frame_num = self.get_cur_frame_num()
        self.cache.assignments[cur_frame_num].append([detection_num, label])

    def del_assignment_from_cache(self, detection_num, cur_frame_num):
        indices = [i for i, assignment in enumerate(self.cache.assignments[cur_frame_num]) if
                   assignment[0] == detection_num]
        assert len(indices) == 1
        assignment_num_to_del = indices[0]
        del self.cache.assignments[cur_frame_num][assignment_num_to_del]

    def save_detections_to_cache(self, frame_num, detections):
        self.detection_list.set_detections(detections)
        self.cache.all_detections[frame_num] = detections
        self.cache.unused_detections[frame_num] = list(range(len(detections)))
        self.cache.assignments[frame_num] = []
        self.assignment_list.clear()

    def extract_data_from_cache(self):
        cur_frame_num = self.get_cur_frame_num()
        detections = [self.cache.all_detections[cur_frame_num][unused_detection_num] for unused_detection_num in self.cache.unused_detections[cur_frame_num]]
        self.detection_list.set_detections(detections)
        self.upload_data_from_cache_to_assignment_list(cur_frame_num)

    def upload_data_from_cache_to_assignment_list(self, cur_frame_num):
        self.assignment_list.clear()
        assignments = self.cache.assignments[cur_frame_num]
        frame_detections = self.cache.all_detections[cur_frame_num]
        for detection_num, user_label in assignments:
            dnn_label, box = extract_detection_data(frame_detections[detection_num])
            self.assignment_list.add_assignment(dnn_label, user_label, box, detection_num)

    def add_label(self, label):
        self.cache.labels.append(label)
        label_index = len(self.cache.labels) - 1
        self.category_section.add_label(label, label_index)
        return label_index

    def del_label_from_cache(self, user_label, user_label_index):
        self.del_category(user_label_index)
        # instructions order is important!!
        self.cache.labels.remove(user_label)
        #call it as the last instruction since it spoil label indices link between lists
        self.del_assignments_by_label(user_label_index)

    def del_category(self, user_label_index):
        self.category_section.del_item_by_text(self.cache.labels[user_label_index])

    def del_assignments_by_label(self, user_label_index):

        cur_frame_num = self.get_cur_frame_num()
        if not cur_frame_num:
            return
        assignments = self.get_data_by_label(user_label_index)
        assignment_indices = []
        for frame_num, assignment_num, detection_num in assignments:
            self.del_assignment_by_detection_num(detection_num)
            if frame_num == cur_frame_num:
                assignment_indices.append(assignment_num)

        #remove list from end to beginning to avoid indices shift
        assignment_indices.sort(reverse=True)
        for assignment_index in assignment_indices:
            self.assignment_list.takeItem(assignment_index)
        self.print_out_cache_per_frame(15)

    def del_unused_detection_from_cache(self, detection_num):
        cur_frame_num = self.get_cur_frame_num()
        self.cache.unused_detections[cur_frame_num].remove(detection_num)


    def load_video_file(self):
        #self.video_file_name, _ = QFileDialog.getOpenFileName(self, "Open Movie", QDir.homePath())
        self.video_file_name = 'sample.mkv'
        if not self.video_file_name == '':
            self.isVideoFileLoaded = True
            self.video_player.set_video_stream(VideoStream(self.video_file_name))

    def close(self):
        self.video_player.close()

    def get_cur_frame_num(self):
        vid_stream = self.video_player.video_stream
        return vid_stream.cur_frame_num if vid_stream else None

    def print_out_cache_per_frame(self, frame_num):
        print('unused detections', self.cache.unused_detections[frame_num])
        print('labels', self.cache.labels)
        print('assignments', self.cache.assignments[frame_num])