import sys
import time
import numpy as np

from multiprocessing.shared_memory import SharedMemory

from core_app.controllers_TOREMOVE.controller_Amptek import mca8000d
from core_app.controllers_TOREMOVE.controller_QePro import qepro
from core_app.controllers_TOREMOVE.controller_Owis import owis

from core_app.MITHRA_utils.acquisition_parameters import AcquisitionParameters


class Data(AcquisitionParameters):
    def __init__(self, *args, **kwargs):
        super(Data, self).__init__(*args, **kwargs)

        self.spectrum_xrf = np.zeros(512)
        self.spectrum_ris = np.zeros(1044)
        self.spectrum_lis1 = np.zeros(1044)
        self.spectrum_lis2 = np.zeros(1044)
        self.spectrum_lis3 = np.zeros(1044)
        self.spectrum_swir = np.zeros(256)

        self.datacube = np.ndarray

        self.datacube_xrf = np.zeros((self.line_number(), self.pixel_number(), 512))
        self.datacube_ris_lis = np.zeros((self.line_number(), self.pixel_number(), 1044 * 4))
        self.datacube_swir = np.zeros((self.line_number(), self.pixel_number(), 256))

        self.datacube_shape = (self.line_number(), self.pixel_number(), 0)

        self.white_spectrum = np.zeros(1044)
        self.dark_spectrum = np.zeros(1044)


