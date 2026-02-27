import sys
import time
from fileinput import filename

import numpy as np
import cv2

from multiprocessing import Process, Queue
from multiprocessing.shared_memory import SharedMemory

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from controllers_TOREMOVE.controller_Owis import owis
from controllers_TOREMOVE.controller_Amptek import mca8000d
from controllers_TOREMOVE.controller_QePro import qepro
from controllers_TOREMOVE.controller_PanasonicHGC1100 import panasonic_hgc1100


from MITHRA_IO.load import DataLoader
from MITHRA_IO.save import DataSaver

from MITHRA_guis.interface_managment import GUIManagement

from MITHRA_utils.acquisition_parameters import AcquisitionParameters
from MITHRA_utils.data_acquisition import Data, DataAcquisition
from MITHRA_utils.threads import *


class Master(GUIManagement):
    def __init__(self, *args, **kwargs):
        super(Master, self).__init__(*args, **kwargs)

        self.gui = GUIManagement()

        self.motor = owis.Device()
        self.x_ray_detector = mca8000d.Device()
        self.optical_spectrometer_1 = qepro.Device()
        self.optical_spectrometer_2 = None

        self.data_acquisition_status = (False, None, None)
        self.q_data_acquisition_status = Queue()

        self.telemetric_laser = panasonic_hgc1100.Device()
        self.q_laser = Queue()
        self.z_lock_status = (False, None) # package of z_lock_status and z_lock_distance
        self.q_z_lock_status = Queue()

        self.cfg = DataLoader().load_cfg('G:\DATA\PyCharm Projects\MITHRA\core_app\MITHRA.cfg')
        # self.cfg = DataLoader().load_cfg('C:\Data\MITHRA\core_app\MITHRA.cfg')

        self.analyse_list = []
        self.run_counter = 0

        self.project_name = self.cfg['project info']['name']
        self.file_name = self.cfg['analyse list'][self.run_counter]['analyse name']
        self.operator = self.cfg['project info']['operator']
        self.localisation = self.cfg['project info']['localisation']

        self.x = self.cfg['analyse list'][self.run_counter]['mapping parameters']['x']
        self.y = self.cfg['analyse list'][self.run_counter]['mapping parameters']['y']
        self.pixel_size = self.cfg['analyse list'][self.run_counter]['mapping parameters']['pixel_size']
        self.acquisition_time = self.cfg['analyse list'][self.run_counter]['mapping parameters']['acquisition_time']

        self.global_data_acquisition_parameter= DataAcquisition(self.x, self.y, self.pixel_size,
                                                                self.acquisition_time, self.project_name,
                                                                self.file_name, self.operator, self.localisation)

        self.saver = DataSaver(self.x, self.y, self.pixel_size, self.acquisition_time, self.project_name,
                               self.file_name, self.operator, self.localisation)

        self.threadpool = QThreadPool.globalInstance()

    def update_params(self):
        self.x = int(self.line_edit_x.text())
        self.y = int(self.line_edit_y.text())
        self.pixel_size = int(self.line_edit_pixel_size.text())
        self.acquisition_time = int(self.line_edit_acquisition_time.text())

        self.project_name = self.line_edit_project_name.text()
        self.file_name = self.line_edit_file_name.text()
        self.operator = self.line_edit_operator.text()
        self.localisation = self.line_edit_localisation.text()



        self.global_data_acquisition_parameter = DataAcquisition(self.x, self.y, self.pixel_size,
                                                                 self.acquisition_time, self.project_name,
                                                                 self.file_name, self.operator, self.localisation)

        self.global_data_acquisition_parameter.data_acquisition_xrf = self.checkbox_xrf.isChecked()
        self.global_data_acquisition_parameter.data_acquisition_ris_lis = self.checkbox_ris_lis.isChecked()
        self.global_data_acquisition_parameter.data_acquisition_swir = self.checkbox_swir.isChecked()

        self.global_data_acquisition_parameter.data_acquisition_type_and_mode(self.q_data_acquisition_status)

        self.update_gui_params(self.global_data_acquisition_parameter)

        self.saver = DataSaver(self.x, self.y, self.pixel_size, self.acquisition_time, self.project_name,
                               self.file_name, self.operator, self.localisation)


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

    def data_consumer(self, data_point, line_finished, acquisition_completed):
        p_mapping = Process(target=self.global_data_acquisition_parameter.analyse_type,
                            args=(self.q_data_acquisition_status,))
                            # args=(*self.global_data_acquisition_parameter.arg_data_acquisition,)), self.optical_spectrometer_1, self.motor
        p_mapping.start()
        time.sleep(0.1)
        while self.data_acquisition_status[0]:
            self.data_acquisition_status = self.q_data_acquisition_status.get()
            if self.data_acquisition_status[0]:
                shm = SharedMemory(name=self.global_data_acquisition_parameter.name_shm)
                datacube = np.ndarray(self.global_data_acquisition_parameter.datacube_shape,
                                      dtype=np.uint32, buffer=shm.buf)
                self.global_data_acquisition_parameter.datacube = np.copy(datacube)


                data_point.emit(self.global_data_acquisition_parameter.datacube)
                if self.data_acquisition_status[2] == (self.global_data_acquisition_parameter.pixel_number() - 1) :
                    # print('progress line')
                    line_finished.emit(self.data_acquisition_status[1], self.global_data_acquisition_parameter.line_number())
                    self.saver.backup_line_saver(self.global_data_acquisition_parameter.datacube[self.data_acquisition_status[1], :, :],
                                                 self.data_acquisition_status[1])

        shm.close()
        shm.unlink()
        p_mapping.join()
        p_mapping.terminate()
        # line_finished.emit(self.data_acquisition_status[1], self.global_data_acquisition_parameter.line_number())
        time.sleep(0.1)
        acquisition_completed.emit()

    def acquisition_completed(self):
        QMessageBox.information(self, "Information", "Data Acquisition Complete", QMessageBox.Ok)
        self.push_button_start.setEnabled(True)
        self.push_button_stop.setEnabled(False)
        self.run_counter +=1


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

        self.saver.backup_directory_cleaner()

        self.update_params()

        analyse_info = self.saver.analyse_info_builder(self.global_data_acquisition_parameter.analyse_mode_map,
                                                       self.global_data_acquisition_parameter.analyse_mode_point,
                                                       self.global_data_acquisition_parameter.data_acquisition_xrf,
                                                       self.global_data_acquisition_parameter.data_acquisition_ris_lis,
                                                       self.global_data_acquisition_parameter.data_acquisition_swir)
        self.analyse_list.append(analyse_info)
        self.cfg = self.saver.config_builder(self.analyse_list)
        self.saver.config_saver(self.cfg)

        thread_acquisition = ThreadMap(self.data_consumer)
        thread_acquisition.signals.progress.connect(self.update_image_view)
        thread_acquisition.signals.line_finished.connect(self.update_progressbar)
        thread_acquisition.signals.completed.connect(self.acquisition_completed)

        self.threadpool.start(thread_acquisition)
        self.data_acquisition_status = (True, 0, 0)

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

    @pyqtSlot(int)
    def on_spinbox_low_map1_valueChanged(self):
        self.update_image_view(self.global_data_acquisition_parameter.datacube)

    @pyqtSlot(int)
    def on_spinbox_low_map2_valueChanged(self):
        self.update_image_view(self.global_data_acquisition_parameter.datacube)

    @pyqtSlot(int)
    def on_spinbox_low_map3_valueChanged(self):
        self.update_image_view(self.global_data_acquisition_parameter.datacube)

    @pyqtSlot(int)
    def on_spinbox_low_map4_valueChanged(self):
        self.update_image_view(self.global_data_acquisition_parameter.datacube)

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
    def on_push_button_connect_xrf_clicked(self):
        try:
            self.x_ray_detector.connect_xrf_spectrometer()
            self.checkbox_xrf_connected.setCheckState(True)
            QMessageBox.information(self, "Information", 'Detector connected', QMessageBox.Ok)
        except Exception as e:
            QMessageBox.warning(self, "Warning", 'No device connected\n Detail: ' + str(e), QMessageBox.Ok)

    @pyqtSlot()
    def on_push_button_connect_ris_lis_clicked(self):
        try:
            self.optical_spectrometer_1.connect_optical_spectrometer()
            self.checkbox_ris_lis_connected.setCheckState(True)
            QMessageBox.information(self, "Information", 'Spectrometer connected', QMessageBox.Ok)
        except Exception as e:
            QMessageBox.warning(self, "Warning", 'No device connected\n Detail: ' + str(e), QMessageBox.Ok)

    @pyqtSlot()
    def on_push_button_connect_motor_clicked(self):
        try:
            self.motor.connect_motor()
            self.slider_motorspeed_x.setValue(7)
            self.slider_motorspeed_y.setValue(7)
            self.slider_motorspeed_z.setValue(7)
            self.checkbox_motor_connected.setCheckState(True)
            QMessageBox.information(self, "Information", 'Linear stages connected', QMessageBox.Ok)
        except Exception as e:
            QMessageBox.warning(self, "Warning", str(e), QMessageBox.Ok)


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

    @pyqtSlot()
    def on_push_button_move_up_clicked(self):
        try:
            factor = 1
            if self.combobox_scale.currentText() == 'cm':
                factor = 10000
            elif self.combobox_scale.currentText() == 'mm':
                factor = 1000
            elif self.combobox_scale.currentText() == 'µm':
                factor = 1
            move = float(self.line_edit_travel_distance.text()) * factor
            self.motor.move_Y(-move, self.motor_speed_y, False)
        except Exception as e:
            QMessageBox.warning(self, "Warning", str(e), QMessageBox.Ok)

    @pyqtSlot()
    def on_push_button_move_down_clicked(self):
        try:
            factor = 1
            if self.combobox_scale.currentText() == 'cm':
                factor = 10000
            elif self.combobox_scale.currentText() == 'mm':
                factor = 1000
            elif self.combobox_scale.currentText() == 'µm':
                factor = 1
            move = float(self.line_edit_travel_distance.text()) * factor
            self.motor.move_Y(move, self.motor_speed_y, False)
        except Exception as e:
            QMessageBox.warning(self, "Warning", str(e), QMessageBox.Ok)

    @pyqtSlot()
    def on_push_button_move_left_clicked(self):
        try:
            factor = 1
            if self.combobox_scale.currentText() == 'cm':
                factor = 10000
            elif self.combobox_scale.currentText() == 'mm':
                factor = 1000
            elif self.combobox_scale.currentText() == 'µm':
                factor = 1
            move = float(self.line_edit_travel_distance.text()) * factor
            self.motor.move_X(-move, self.motor_speed_y, False)
        except Exception as e:
            QMessageBox.warning(self, "Warning", str(e), QMessageBox.Ok)

    @pyqtSlot()
    def on_push_button_move_right_clicked(self):
        try:
            factor = 1
            if self.combobox_scale.currentText() == 'cm':
                factor = 10000
            elif self.combobox_scale.currentText() == 'mm':
                factor = 1000
            elif self.combobox_scale.currentText() == 'µm':
                factor = 1
            move = float(self.line_edit_travel_distance.text()) * factor
            self.motor.move_X(move, self.motor_speed_y, False)
        except Exception as e:
            QMessageBox.warning(self, "Warning", str(e), QMessageBox.Ok)

    @pyqtSlot()
    def on_push_button_move_forward_clicked(self):
        try:
            factor = 1
            if self.combobox_scale.currentText() == 'cm':
                factor = 10000
            elif self.combobox_scale.currentText() == 'mm':
                factor = 1000
            elif self.combobox_scale.currentText() == 'µm':
                factor = 1
            move = float(self.line_edit_travel_distance.text()) * factor
            self.motor.move_Z(move, self.motor_speed_y, False)
        except Exception as e:
            QMessageBox.warning(self, "Warning", str(e), QMessageBox.Ok)

    @pyqtSlot()
    def on_push_button_move_backward_clicked(self):
        try:
            factor = 1
            if self.combobox_scale.currentText() == 'cm':
                factor = 10000
            elif self.combobox_scale.currentText() == 'mm':
                factor = 1000
            elif self.combobox_scale.currentText() == 'µm':
                factor = 1
            move = float(self.line_edit_travel_distance.text()) * factor
            self.motor.move_Z(-move, self.motor_speed_y, False)
        except Exception as e:
            QMessageBox.warning(self, "Warning", str(e), QMessageBox.Ok)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    MainWindow = Master()
    MainWindow.show()
    rc = app.exec_()
    sys.exit(rc)