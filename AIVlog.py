from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QDir, Qt, QUrl
from PyQt5.QtWidgets import (QApplication, QFileDialog, QHBoxLayout, QVBoxLayout, QLabel,
                             QPushButton, QSizePolicy, QSlider, QStyle, QVBoxLayout, QWidget, QInputDialog)
from DetectionList import DetectionList
from VideoStream import VideoStream
from VideoPlayer import VideoPlayer
from LabelSection import LabelSection
from AssignmentList import AssignmentList
from Cache import Cache
from CategorySection import CategorySection
from Utils import format_detection_to_print_out, extract_detection_data, format_bounding_box_tuple_to_str
from DB import DB
import os
from Utils import get_index_by_value, generate_yolo_style_object_detection_row
import glob

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
        self.db_name = ''
        self.data_base = None
        self.cache = Cache()
        self.main_vbox = QVBoxLayout(self)
        self.video_player = VideoPlayer(self.cache, screen_size)
        self.video_player.detection_signal.connect(self.update_data_per_frame)
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
        self.is_video_loaded = False

    def change_category(self, user_label):
        assignments = self.get_data_from_assignments_by_label(user_label)
        data = self.get_category_data_by_assignments(assignments)
        self.update_category_list(data)

    def update_category_list(self, data):
        self.category_section.category_list.clear()
        for frame_num, bouding_box, dnn_label in data:
            self.category_section.category_list.add_item(f'{frame_num}\t{bouding_box}\t{dnn_label}')

    def get_category_data_by_assignments(self, assignments):
        # return list of items of the following form: (frame_num, bounding_box, dnn_label)
        ret_list = []
        for frame_num, _, detection_num in assignments:
            dnn_label, box = extract_detection_data(self.cache.all_detections[frame_num][detection_num])

            ret_list.append([frame_num, box, dnn_label])
        return ret_list

    def get_data_from_assignments_by_label(self, user_label):
        # return list of items of the following form: (frame_num, assignment_num_on_this_frame, detection_num_on_this_frame)
        ret_data = []
        for frame_num, assignments in self.cache.assignments.items():
            for i, assignment in enumerate(assignments):
                if assignment[1] == user_label:
                    ret_data.append([frame_num, i, assignment[0]])
        return ret_data

    def del_assignment_by_detection_num(self, detection_num, frame_num=None):
        cur_frame_num = self.get_cur_frame_num()

        frame_num = cur_frame_num if not frame_num else frame_num
        if frame_num is None or frame_num == cur_frame_num:
            self.add_unused_detection_to_detection_list(detection_num, cur_frame_num)
        self.cache.unused_detections[frame_num].append(detection_num)
        self.del_assignment_from_cache(detection_num, frame_num)

    def add_unused_detection_to_detection_list(self, detection_num, cur_frame_num):
        detection_str = format_detection_to_print_out(self.cache.all_detections[cur_frame_num][detection_num])
        self.detection_list.add_item(detection_num, detection_str)


    def assign_label(self, user_label, user_label_num, detection_num):
        cur_frame_num = self.get_cur_frame_num()

        dnn_label, box = extract_detection_data(self.cache.all_detections[cur_frame_num][detection_num])
        self.save_assignment_to_cache(detection_num, user_label)
        self.assignment_list.add_assignment(dnn_label, user_label, box, detection_num)

        self.detection_list.del_dragged_item()
        self.del_unused_detection_from_cache(detection_num)
        self.update_cur_category(user_label)


    def save_assignment_to_cache(self, detection_num, label):
        cur_frame_num = self.get_cur_frame_num()
        self.cache.assignments[cur_frame_num].append([detection_num, label])

    def del_assignment_from_cache(self, detection_num, frame_num):
        indices = [i for i, assignment in enumerate(self.cache.assignments[frame_num]) if
                   assignment[0] == detection_num]
        assert len(indices) == 1
        assignment_num_to_del = indices[0]
        user_label = self.cache.assignments[frame_num][assignment_num_to_del][1]
        del self.cache.assignments[frame_num][assignment_num_to_del]
        self.update_cur_category(user_label)

    def update_cur_category(self, user_label):
        if self.category_section.check_cur_item_by_label(user_label):
            self.change_category(user_label)

    def update_data_per_frame(self, frame_num, detections):
        numbered_detections = [[i, [detection[0], [int(num) for num in detection[1]]]] for i, detection in
                               enumerate(detections)]
        self.detection_list.set_detections(numbered_detections)
        self.cache.all_detections[frame_num] = detections
        self.cache.unused_detections[frame_num] = list(range(len(detections)))
        self.cache.assignments[frame_num] = []
        self.assignment_list.clear()

    def extract_data_per_frame_from_cache(self):

        cur_frame_num = self.get_cur_frame_num()
        if not self.is_video_loaded or not self.cache.all_detections.get(cur_frame_num, None):
            return
        detections = [[unused_detection_num, self.cache.all_detections[cur_frame_num][unused_detection_num]] for unused_detection_num in self.cache.unused_detections[cur_frame_num]]
        self.detection_list.set_detections(detections)
        self.upload_data_from_cache_to_assignment_list(cur_frame_num)

    def upload_data_from_cache_to_assignment_list(self, cur_frame_num):
        self.assignment_list.clear()
        assignments = self.cache.assignments[cur_frame_num]
        frame_detections = self.cache.all_detections[cur_frame_num]
        for detection_num, user_label in assignments:
            dnn_label, box = frame_detections[detection_num]
            self.assignment_list.add_assignment(dnn_label, user_label, box, detection_num)


    def check_label(self, label):
        if label == '':
            return False
        return True

    def add_label(self, label):
        self.cache.labels.append(label)
        self.category_section.add_label(label)

    def del_label_from_cache(self, user_label):
        self.del_category(user_label)
        # instructions order is important!!
        self.cache.labels.remove(user_label)
        self.del_assignments_by_label(user_label)

    def del_category(self, user_label):
        self.category_section.del_item_by_text(user_label)

    def del_assignments_by_label(self, user_label):
        cur_frame_num = self.get_cur_frame_num()
        if not self.is_video_loaded:
            return
        assignments = self.get_data_from_assignments_by_label(user_label)
        assignment_indices = []

        for frame_num, assignment_num, detection_num in assignments:
            self.del_assignment_by_detection_num(detection_num, frame_num)

            if frame_num == cur_frame_num:
                assignment_indices.append(assignment_num)

        #remove list from end to beginning to avoid indices shift
        assignment_indices.sort(reverse=True)
        for assignment_index in assignment_indices:
            self.assignment_list.takeItem(assignment_index)

    def del_unused_detection_from_cache(self, detection_num):
        cur_frame_num = self.get_cur_frame_num()
        #self.cache.unused_detections[cur_frame_num].remove(detection_num)


    def save(self):
        if not self.is_video_loaded or self.data_base is None:
            self.save_as()
        else:
            self.upload_data_from_cache_to_db()


    def save_as(self):
        if not self.is_video_loaded:
            return
        text, ok = QInputDialog.getText(self, 'DataBase name input', 'Enter database name for data storing:')

        if ok:
            self.db_name = text
            self.data_base = DB('localhost', 'root', 'root', self.db_name)
            self.upload_data_from_cache_to_db()

            name, _ = QFileDialog.getSaveFileName(self, 'Save project', QDir.homePath())
            if name == '':
                return

            with open(name, 'w') as project_file:
                project_file.write('\n'.join([self.video_file_name, self.db_name]))



    def upload_data_from_cache_to_db(self):
        # truncate all tables in db
        self.truncate_bd()

        template = f"INSERT INTO `Detections` (`detection_id`, `frame_num`, `dnn_label`, `box`) VALUES (%s, %s, %s, %s)"
        for frame_num, detections in self.cache.all_detections.items():
            for i, (dnn_label, box) in enumerate(detections):
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


    def open_project_from_db(self):
        name, _ = QFileDialog.getOpenFileName(self, "Open project", QDir.homePath())
        if name == '':
            return
        with open(name, 'r') as project_file:
            self.video_file_name = project_file.readline().strip()
            self.db_name = project_file.readline().strip()

            self.data_base = DB('localhost', 'root', 'root', self.db_name)
            self.is_video_loaded = True
            self.video_player.set_video_stream(VideoStream(self.video_file_name))
            self.load_data_from_db_to_cache()


    def load_data_from_db_to_cache(self):
        cache = Cache()

        # upload detections
        cursor = self.data_base.exec_query("SELECT * FROM Detections")
        cache.all_detections = {}
        while cursor.rownumber < cursor.rowcount:
            detection = cursor.fetchone()
            frame_num = detection['frame_num']
            if not cache.all_detections.get(frame_num, None):
                cache.all_detections[frame_num] = []
            box = [int(num) for num in detection['box'][1:-1].split(',')]
            cache.all_detections[frame_num].append([detection['dnn_label'], box])

        # upload labels
        cursor = self.data_base.exec_query("SELECT * FROM Labels")
        labels = []
        while cursor.rownumber < cursor.rowcount:
            label = cursor.fetchone()
            labels.append([label['label_id'], label['name']])
        labels.sort(key=lambda label_pair: label_pair[0])
        cache.labels = [label_pair[1] for label_pair in labels]

        # upload assignments
        cursor = self.data_base.exec_query("SELECT * FROM Assignments")
        cache.assignments = {}
        for frame_num in cache.all_detections.keys():
            cache.assignments[frame_num] = []
        while cursor.rownumber < cursor.rowcount:
            assignment = cursor.fetchone()
            frame_num = assignment['frame_num']
            label = cache.labels[assignment['label_id']]
            cache.assignments[frame_num].append([assignment['detection_id'], label])

        cache.unused_detections = self.define_unused_detections_by_assignments(cache.all_detections, cache.assignments)
        self.update_cache(cache)
        self.clear_all_lists()
        self.extract_data_per_frame_from_cache()
        self.set_labels_to_label_list(self.cache.labels)
        #self.change_category(self.cache.labels[-1])

    def define_unused_detections_by_assignments(self, all_detections, assignments):
        unused_detections = {}
        for frame_num, detections in all_detections.items():
            all_detection_nums = set(range(len(detections)))
            assignments = assignments.get(frame_num, None)
            assignment_detection_nums = set(assignment[0] for assignment in assignments) if assignments else set()
            unused_detection_nums = all_detection_nums - assignment_detection_nums
            unused_detections[frame_num] = list(unused_detection_nums)
        return unused_detections


    def clear_all_lists(self):
        self.detection_list.clear()
        self.label_section.label_list.clear()
        self.assignment_list.clear()
        self.category_section.combo_box.clear()

    def set_labels_to_label_list(self, labels):
        for label in labels:
            self.label_section.add_item(label)
            self.category_section.add_label(label)


    def create_project(self):
        self.video_file_name, _ = QFileDialog.getOpenFileName(self, "Open Movie", QDir.homePath())
        if not self.video_file_name == '':
            self.is_video_loaded = True
            self.video_player.set_video_stream(VideoStream(self.video_file_name))


    def generate_dnn_input_data(self):
        input_data_dir = QFileDialog.getExistingDirectory(self, "Open dataset directory", QDir.homePath())
        if not input_data_dir == '':
            labels_dir_path = os.path.join(input_data_dir, 'labels')
            names_file_name = os.path.join(input_data_dir, 'data.names')
            self.make_dir(labels_dir_path)
            # folder containing image-detection_file pairs
            labels = self.generate_dataset(labels_dir_path)
            labels_num = len(labels)
            test_data_file_name, train_data_file_name = os.path.join(input_data_dir, 'test.txt'), os.path.join(input_data_dir, 'train.txt')
            # separate data to train and test
            self.separate_data(labels_dir_path, test_data_file_name, train_data_file_name)
            # .names file
            self.generate_names_file(names_file_name, labels)
            backup_dir = os.path.join(input_data_dir, 'backup')
            data_file_name = os.path.join(input_data_dir, 'data.data')
            self.make_dir(backup_dir)
            # .data file
            self.generate_data_file(data_file_name, labels_num, train_data_file_name, test_data_file_name, names_file_name, backup_dir)

            original_cfg_file_name = 'cfg/yolov3.cfg'
            result_cfg_file_name = os.path.join(input_data_dir, 'yolov3.cfg')

            self.generate_cfg_file(original_cfg_file_name, result_cfg_file_name, labels_num)

    @staticmethod
    def generate_cfg_file(orig_cfg_file, result_cfg_file, labels_num):
        filters_row_nums = [603, 689, 776]
        classes_row_nums = [610, 696, 783]

        with open(orig_cfg_file, 'r') as original_cfg:
            cfg = original_cfg.readlines()
        filters_str = f'filters={(labels_num + 5) * 3}\n'
        classes_str = f'classes={labels_num}\n'

        for filters_row_num in filters_row_nums:
            cfg[filters_row_num-1] = filters_str

        for classes_row_num in classes_row_nums:
            cfg[classes_row_num-1] = classes_str

        with open(result_cfg_file, 'w') as result_cfg:
            result_cfg.writelines(cfg)


    @staticmethod
    def generate_data_file(data_file, classes_num, train_file, test_file, names_file, backup_dir):
        with open(data_file, 'w') as data_file:
            data_file.write(f'classes = {classes_num}\n')
            data_file.write(f'train = {train_file}\n')
            data_file.write(f'valid = {test_file}\n')
            data_file.write(f'names = {names_file}\n')
            data_file.write(f'backup = {backup_dir}\n')



    @staticmethod
    def separate_data(labels_dir, test_data_file_name, train_data_file_name):
        current_dir = labels_dir
        percentage_test = 15
        file_train = open(train_data_file_name, 'w')
        file_test = open(test_data_file_name, 'w')

        counter = 1
        index_test = round(100 / percentage_test)
        for pathAndFilename in glob.iglob(os.path.join(current_dir, "*.jpg")):
            title, ext = os.path.splitext(os.path.basename(pathAndFilename))

            if counter == index_test:
                counter = 1
                file_test.write(current_dir + "/" + title + '.jpg' + "\n")
            else:
                file_train.write(current_dir + "/" + title + '.jpg' + "\n")
                counter = counter + 1

    def generate_names_file(self, names_file_name, labels):
        with open(names_file_name, 'w') as names_file:
            for label in labels:
                names_file.write(f'{label}\n')


    def generate_dataset(self, labels_dir_path):
        labels = []
        frame_width = self.video_player.video_stream.width
        frame_height = self.video_player.video_stream.height
        for frame_num, assignments in self.cache.assignments.items():
            if assignments:
                frame_name = os.path.join(labels_dir_path, f'frame_{frame_num}')
                self.video_player.video_stream.save_frame_by_num_as(frame_num, f'{frame_name}.jpg')
                with open(f'{frame_name}.txt', 'w') as label_txt:
                    for detection_num, label in assignments:
                        detection = self.cache.all_detections[frame_num][detection_num]
                        box = detection[1]
                        index = get_index_by_value(labels, label)
                        object_detection_row = generate_yolo_style_object_detection_row(index, box, frame_width,
                                                                                        frame_height)
                        label_txt.write(object_detection_row)
        return labels

    def make_dir(self, dir_name):
        try:
            os.mkdir(dir_name)
        except:
            print('failed to create directory')

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