class DataAcquisition(Data):
    def __init__(self, *args, **kwargs):
        super(DataAcquisition, self).__init__(*args, **kwargs)

        self.analyse_type = None
        self.name_shm: str = ''
        self.arg_data_acquisition:tuple = ()

        self.analyse_mode_map = True
        self.analyse_mode_point = False

        self.data_acquisition_xrf = True
        self.data_acquisition_ris_lis = False
        self.data_acquisition_swir = False


    def data_acquisition_type_and_mode(self, q_data_acquisition_status):#, x_ray_detector, optical_spectrometer_1, optical_spectrometer_2, motor
        if self.analyse_mode_map:
            if self.data_acquisition_xrf and self.data_acquisition_ris_lis and self.data_acquisition_swir:
                self.analyse_type = self.mapping_xrf_ris_lis_swir
                self.arg_data_acquisition = (q_data_acquisition_status, )
                self.name_shm = 'shared_memory_xrf_ris_lis_swir'
                shape = list(self.datacube_shape)
                shape[2] = 512 + 1044 * 4 + 256
                self.datacube_shape = tuple(shape)
                print('xrf ris lis swir selected')

            elif self.data_acquisition_xrf and self.data_acquisition_ris_lis:
                self.analyse_type = self.mapping_xrf_ris_lis
                self.arg_data_acquisition = (q_data_acquisition_status,)
                self.name_shm = 'shared_memory_xrf_ris_lis'
                shape = list(self.datacube_shape)
                shape[2] = 512 + 1044 * 4
                self.datacube_shape = tuple(shape)
                print('xrf ris lis selected')

            elif self.data_acquisition_xrf and self.data_acquisition_swir:
                self.analyse_type = self.mapping_xrf_swir
                self.arg_data_acquisition = (q_data_acquisition_status,)
                self.name_shm = 'shared_memory_xrf_swir'
                shape = list(self.datacube_shape)
                shape[2] = 512 + 256
                self.datacube_shape = tuple(shape)
                print('xrf swir selected')

            elif self.data_acquisition_ris_lis and self.data_acquisition_swir:
                self.analyse_type = self.mapping_ris_lis_swir
                self.arg_data_acquisition = (q_data_acquisition_status,)
                self.name_shm = 'shared_memory_ris_lis_swir'
                shape = list(self.datacube_shape)
                shape[2] = 1044 * 4 + 256
                self.datacube_shape = tuple(shape)
                print('ris lis swir selected')

            elif self.data_acquisition_xrf:
                self.analyse_type = self.mapping_xrf
                self.arg_data_acquisition = (q_data_acquisition_status,)
                self.name_shm = 'shared_memory_xrf'
                shape = list(self.datacube_shape)
                shape[2] = 512
                self.datacube_shape = tuple(shape)
                print('xrf selected')

            elif self.data_acquisition_ris_lis:
                self.analyse_type = self.mapping_ris_lis
                self.arg_data_acquisition = (q_data_acquisition_status,)
                self.name_shm = 'shared_memory_ris_lis'
                shape = list(self.datacube_shape)
                shape[2] = 1044 * 4
                self.datacube_shape = tuple(shape)
                print('ris lis selected')

            elif self.data_acquisition_swir:
                self.analyse_type = self.mapping_swir
                self.arg_data_acquisition = (q_data_acquisition_status,)
                self.name_shm = 'shared_memory_swir'
                shape = list(self.datacube_shape)
                shape[2] = 256
                self.datacube_shape = tuple(shape)
                print('swir selected')

        elif self.analyse_mode_point:
            pass


    def point_xrf(self, acquisition_time, x_ray_detector):
        start = time.perf_counter()
        end = time.perf_counter()
        clock = end - start
        while clock < (acquisition_time / 1000):
            end = time.perf_counter()
            clock = end - start
        self.spectrum_xrf = x_ray_detector.spectrum(True, False)
        return

    def point_ris_lis(self, acquisition_time, optical_spectrometer_1):
        pass

    def point_swir(self, acquisition_time, optical_spectrometer_2):
        pass

    def mapping_xrf_ris_lis_swir(self, q_status, x_ray_detector, optical_spectrometer1, optical_spectrometer_2, motor):
        pass

    def mapping_xrf_ris_lis(self, q_status):
        line = self.line_number()
        pixel = self.pixel_number()

        x_ray_detector = mca8000d.Device()
        x_ray_detector.connect_xrf_spectrometer()

        optical_spectrometer_1 = qepro.Device()
        optical_spectrometer_1.connect_optical_spectrometer()

        motor = owis.MotorOwis()
        motor.connect_motor()

        try:
            sh_mem_xrf_ris_lis = SharedMemory(create=True, size=(1044 * 16 + 2048) * pixel * line, name='shared_memory_xrf_ris_lis')
        except FileExistsError:
            sh_mem_xrf_ris_lis = SharedMemory(name='shared_memory_xrf_ris_lis')
        map_xrf_ris_lis_buffer = np.ndarray((line, pixel, 1044 * 4 + 512), dtype=np.uint32, buffer=sh_mem_xrf_ris_lis.buf)

        optical_spectrometer_1.set_integration_time(int(self.acquisition_time / 4))
        optical_spectrometer_1.set_single_strobe(1)
        optical_spectrometer_1.set_single_strobe_width(2000)  # in microsec
        optical_spectrometer_1.set_single_strobe_width(int(((self.acquisition_time / 4) - 4) * 1000))

        # x_ray_detector.spectrum(True, True)
        # x_ray_detector.enable_MCA_MCS()

        i = 0
        while i < line:
            j = 0
            optical_spectrometer_1.clear_buffer()

            # if i % 2 == 0:
            #     motor.move_X((self.x * 10000), self.motor_speed(), idle=False)
            # if i % 2 == 1:
            #     motor.move_X(-(self.x * 10000), self.motor_speed(), idle=False)

            optical_spectrometer_1.start_acq()
            while j < pixel:
                optical_spectrum_1 = optical_spectrometer_1.get_spectrum()[0]
                optical_spectrum_2 = optical_spectrometer_1.get_spectrum()[0]
                optical_spectrum_3 = optical_spectrometer_1.get_spectrum()[0]
                optical_spectrum_4 = optical_spectrometer_1.get_spectrum()[0]
                xrf_spectrum = x_ray_detector.spectrum(True, True)[0]# Careful that XRF array is uint32
                if i % 2 == 0:
                    map_xrf_ris_lis_buffer[i, j, :1044] = optical_spectrum_1
                    map_xrf_ris_lis_buffer[i, j, 1044:2088] = optical_spectrum_2
                    map_xrf_ris_lis_buffer[i, j, 2088:3132] = optical_spectrum_3
                    map_xrf_ris_lis_buffer[i, j, 3132:4176] = optical_spectrum_4
                    map_xrf_ris_lis_buffer[i, j, 4176:] = xrf_spectrum
                if i % 2 == 1:
                    map_xrf_ris_lis_buffer[i, -j-1, :1044] = optical_spectrum_1
                    map_xrf_ris_lis_buffer[i, -j-1, 1044:2088] = optical_spectrum_2
                    map_xrf_ris_lis_buffer[i, -j-1, 2088:3132] = optical_spectrum_3
                    map_xrf_ris_lis_buffer[i, -j-1, 3132:4176] = optical_spectrum_4
                    map_xrf_ris_lis_buffer[i, -j-1, 4176:] = xrf_spectrum
                q_status.put((True, i, j))
                j += 1
            optical_spectrometer_1.set_lamp_enable(1)
            optical_spectrometer_1.start_acq()
            optical_spectrometer_1.get_spectrum()
            optical_spectrometer_1.abort_acq()
            optical_spectrometer_1.set_lamp_enable(0)
            i += 1
            time.sleep(1)

        q_status.put((False, i, j))
        sh_mem_xrf_ris_lis.close()
        time.sleep(1)
        sh_mem_xrf_ris_lis.unlink()




    def mapping_xrf_swir(self, q_status, x_ray_detector, optical_spectrometer1, optical_spectrometer_2, motor):
        pass

    def mapping_ris_lis_swir(self, q_status, x_ray_detector, optical_spectrometer1, optical_spectrometer_2, motor):
        pass

    def mapping_xrf(self,  q_status):
        line = self.line_number()
        pixel = self.pixel_number()

        x_ray_detector = mca8000d.Device()
        x_ray_detector.connect_xrf_spectrometer()

        motor = owis.MotorOwis()
        motor.connect_motor()

        try:
            sh_mem_xrf = SharedMemory(create=True, size=2048 * pixel * line, name='shared_memory_xrf')
        except FileExistsError:
            sh_mem_xrf = SharedMemory(name='shared_memory_xrf')
        map_xrf_buffer = np.ndarray((line, pixel, 512), dtype=np.uint32, buffer=sh_mem_xrf.buf)

        # x_ray_detector.spectrum(True, True)
        # x_ray_detector.enable_MCA_MCS()

        i = 0
        while i < line:
            j = 0

            # if i % 2 == 0:
            #     motor.move_X((self.x * 10000), self.motor_speed(), idle=False)
            # if i % 2 == 1:
            #     motor.move_X(-(self.x * 10000), self.motor_speed(), idle=False)

            start = time.perf_counter()
            while j < pixel:
                end = time.perf_counter()
                clock = end - start
                while clock < (self.acquisition_time /1000):
                    end = time.perf_counter()
                    clock = end - start
                start = time.perf_counter()
                # xrf_spectrum = x_ray_detector.spectrum(True, True)[0] # Careful that XRF array is uint32
                xrf_spectrum = np.random.randint(0, 1000, 512, dtype=np.uint32)
                if i % 2 ==0:
                    map_xrf_buffer[i, j, :] = xrf_spectrum
                elif i%2 ==1:
                    map_xrf_buffer[i, -j-1, :] = xrf_spectrum
                q_status.put((True, i, j))
                j += 1
            i+=1
            time.sleep(1)

        q_status.put((False, i, j))
        sh_mem_xrf.close()
        time.sleep(1)
        sh_mem_xrf.unlink()

    def mapping_ris_lis(self, q_status):#, optical_spectrometer_1, motor
        line = self.line_number()
        pixel = self.pixel_number()

        optical_spectrometer_1 = qepro.Device()
        optical_spectrometer_1.connect_optical_spectrometer()

        motor = owis.MotorOwis()
        motor.connect_motor()

        try:
            sh_mem_ris_lis = SharedMemory(create=True, size=1044 * 16 * pixel * line,
                                              name='shared_memory_ris_lis')
        except FileExistsError:
            sh_mem_ris_lis = SharedMemory(name='shared_memory_ris_lis')
        map_ris_lis_buffer = np.ndarray((line, pixel, 1044 * 4), dtype=np.uint32,buffer=sh_mem_ris_lis.buf)


        optical_spectrometer_1.set_integration_time(int(self.acquisition_time / 4))
        optical_spectrometer_1.set_single_strobe(1)
        optical_spectrometer_1.set_single_strobe_width(2000)  # in microsec
        optical_spectrometer_1.set_single_strobe_width(int(((self.acquisition_time / 4) - 4) * 1000))

        i = 0
        while i < line:
            j = 0
            optical_spectrometer_1.clear_buffer()

            # if i % 2 == 0:
            #     motor.move_X((self.x * 10000), self.motor_speed(), idle=False)
            # if i % 2 == 1:
            #     motor.move_X(-(self.x * 10000), self.motor_speed(), idle=False)

            optical_spectrometer_1.start_acq()
            while j < pixel:
                optical_spectrum_1 = optical_spectrometer_1.get_spectrum()[0]
                optical_spectrum_2 = optical_spectrometer_1.get_spectrum()[0]
                optical_spectrum_3 = optical_spectrometer_1.get_spectrum()[0]
                optical_spectrum_4 = optical_spectrometer_1.get_spectrum()[0]

                # optical_spectrum_1 = np.random.randint(0, 1000, 1044, dtype=np.uint32) #
                # time.sleep(0.02)
                # optical_spectrum_2 = np.random.randint(0, 1000, 1044, dtype=np.uint32) #
                # time.sleep(0.02)
                # optical_spectrum_3 = np.random.randint(0, 1000, 1044, dtype=np.uint32) #
                # time.sleep(0.02)
                # optical_spectrum_4 = np.random.randint(0, 1000, 1044, dtype=np.uint32) #
                # time.sleep(0.02)
                if i % 2 == 0:
                    map_ris_lis_buffer[i, j, :1044] = optical_spectrum_1
                    map_ris_lis_buffer[i, j, 1044:2088] = optical_spectrum_2
                    map_ris_lis_buffer[i, j, 2088:3132] = optical_spectrum_3
                    map_ris_lis_buffer[i, j, 3132:] = optical_spectrum_4

                if i % 2 == 1:
                    map_ris_lis_buffer[i, -j - 1, :1044] = optical_spectrum_1
                    map_ris_lis_buffer[i, -j - 1, 1044:2088] = optical_spectrum_2
                    map_ris_lis_buffer[i, -j - 1, 2088:3132] = optical_spectrum_3
                    map_ris_lis_buffer[i, -j - 1, 3132:] = optical_spectrum_4
                q_status.put((True, i, j))
                j += 1
            optical_spectrometer_1.set_lamp_enable(1)
            optical_spectrometer_1.start_acq()
            optical_spectrometer_1.get_spectrum()
            optical_spectrometer_1.abort_acq()
            optical_spectrometer_1.set_lamp_enable(0)
            i += 1
            time.sleep(1)

        q_status.put((False, i, j))
        sh_mem_ris_lis.close()
        time.sleep(1)
        sh_mem_ris_lis.unlink()

    def mapping_swir(self):
        pass







