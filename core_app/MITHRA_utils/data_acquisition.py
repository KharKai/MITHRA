import time
import numpy as np

from multiprocessing.shared_memory import SharedMemory

from core_app.controllers_TOREMOVE.controller_Amptek import mca8000d
from core_app.controllers_TOREMOVE.controller_QePro import qepro

from core_app.MITHRA_utils.acquisition_parameters import AcquisitionParameters


class Data(AcquisitionParameters):
    def __init__(self, *args, **kwargs):
        super(Data, self).__init__(*args, **kwargs)

        self.spectrum_xrf = np.zeros(512)
        self.spectrum_ris = np.zeros(1044)
        self.spectrum_lis1 = np.zeros(1044)
        self.spectrum_lis2 = np.zeros(1044)
        self.spectrum_lis3 = np.zeros(1044)
        self.spectrum_swir = [0, 0]

        self.datacube_xrf = np.zeros((self.line_number(), self.pixel_number(), 512))
        self.datacube_ris_lis = np.zeros((self.line_number(), self.pixel_number() * 4, 1044))

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


    def data_acquisition_type_and_mode(self, q_data_acquisition_status, x_ray_detector, optical_spectrometer_1, optical_spectrometer_2, motor):
        if self.analyse_mode_map:
            if self.data_acquisition_xrf and self.data_acquisition_ris_lis and self.data_acquisition_swir:
                self.analyse_type = self.mapping_xrf_ris_lis_swir

            elif self.data_acquisition_xrf and self.data_acquisition_ris_lis:
                self.analyse_type = self.mapping_xrf_ris_lis
            elif self.data_acquisition_xrf and self.data_acquisition_swir:
                self.analyse_type = self.mapping_swir
            elif self.data_acquisition_ris_lis and self.data_acquisition_swir:
                self.analyse_type = self.mapping_ris_lis_swir

            elif self.data_acquisition_xrf:
                self.analyse_type = self.mapping_xrf
                self.arg_data_acquisition = (q_data_acquisition_status, x_ray_detector, motor,)
                self.name_shm = 'shared_memory_xrf'
            elif self.data_acquisition_ris_lis:
                self.analyse_type = self.mapping_ris_lis
                self.arg_data_acquisition = (q_data_acquisition_status, x_ray_detector, motor,)
                self.name_shm = 'shared_memory_ris_lis'
            elif self.data_acquisition_swir:
                self.analyse_type = self.mapping_swir
                self.arg_data_acquisition = (q_data_acquisition_status, x_ray_detector, motor,)
                self.name_shm = 'shared_memory_swir'

        elif self.analyse_mode_point:
            pass


    def point_xrf(self, acquisition_time, x_ray_detector, single_point=True):
        if single_point:
            start = time.perf_counter()
        else:
            pass
        end = time.perf_counter()
        clock = end - start
        while clock < (acquisition_time / 1000):
            end = time.perf_counter()
            clock = end - start
        self.spectrum_xrf = x_ray_detector.spectrum(True, False)
        return

    def mapping_xrf_ris_lis_swir(self, q_status, x_ray_detector, motor):
        pass

    def mapping_xrf_ris_lis(self):
        pass

    def mapping_xrf_swir(self):
        pass

    def mapping_ris_lis_swir(self):
        pass

    def mapping_xrf(self,  q_status, x_ray_detector, motor):# acquisition_time, pixel_number, line_number,
        line = self.line_number()
        pixel = self.pixel_number()
        try:
            sh_mem_xrf = SharedMemory(create=True, size=2048 * pixel * line, name='shared_memory_xrf')
        except FileExistsError:
            sh_mem_xrf = SharedMemory(name='shared_memory_xrf')
        map_xrf_buffer = np.ndarray((line, pixel, 512), dtype=np.uint32, buffer=sh_mem_xrf.buf)
        i = 0
        while i < line:
            j = 0
            # q_status.put(True, i, j)
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

            #self.datacube_xrf[i, :, :] = line_xrf_buffer
            i+=1
            time.sleep(1)

        q_status.put((False, i, j))
        sh_mem_xrf.close()
        time.sleep(1)
        sh_mem_xrf.unlink()
        print('done acquisition')

    def mapping_ris_lis(self):
        pass

    def mapping_swir(self):
        pass







