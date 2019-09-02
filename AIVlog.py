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
from Utils import format_detection_to_print_out, extract_detection_data, format_bounding_box_tuple_to_str
import pickle
from DB import DB

class AIVlog(QtWidgets.QWidget):
    def __init__(self, parent, screen_size: tuple):
        super(AIVlog, self).__init__(parent)
        self.top_hbox = QHBoxLayout()
        self.detection_list = DetectionList(self)
        self.assignment_list = AssignmentList()
        self.label_section = LabelSection(self)

        self.label_section.label_list.assigning.connect(self.assign_label)
        self.label_section.label_removing.connect(self.del_label_from_cache)

        self.assignment_list.item_removing.connect(self.del_assignment_by_detection_num)
        self.list_hbox = QHBoxLayout()
        self.list_hbox.addWidget(self.detection_list)
        self.list_hbox.addWidget(self.label_section)
        self.list_hbox.addWidget(self.assignment_list)
        self.db_name = 'vlog_db'
        self.data_base = DB('localhost', 'root', 'root', self.db_name)
        self.cache = Cache()
        self.main_vbox = QVBoxLayout(self)
        self.video_player = VideoPlayer(self.cache, screen_size)
        self.video_player.detection_signal.connect(self.save_detections_to_cache)
        self.video_player.cache_signal.connect(self.extract_data_per_frame_from_cache)

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

    def change_category(self, user_label):
        self.category_section.category_list.clear()
        assignments = self.get_data_by_label(user_label)
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



    def get_data_by_label(self, user_label):
        # return list of items of the following form: (frame_num, assignment_num_on_this_frame, detection_num_on_this_frame)
        ret_data = []
        for frame_num, assignments in self.cache.assignments.items():
            for i, assignment in enumerate(assignments):
                if assignment[1] == user_label:
                    ret_data.append([frame_num, i, assignment[0]])
        return ret_data

    def del_assignment_by_detection_num(self, detection_num):
        cur_frame_num = self.get_cur_frame_num()
        detection_str = format_detection_to_print_out(self.cache.all_detections[cur_frame_num][detection_num])
        self.detection_list.add_item(detection_num, detection_str)
        self.cache.unused_detections[cur_frame_num].append(detection_num)
        self.del_assignment_from_cache(detection_num, cur_frame_num)


    def assign_label(self, user_label, user_label_num, detection_num):
        cur_frame_num = self.get_cur_frame_num()

        dnn_label, box = extract_detection_data(self.cache.all_detections[cur_frame_num][detection_num])
        self.save_assignment_to_cache(detection_num, user_label)
        self.assignment_list.add_assignment(dnn_label, user_label, box, detection_num)

        self.detection_list.del_dragged_item()
        self.del_unused_detection_from_cache(detection_num)
        if self.category_section.check_cur_item_by_label(user_label):
            self.change_category(user_label)


    def save_assignment_to_cache(self, detection_num, label):
        cur_frame_num = self.get_cur_frame_num()
        self.cache.assignments[cur_frame_num].append([detection_num, label])

    def del_assignment_from_cache(self, detection_num, cur_frame_num):
        indices = [i for i, assignment in enumerate(self.cache.assignments[cur_frame_num]) if
                   assignment[0] == detection_num]
        assert len(indices) == 1
        assignment_num_to_del = indices[0]
        user_label = self.cache.assignments[cur_frame_num][assignment_num_to_del][1]
        del self.cache.assignments[cur_frame_num][assignment_num_to_del]
        if self.category_section.check_cur_item_by_label(user_label):
            self.change_category(user_label)

    def save_detections_to_cache(self, frame_num, detections):
        self.detection_list.set_detections(detections)
        self.cache.all_detections[frame_num] = detections
        self.cache.unused_detections[frame_num] = list(range(len(detections)))
        self.cache.assignments[frame_num] = []
        self.assignment_list.clear()

    def extract_data_per_frame_from_cache(self):
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
        self.category_section.add_label(label)
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

            #self.change_category(user_label_num)
            if frame_num == cur_frame_num:
                assignment_indices.append(assignment_num)

        #remove list from end to beginning to avoid indices shift
        assignment_indices.sort(reverse=True)
        for assignment_index in assignment_indices:
            self.assignment_list.takeItem(assignment_index)
        #self.print_out_cache_per_frame(15)

    def del_unused_detection_from_cache(self, detection_num):
        cur_frame_num = self.get_cur_frame_num()
        self.cache.unused_detections[cur_frame_num].remove(detection_num)

    def save_project_into_binary_file(self):
        name, _ = QFileDialog.getSaveFileName(self, 'Save project', QDir.homePath())
        if name == '':
            return
        with open(name, 'wb') as f:
            pickle.dump(self.cache, f)


    def save_project_into_db(self):
        # truncate all tables in db
        self.truncate_bd()

        template = f"INSERT INTO `Detections` (`detection_id`, `frame_num`, `dnn_label`, `box`) VALUES (%s, %s, %s, %s)"
        for frame_num, detections in self.cache.all_detections.items():
            for i, (dnn_label, _, box) in enumerate(detections):
                box_str = format_bounding_box_tuple_to_str(box)
                self.data_base.exec_template_query(template, (i, frame_num, dnn_label, box_str))

        template = f"INSERT INTO `Labels`(`label_id`, `name`) VALUES (%s, %s)"
        for i, label in enumerate(self.cache.labels):
            self.data_base.exec_template_query(template, (i, label))

        template = f"INSERT INTO `Assignments`(`frame_num`, `label_id`, `detection_id`) VALUES (%s, %s, %s)"
        for frame_num, assignments in self.cache.assignments.items():
            for detection_num, label in assignments:
                label_num = self.cache.labels.index(label)
                self.data_base.exec_template_query(template, (frame_num, label_num, detection_num))

    def truncate_bd(self):
        self.data_base.exec_query('SET FOREIGN_KEY_CHECKS=0;')
        truncates = self.data_base.exec_query(f"SELECT Concat('TRUNCATE TABLE ',table_schema,'.',TABLE_NAME, ';') \
                                                FROM INFORMATION_SCHEMA.TABLES where  table_schema = '{self.db_name}';").fetchall()
        for truncate in truncates:
            self.data_base.exec_query(list(truncate.values())[0])

    def open_project_from_binary_file(self):
        name, _ = QFileDialog.getOpenFileName(self, "Open project", QDir.homePath())
        if name == '':
            return
        with open(name, 'rb') as f:
            self.update_cache(pickle.load(f))
        self.clear_all_lists()
        self.extract_data_per_frame_from_cache()
        self.set_labels_to_label_list(self.cache.labels)

    def open_project_from_db(self):
        cache = Cache()

        # upload detections
        cursor = self.data_base.exec_query("SELECT * FROM Detections")
        detections = self.cache.all_detections
        while cursor.rownumber < cursor.rowcount:
            detection = cursor.fetchone()
            frame_num = detection['frame_num']
            if not detections.get(frame_num, None):
                detections[frame_num] = []
            detections[frame_num].append([detection['dnn_label'], detection['box']])

        # upload labels
        cursor = self.data_base.exec_query("SELECT * FROM Labels")
        labels = self.cache.labels
        while cursor.rownumber < cursor.rowcount:
            label = cursor.fetchone()
            labels.append(label['name'])

        # upload assignments
        cursor = self.data_base.exec_query("SELECT * FROM Assignments")
        assignments = self.cache.assignments
        while cursor.rownumber < cursor.rowcount:
            assignment = cursor.fetchone()
            frame_num = assignment['frame_num']
            if not assignments.get(frame_num, None):
                assignments[frame_num] = []
            assignments[frame_num].append([assignment['detection_id'], assignment['label_id']])

        #self.define_unused_detections_by_assignments()

        self.update_cache(cache)
        self.clear_all_lists()
        self.extract_data_per_frame_from_cache()
        self.set_labels_to_label_list(self.cache.labels)


    def define_unused_detections_by_assignments(self):
        for frame_num in self.cache.all_detections.keys():
            assignments = self.cache.assignments.get(frame_num, None)
            if assignments:
                print(frame_num)
                for assignment in assignments:
                    print('\t', assignment[0])
            else:
                pass


    def clear_all_lists(self):
        self.detection_list.clear()
        self.label_section.label_list.clear()
        self.assignment_list.clear()
        self.category_section.combo_box.clear()

    def set_labels_to_label_list(self, labels):
        for i, label in enumerate(labels):
            self.label_section.add_item(label, i)
            self.category_section.add_label(label)


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

    def update_cache(self, cache):
        self.video_player.cache = self.cache = cache
