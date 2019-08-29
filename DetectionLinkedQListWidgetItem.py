from PyQt5 import QtWidgets, QtCore


class DetectionLinkedQListWidgetItem(QtWidgets.QListWidgetItem):
    def __init__(self, detection_num, value, parent=None):
        super(DetectionLinkedQListWidgetItem, self).__init__(value, parent)
        self.detection_num = str(detection_num)
