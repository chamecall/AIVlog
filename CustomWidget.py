from PyQt5 import QtWidgets, QtCore, QtGui

class CustomWidget(QtWidgets.QWidget):
    def __init__(self, label_text, button_text, parent=None):
        super(CustomWidget, self).__init__(parent)

        self.label = QtWidgets.QLabel(label_text)

        self.button = QtWidgets.QPushButton(button_text)
        self.button.setStyleSheet("* {background-color: red;}")
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.button)
        self.setLayout(layout)