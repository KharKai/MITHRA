import sys
import time

import numpy as np
import cv2

from multiprocessing import Process
from multiprocessing.shared_memory import SharedMemory

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from pyqtgraph.parametertree.parameterTypes import file

from MITHRA_IO.load import DataLoader

from guis.interface_managment import GUIManagement

from utils.mapping_parameters import MappingParameters
from utils.threads import *


class Master(GUIManagement):
    def __init__(self, *args, **kwargs):
        super(Master, self).__init__(*args, **kwargs)

        self.gui = GUIManagement()

        self.motor = None
        self.x_ray_detector = None
        self.optical_spectrometer_1 = None
        self.optical_spectrometer_2 = None

        self.cfg = DataLoader().load_cfg('G:\DATA\PyCharm Projects\MITHRA\core_app\MITHRA.cfg')

        self.project_name = self.cfg['project info']['name']

        self.x = self.cfg['mapping parameters']['x']
        self.y = self.cfg['mapping parameters']['y']
        self.pixel_size = self.cfg['mapping parameters']['pixel_size']
        self.acquisition_time = self.cfg['mapping parameters']['acquisition_time']

        MappingParameters(self.x, self.y, self.pixel_size, self.acquisition_time)

        self.threadpool = QThreadPool.globalInstance()

    def update_cfg(self):
        self.x = int(self.line_edit_x.text())
        self.y = int(self.line_edit_y.text())
        self.pixel_size = int(self.line_edit_pixel_size.text())
        self.acquisition_time = int(self.line_edit_acquisition_time.text())
        MappingParameters(self.x, self.y, self.pixel_size, self.acquisition_time)

    """ GUI interactions"""

    def closeEvent(self, event):
        response = QMessageBox.question(self, "Confirm", "Are you sure you want to leave?",
                                        QMessageBox.Yes, QMessageBox.No)
        if response == QMessageBox.Yes:
            self.webcam_on = False
            event.accept()
        else:
            event.ignore()

    @pyqtSlot()
    def on_push_button_browse_clicked(self):
        self.project_name = str(QFileDialog.getExistingDirectory(self, "Select or create Project directory"))
        self.line_edit_project_name.setText(self.project_name)

    @pyqtSlot()
    def on_push_button_start_clicked(self):
        self.push_button_start.setEnabled(False)
        self.push_button_stop.setEnabled(True)

    @pyqtSlot()
    def on_push_button_stop_clicked(self):
        self.push_button_start.setEnabled(True)
        self.push_button_stop.setEnabled(False)

    @pyqtSlot()
    def on_push_button_start_webcam_clicked(self):
        if not self.webcam_on:
            try:
                thread_webcam = ThreadWebcam(self.frame_consumer)
                thread_webcam.signals.webcam_update.connect(self.update_webcam_view)
                self.threadpool.start(thread_webcam)
                self.webcam_on = True
            except Exception as e:
                QMessageBox.warning(self, "Warning", str(e), QMessageBox.Ok)
        else:
            QMessageBox.information(self, "Information", 'Webcam is already running', QMessageBox.Ok)

    @pyqtSlot()
    def on_push_button_stop_webcam_clicked(self):
        if self.webcam_on:
            self.webcam_on = False

        else:
            QMessageBox.information(self, "Information", 'Webcam is already stopped', QMessageBox.Ok)

    @pyqtSlot()
    def on_push_button_connect_telemetric_clicked(self):
        try:
            self.telemetric_laser.connect()
            self.checkbox_telemetric_connected.setCheckState(True)
            self.laser_on = True
            QMessageBox.information(self, "Information", 'Telemetric laser connected', QMessageBox.Ok)
        except Exception as e:
            QMessageBox.warning(self, "Warning", str(e), QMessageBox.Ok)
        thread_telemetric_laser = ThreadLaser(self.get_distance)
        thread_telemetric_laser.signals.distance.connect(self.update_distance)
        self.threadpool.start(thread_telemetric_laser)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    MainWindow = Master()
    MainWindow.show()
    rc = app.exec_()
    sys.exit(rc)