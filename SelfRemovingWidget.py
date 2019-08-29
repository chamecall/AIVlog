from PyQt5 import QtWidgets, QtCore, QtGui

class SelfRemovingWidget(QtWidgets.QWidget):
    def __init__(self, label_text, button_text, detection_num=None, parent=None):
        super(SelfRemovingWidget, self).__init__(parent)

        self.label = QtWidgets.QLabel(label_text)
        self.detection_num = detection_num
        self.button = QtWidgets.QPushButton(button_text)
        self.button.setStyleSheet("* {background-color: red;}")
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.button)
        self.setLayout(layout)