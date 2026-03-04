import sys
import os

import time
import cv2
import numpy as np

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from core_app.MITHRA_guis.GUI_MITHRA import *
from core_app.MITHRA_utils.processes import WebcamProcess, TelemetricLaserProcess



class GUIManagement(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(GUIManagement, self).__init__(parent)
        self.setupUi(self)

        self.webcam_process = WebcamProcess(1) #TODO implement source change
        self.webcam_on = False

        self.telemetric_laser_process = TelemetricLaserProcess()
        self.laser_on = False

        self.motor_speed_x = 10.0
        self.motor_speed_y = 10.0
        self.motor_speed_z = 10.0

        self.widget_plot_xrf.setBackground('w')
        self.widget_plot_fors.setBackground('w')
        self.widget_plot_pl1.setBackground('w')
        self.widget_plot_pl2.setBackground('w')
        self.widget_plot_pl3.setBackground('w')
        self.widget_plot_swir.setBackground('w')

        self.widget_map_1.ui.histogram.hide()
        self.widget_map_1.ui.roiBtn.hide()
        self.widget_map_1.ui.menuBtn.hide()

        self.widget_map_2.ui.histogram.hide()
        self.widget_map_2.ui.roiBtn.hide()
        self.widget_map_2.ui.menuBtn.hide()

        self.widget_map_3.ui.histogram.hide()
        self.widget_map_3.ui.roiBtn.hide()
        self.widget_map_3.ui.menuBtn.hide()

        self.widget_map_4.ui.histogram.hide()
        self.widget_map_4.ui.roiBtn.hide()
        self.widget_map_4.ui.menuBtn.hide()

    def update_webcam_view(self, frame):
        self.label_webcam.setPixmap(QPixmap.fromImage(frame))

    def update_distance(self, value):
        if value < 130:
            self.line_edit_read_z.setText("%.2f" % value)
        else:
            self.line_edit_read_z.setText("---")

    def update_progressbar(self, value, line_number):
        self.line_edit_progression.setText(str(value + 1) + '/' + str(line_number))
        progress = int(value + 1)
        self.acquisition_progressbar.setMaximum(int(line_number))
        self.acquisition_progressbar.setValue(progress)

    def update_image_view(self, data):
        self.widget_map_1.setImage(np.flip(data.T[self.spinbox_low_map1.value(), :, :], 1))
        self.widget_map_2.setImage(np.flip(data.T[self.spinbox_low_map2.value(), :, :], 1))
        self.widget_map_3.setImage(np.flip(data.T[self.spinbox_low_map3.value(), :, :], 1))
        self.widget_map_4.setImage(np.flip(data.T[self.spinbox_low_map4.value(), :, :], 1))
        # self.widget_map_4.setImage(np.flip(self.datacube_xrf.T[176, 1:-1, 1:-1], 1))

    def update_gui_params(self, param):
        self.line_edit_motor_speed.setText(str(param.motor_speed()))
        self.line_edit_mapping_duration_h.setText(str(int(param.mapping_duration()[1])))
        self.line_edit_mapping_duration_m.setText(str(int(param.mapping_duration()[2])))
        self.line_edit_mapping_duration_s.setText(str(int(param.mapping_duration()[3])))
        self.line_edit_pixel_number.setText(str(int(param.pixel_number())))
        self.line_edit_number_line.setText(str(param.line_number()))

    def speed_selection_x(self):
        speed_range = [0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 30.0, 50.0]
        i = self.slider_motorspeed_x.value()
        self.motor_speed_x = speed_range[i]
        self.line_edit_motrospeed_x.setText(str(self.motor_speed_x))

    def speed_selection_y(self):
        speed_range = [0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 30.0, 50.0]
        i = self.slider_motorspeed_y.value()
        self.motor_speed_y = speed_range[i]
        self.line_edit_motrospeed_y.setText(str(self.motor_speed_y))

    def speed_selection_z(self):
        speed_range = [0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 30.0, 50.0]
        i = self.slider_motorspeed_z.value()
        self.motor_speed_z = speed_range[i]
        self.line_edit_motrospeed_z.setText(str(self.motor_speed_z))