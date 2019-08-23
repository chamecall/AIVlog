from MainWindow import MainWindow
from PyQt5 import QtWidgets, QtCore

if __name__ == '__main__':
    import sys

    app = QtWidgets.QApplication(sys.argv)
    screen_size = app.primaryScreen().size()
    window = MainWindow((screen_size.width(), screen_size.height()))
    window.show()
    sys.exit(app.exec_())
