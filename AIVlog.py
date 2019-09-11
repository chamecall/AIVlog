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
from pascal_voc_writer import Writer
import pathlib
import re

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

        try:
            template = f"INSERT INTO `Detections` (`detection_id`, `frame_num`, `dnn_label`, `box`) VALUES (%s, %s, %s, %s)"
            data = []
            for frame_num, detections in self.cache.all_detections.items():
                for i, (dnn_label, box) in enumerate(detections):
                    box_str = format_bounding_box_tuple_to_str(box)
                    data.append((i, frame_num, dnn_label, box_str))
            self.data_base.exec_many_queries(template, data)


            template = f"INSERT INTO `Labels`(`label_id`, `name`) VALUES (%s, %s)"
            data = []
            for i, label in enumerate(self.cache.labels):
                data.append((i, label))
            self.data_base.exec_many_queries(template, data)

            template = f"INSERT INTO `Assignments`(`frame_num`, `label_id`, `detection_id`) VALUES (%s, %s, %s)"
            data = []
            for frame_num, assignments in self.cache.assignments.items():
                for detection_num, label in assignments:
                    label_num = self.cache.labels.index(label)
                    data.append((frame_num, label_num, detection_num))
            self.data_base.exec_many_queries(template, data)

            self.data_base.commit()
        except Exception as error:
            print(f"Failed to update record to database rollback: {error}")
            self.data_base.rollback()


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
        self.data_base.commit()
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
        self.data_base.commit()

        labels = []
        while cursor.rownumber < cursor.rowcount:
            label = cursor.fetchone()
            labels.append([label['label_id'], label['name']])
        labels.sort(key=lambda label_pair: label_pair[0])
        cache.labels = [label_pair[1] for label_pair in labels]

        # upload assignments
        cursor = self.data_base.exec_query("SELECT * FROM Assignments")
        self.data_base.commit()

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
            assignments_per_frame = assignments.get(frame_num, None)
            assignment_detection_nums = set(assignment[0] for assignment in assignments_per_frame) if assignments_per_frame else set()
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
            input_data_dir = os.path.join(input_data_dir, 'VOC2007')
            self.make_dir(input_data_dir)
            ann_dir_path = os.path.join(input_data_dir, 'Annotations')
            jpeg_img_dir_path = os.path.join(input_data_dir, 'JPEGImages')
            img_sets_dir_path = os.path.join(os.path.join(input_data_dir, 'ImageSets'), 'Main')
            pathlib.Path(img_sets_dir_path).mkdir(parents=True, exist_ok=True)
            self.make_dir(ann_dir_path)
            self.make_dir(jpeg_img_dir_path)
            self.make_dir(img_sets_dir_path)
            # folder containing image-detection_file pairs
            labels = self.generate_dataset(ann_dir_path, jpeg_img_dir_path)
            test_data_file_name, train_data_file_name = os.path.join(img_sets_dir_path, 'test.txt'), os.path.join(img_sets_dir_path, 'trainval.txt')
            # separate data to train and test
            self.separate_data(jpeg_img_dir_path, test_data_file_name, train_data_file_name)
            mmdetection_dir = 'mmdetection'
            self.generate_cfg(labels, mmdetection_dir)


    def generate_cfg(self, labels, mmdetection_dir_path):
        cfg_file = os.path.join(mmdetection_dir_path, 'configs/pascal_voc/faster_rcnn_r50_fpn_1x_voc0712.py')
        anno_path = os.path.join(mmdetection_dir_path, "data/VOC2007/Annotations")
        voc_file = os.path.join(mmdetection_dir_path, "mmdet/datasets/voc.py")
        total_epochs = 20
        self.modify_voc(voc_file, labels)
        self.modify_cfg(cfg_file, labels, total_epochs)


    def modify_cfg(self, config_name, labels, total_epochs):
        with open(config_name) as f:
            s = f.read()
            work_dir = re.findall(r"work_dir = \'(.*?)\'", s)[0]
            # Update `num_classes` including `background` class.
            s = re.sub('num_classes=.*?,',
                       'num_classes={},'.format(len(labels) + 1), s)
            s = re.sub('ann_file=.*?\],',
                       "ann_file=data_root + 'VOC2007/ImageSets/Main/trainval.txt',", s, flags=re.S)
            s = re.sub('total_epochs = \d+',
                       'total_epochs = {} #'.format(total_epochs), s)
            if "CocoDataset" in s:
                s = re.sub("dataset_type = 'CocoDataset'",
                           "dataset_type = 'VOCDataset'", s)
                s = re.sub("data_root = 'data/coco/'",
                           "data_root = 'data/VOCdevkit/'", s)
                s = re.sub("annotations/instances_train2017.json",
                           "VOC2007/ImageSets/Main/trainval.txt", s)
                s = re.sub("annotations/instances_val2017.json",
                           "VOC2007/ImageSets/Main/test.txt", s)
                s = re.sub("annotations/instances_val2017.json",
                           "VOC2007/ImageSets/Main/test.txt", s)
                s = re.sub("train2017", "VOC2007", s)
                s = re.sub("val2017", "VOC2007", s)
            else:
                s = re.sub('img_prefix=.*?\],',
                           "img_prefix=data_root + 'VOC2007/',".format(total_epochs), s)
        with open(config_name, 'w') as f:
            f.write(s)


    def modify_voc(self, voc_file, labels):
        print(labels)
        with open(voc_file) as f:
            s = f.read()
            s = re.sub('CLASSES = \(.*?\)',
                       'CLASSES = ({})'.format(", ".join(["\'{}\'".format(name) for name in labels])), s,
                       flags=re.S)
        with open(voc_file, 'w') as f:
            f.write(s)



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
                file_test.write(title + "\n")
            else:
                file_train.write(title + "\n")
                counter = counter + 1




    def generate_dataset(self, ann_dir_path, jpeg_img_dir_path):
        labels = []
        frame_width = self.video_player.video_stream.width
        frame_height = self.video_player.video_stream.height
        for frame_num, assignments in self.cache.assignments.items():
            if assignments:
                frame_name = os.path.join(jpeg_img_dir_path, f'frame_{frame_num}')
                image_name = f'{frame_name}.jpg'
                self.video_player.video_stream.save_frame_by_num_as(frame_num, image_name)

                voc_writer = Writer(image_name, frame_width, frame_height)

                for detection_num, label in assignments:
                    detection = self.cache.all_detections[frame_num][detection_num]
                    box = detection[1]
                    index = get_index_by_value(labels, label)
                    voc_writer.addObject(label, *box)
                xml_file_name = os.path.join(ann_dir_path, f'frame_{frame_num}.xml')
                voc_writer.save(xml_file_name)
        labels.sort()
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
