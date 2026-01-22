import sys
import time

import numpy as np
import cv2

from multiprocessing import Process, Queue
from multiprocessing.shared_memory import SharedMemory

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from pyqtgraph.parametertree.parameterTypes import file


from controllers_TOREMOVE.controller_Amptek import mca8000d
from controllers_TOREMOVE.controller_PanasonicHGC1100 import panasonic_hgc1100


from MITHRA_IO.load import DataLoader
from MITHRA_IO.save import DataSaving

from MITHRA_guis.interface_managment import GUIManagement

from MITHRA_utils.mapping_parameters import MappingParameters
from MITHRA_utils.threads import *


class Master(GUIManagement):
    def __init__(self, *args, **kwargs):
        super(Master, self).__init__(*args, **kwargs)

        self.gui = GUIManagement()

        self.motor = None
        self.x_ray_detector = mca8000d.Device()
        self.optical_spectrometer_1 = None
        self.optical_spectrometer_2 = None

        self.telemetric_laser = panasonic_hgc1100.Device()
        self.q_laser = Queue()
        self.z_lock_status = (False, None) # package of z_lock_status and z_lock_distance
        self.q_z_lock_status = Queue()

        self.cfg = DataLoader().load_cfg('G:\DATA\PyCharm Projects\MITHRA\core_app\MITHRA.cfg')

        self.project_name = self.cfg['project info']['name']

        self.x = self.cfg['mapping parameters']['x']
        self.y = self.cfg['mapping parameters']['y']
        self.pixel_size = self.cfg['mapping parameters']['pixel_size']
        self.acquisition_time = self.cfg['mapping parameters']['acquisition_time']

        MappingParameters(self.x, self.y, self.pixel_size, self.acquisition_time)

        self.threadpool = QThreadPool.globalInstance()

    def update_params(self):
        self.x = int(self.line_edit_x.text())
        self.y = int(self.line_edit_y.text())
        self.pixel_size = int(self.line_edit_pixel_size.text())
        self.acquisition_time = int(self.line_edit_acquisition_time.text())
        param = MappingParameters(self.x, self.y, self.pixel_size, self.acquisition_time)

        self.update_gui_params(param)

    def frame_consumer(self, frame):
        p_webcam = Process(target=self.webcam_process.get_frame)
        p_webcam.start()
        while self.webcam_on:
            shm = SharedMemory(name='shared_memory_webcam')
            data = np.ndarray((480, 640, 3), dtype=np.uint8, buffer=shm.buf)

            image = cv2.cvtColor(data, cv2.COLOR_BGR2RGB)
            convert_to_qt_format = QImage(image.data, image.shape[1], image.shape[0], QImage.Format_RGB888)
            # pic = convert_to_Qt_format.scaled(480, 640, Qt.KeepAspectRatio)

            frame.emit(convert_to_qt_format)
            time.sleep(0.03)
        p_webcam.terminate()
        shm.close()
        shm.unlink()
        frame.emit(QImage('fonts\\nosignal.jpg'))

    def distance_consumer(self, distance):
        p_laser = Process(target=self.telemetric_laser_process.get_distance, args=(self.telemetric_laser,
                                                                                   self.q_laser,
                                                                                   self.q_z_lock_status,
                                                                                   self.motor))
        p_laser.start()
        while self.laser_on:
            data = self.q_laser.get()
            distance.emit(data)
            self.q_z_lock_status.put(self.z_lock_status)
        p_laser.terminate()

    """ GUI interactions"""
    def closeEvent(self, event):
        response = QMessageBox.question(self, "Confirm", "Are you sure you want to leave?",
                                        QMessageBox.Yes, QMessageBox.No)
        if response == QMessageBox.Yes:
            self.webcam_on = False
            self.laser_on = False
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

        params = MappingParameters(self.x, self.y, self.pixel_size, self.acquisition_time)
        DataSaving(self.project_name, params)
        #TODO build cfg from params and saved it in project folder
        #TODO Check modality for proper threading procedure




    @pyqtSlot()
    def on_push_button_stop_clicked(self):
        self.push_button_start.setEnabled(True)
        self.push_button_stop.setEnabled(False)

    @pyqtSlot()
    def on_line_edit_x_editingFinished(self):
        self.update_params()

    @pyqtSlot()
    def on_line_edit_y_editingFinished(self):
        self.update_params()

    @pyqtSlot()
    def on_line_edit_pixel_size_editingFinished(self):
        self.update_params()

    @pyqtSlot()
    def on_line_edit_acquisition_time_editingFinished(self):
        self.update_params()

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
    def on_push_button_capture_clicked(self):
        img = self.label_webcam.pixmap()
        file = str(QFileDialog.getSaveFileName(self, 'Save Image'))
        img.save(file)
        #TODO save file in folder Photo within project

    @pyqtSlot()
    def on_push_button_connect_telemetric_clicked(self):
        try:
            # self.telemetric_laser.connect()
            self.checkbox_telemetric_connected.setCheckState(True)
            self.laser_on = True
            QMessageBox.information(self, "Information", 'Telemetric laser connected', QMessageBox.Ok)
        except Exception as e:
            QMessageBox.warning(self, "Warning", str(e), QMessageBox.Ok)
        thread_telemetric_laser = ThreadLaser(self.distance_consumer)
        thread_telemetric_laser.signals.distance.connect(self.update_distance)
        self.threadpool.start(thread_telemetric_laser)

    @pyqtSlot()
    def on_push_button_lock_z_clicked(self):
        self.push_button_lock_z.setEnabled(False)
        self.push_button_unlock_z.setEnabled(True)
        # if self.motor_connected_owis:
        #     self.motor.set_z_correction_param()
        z_lock_distance = float(self.line_edit_read_z.text())
        self.line_edit_lock_z.setText(str(z_lock_distance))
        self.z_lock_status = (True, z_lock_distance)

    @pyqtSlot()
    def on_push_button_unlock_z_clicked(self):
        self.push_button_lock_z.setEnabled(True)
        self.push_button_unlock_z.setEnabled(False)
        self.z_lock_status = (False, None)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    MainWindow = Master()
    MainWindow.show()
    rc = app.exec_()
    sys.exit(rc)