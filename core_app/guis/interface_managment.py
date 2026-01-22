import sys
import os

import time
import cv2
import numpy as np

from multiprocessing import Process
from multiprocessing.shared_memory import SharedMemory

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from core_app.guis.GUI_MITHRA import *
from core_app.utils.processes import Webcam

from core_app.controllers_TOREMOVE.controller_PanasonicHGC1100 import panasonic_hgc1100

class GUIManagement(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(GUIManagement, self).__init__(parent)
        self.setupUi(self)

        self.webcam = Webcam(0)
        self.webcam_on = False

        self.telemetric_laser = panasonic_hgc1100.Device()
        self.laser_on = False
        self.z_lock_status =

        self.widget_plot_xrf.setBackground('w')
        self.widget_plot_fors.setBackground('w')
        self.widget_plot_pl1.setBackground('w')
        self.widget_plot_pl2.setBackground('w')
        self.widget_plot_pl3.setBackground('w')
        self.widget_plot_swir.setBackground('w')

        self.widget_map_Ca.ui.histogram.hide()
        self.widget_map_Ca.ui.roiBtn.hide()
        self.widget_map_Ca.ui.menuBtn.hide()

        self.widget_map_Fe.ui.histogram.hide()
        self.widget_map_Fe.ui.roiBtn.hide()
        self.widget_map_Fe.ui.menuBtn.hide()

        self.widget_map_Cu.ui.histogram.hide()
        self.widget_map_Cu.ui.roiBtn.hide()
        self.widget_map_Cu.ui.menuBtn.hide()

        self.widget_map_Pb.ui.histogram.hide()
        self.widget_map_Pb.ui.roiBtn.hide()
        self.widget_map_Pb.ui.menuBtn.hide()


    def update_webcam_view(self, frame):
        self.label_webcam.setPixmap(QPixmap.fromImage(frame))

    def frame_consumer(self, frame):
        p_webcam = Process(target=self.webcam.get_frame)
        p_webcam.start()
        while self.webcam_on:
            shm = SharedMemory(name='shared_memory_webcam')
            data = np.ndarray((480, 640, 3), dtype=np.uint8, buffer=shm.buf)

            image = cv2.cvtColor(data, cv2.COLOR_BGR2RGB)

            convert_to_qt_format = QImage(image.data, image.shape[1], image.shape[0], QImage.Format_RGB888)

            # pic = convert_to_Qt_format.scaled(480, 640, Qt.KeepAspectRatio)

            frame.emit(convert_to_qt_format)
            time.sleep(0.01)
        p_webcam.terminate()
        shm.close()
        shm.unlink()
        frame.emit(QImage('fonts\\nosignal.jpg'))

    def update_distance(self, value):
        if value < 130:
            self.line_edit_read_z.setText("%.2f" % value)
        else:
            self.line_edit_read_z.setText("---")

    def distance_consumer(self, distance):
        p_laser = Process(target=self.laser.get_distance, args=(self.telemetric_laser, self.q_laser,))
        p_laser.start()
        while self.laser_on:
            data = self.q_laser.get()
            distance.emit(data)
        p_laser.terminate()


