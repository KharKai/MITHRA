import time
import numpy as np

from multiprocessing.shared_memory import SharedMemory

from core_app.controllers_TOREMOVE.controller_Amptek import mca8000d
from core_app.controllers_TOREMOVE.controller_QePro import qepro

from core_app.utils.mapping_parameters import MappingParameters


class Data(MappingParameters):
    def __init__(self, *args, **kwargs):
        super(Data, self).__init__(*args, **kwargs)

        MappingParameters(1, 1, 500, 80)

        self.spectrum_xrf = np.zeros(512)
        self.spectrum_ris = np.zeros(1044)
        self.spectrum_lis1 = np.zeros(1044)
        self.spectrum_lis2 = np.zeros(1044)
        self.spectrum_lis3 = np.zeros(1044)
        self.spectrum_swir = [0, 0]

        self.datacube_xrf = np.zeros((self.line_number(), self.pixel_number(), 511))
        self.datacube_ris_lis = np.zeros((self.line_number(), self.pixel_number() * 4, 1044))

        self.white_spectrum = np.zeros(1044)
        self.dark_spectrum = np.zeros(1044)


class DataAcquisition(Data):
    def __init__(self, *args, **kwargs):
        super(DataAcquisition, self).__init__(*args, **kwargs)

        self.sh_mem_xrf = SharedMemory(create=True, size=2048 * self.pixel_number(), name='shared_memory_xrf')
        self.sh_mem_ris_lis = SharedMemory(create=True, size=2048 * 4 * self.pixel_number(), name='shared_memory_ris_lis')

    def point_xrf(self, acquisition_time, x_ray_detector, single_point=True):
        if single_point:
            start = time.perf_counter()
        else:
            pass
        end = time.perf_counter()
        clock = end - start
        while clock < acquisition_time:
            end = time.perf_counter()
            clock = end - start
        start = time.perf_counter()
        self.spectrum_xrf = x_ray_detector.spectrum(True, False)
        return

    def line_xrf(self, acquisition_time, pixel_number, x_ray_detector):
        sh_mem_xrf = SharedMemory(create=True, size=2048 * self.pixel_number(), name='shared_memory_xrf')
        line_xrf_buffer = np.ndarray((pixel_number, 512), dtype=np.uint32, buffer=sh_mem_xrf.buf)
        i = 0
        start = time.perf_counter()
        while i < pixel_number:
            end = time.perf_counter()
            clock = end - start
            while clock < acquisition_time:
                end = time.perf_counter()
                clock = end - start
            start = time.perf_counter()
            xrf_spectrum = x_ray_detector.spectrum(True, True)[0] # Careful that XRF array is uint32
            line_xrf_buffer[i, :] = xrf_spectrum
        sh_mem_xrf.close()
        sh_mem_xrf.unlink()

    def line_ris_lis(self, acquisition_time, pixel_number, optical_spectrometer):
        pass

    def line_swir(self, acquisition_time, pixel_number, optical_spectrometer):
        pass

    def mapping_xrf(self, acquisition_time, pixel_number, line_number, x_ray_detector):
        i = 0
        while i < line_number:

            self.line_xrf(acquisition_time, pixel_number, x_ray_detector)
        pass

    def mapping_ris_lis(self):
        pass

    def mapping_swir(self):
        pass

    def mapping_xrf_ris_lis(self):
        pass



