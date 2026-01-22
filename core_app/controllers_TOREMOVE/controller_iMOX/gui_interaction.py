import sys

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from guis.GUI_iMOXcsu2 import *

class ConfigXRayTube(QMainWindow, Ui_imoxs_csu2):
    def __init__(self):
        super(ConfigXRayTube, self).__init__()
        self.setupUi(self)
        self.current = 0
        self.voltage = 0

    @pyqtSlot()
    def on_push_button_set_voltage_clicked(self):
        print('click!')




if __name__ == '__main__':
    app = QApplication(sys.argv)
    MainWindow = ConfigXRayTube()
    MainWindow.show()
    rc = app.exec_()
    sys.exit(rc)
