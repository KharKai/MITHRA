import os
import sys
from importlib.metadata import metadata

import pickle
import json

import numpy as np

from datetime import datetime

# from core_app.MITHRA_utils.acquisition_parameters import AcquisitionParameters

import h5py as h5
import PyMca5.PyMcaIO.EdfFile as edf

from core_app.MITHRA_utils.data_acquisition import DataAcquisition


class DataSaver(DataAcquisition):
    def __init__(self, *args, **kwargs):
        super(DataSaver, self).__init__(*args, **kwargs)
        self.hdf5 = bool
        self.edf = bool
        self.raw = bool

    def build_metadata(self, xrf=False, ris_lis=False, swir=False):
        pass

    def analyse_info_builder(self, mode_map, mode_point, data_acquisition_xrf, data_acquisition_ris_lis, data_acquisition_swir):
        analyse_list = {"analyse name": self.filename,
                                    "analyse type": {'map': mode_map, 'point': mode_point},
                                    "analyse mode": {'xrf': data_acquisition_xrf,
                                                     'ris_lis': data_acquisition_ris_lis,
                                                     'swir': data_acquisition_swir},
                                    "date": datetime.today().strftime('%Y-%m-%d %H:%M:%S'),
                                    "mapping parameters":{"x": self.x,
                                                          "y": self.y,
                                                          "pixel_size": self.pixel_size,
                                                          "acquisition_time": self.acquisition_time,
                                                          "total duration": self.mapping_duration_str()}}
        return analyse_list

    def config_builder(self, analyse_list):
        config = {"project info": {"name": self.path,
                                   "operator": self.operator,
                                   "localisation": self.localisation},
                  "analyse list": analyse_list,

                  }
        return config

    def metadata_xrf(self, v, mA, comments):
        metadata_xrf = {'operator': self.operator, 'localisation': self.localisation, 'size x': self.x, 'size y': self.y,
                    'resolution': self.pixel_size, 'acquisition time': self.acquisition_time,
                    'mapping duration': self.mapping_duration_str(),
                    'X Ray Tube device': 'Micro-focus X-ray source iMOXS with power supply CSU', 'X Ray kV': v, 'X Ray mA': mA,
                    'X Ray Detector': 'Amptek FastSDD 123', 'comments': comments}
        # TODO implement detector and tube info as dict
        return metadata_xrf

    def metadata_ris_lis(self, comments):
        metadata_ris_lis = {'operator': self.operator, 'localisation': self.localisation, 'size x': self.x, 'size y': self.y,
                            'resolution': self.pixel_size, 'acquisition time': self.acquisition_time,
                            'mapping duration': self.mapping_duration_str(),
                            'Source1': '', 'Source2': '', 'Source3': '', 'Source4': '',
                            'Optical Spectrometer device':'QePro OceanInsight', 'grating': '', 'slit':'',
                            'comments': comments}
        # TODO implement spectro and tube info as dict
        return metadata_ris_lis

    def metadata_swir(self, comments):
        metadata_ris_lis = {'operator': self.operator, 'localisation': self.localisation, 'size x': self.x, 'size y': self.y,
                            'Source1': '',
                            'Source2': '', 'Source3': '', 'Source4': '',
                            'resolution': self.pixel_size, 'acquisition time': self.acquisition_time,
                            'mapping duration': self.mapping_duration_str(),
                            'Source': '',
                            'Optical Spectrometer device': 'Avantes', 'grating': '', 'slit': '',
                            'comments': comments}
        # TODO implement spectro info as dict
        return metadata_ris_lis

    def save_as(self, hdf5, edf, raw, data_xrf, data_ris, data_lis1, data_lis2, data_lis3, data_swir, comments):
        if hdf5:
            self.hdf5_saver(data_xrf, data_ris, data_lis1, data_lis2, data_lis3, data_swir, comments)
        if edf:
            self.edf_saver(data_xrf, data_ris, data_lis1, data_lis2, data_lis3, data_swir, comments)
        if raw:
            self.raw_saver(data_xrf, data_ris, data_lis1, data_lis2, data_lis3, data_swir, comments)

    def hdf5_saver(self, data_xrf=None, data_ris=None, data_lis1=None, data_lis2=None, data_lis3=None, data_swir=None, comments=''):
        f = h5.File(self.path + '\\' + self.filename + '_data.h5', 'w')
        if data_xrf is not None:
            m_xrf = self.metadata_xrf(self.V, self.mA, comments)
            map_xrf = f.create_group('map xrf')
            for k in m_xrf.keys():
                map_xrf.attrs[k] = m_xrf[k]
            map_xrf.create_dataset('data xrf', shape=data_xrf.shape, data=data_xrf)
            map_xrf.create_dataset('calibration', data=self.calibration_xrf)

        if data_ris is not None:
            m_ris_lis = self.metadata_ris_lis(comments)
            map_ris_lis = f.create_group('map ris lis')
            for k in m_ris_lis.keys():
                map_ris_lis.attrs[k] = m_ris_lis[k]
            map_ris_lis.create_dataset('data ris', shape=data_ris.shape, data=data_ris)
            map_ris_lis.create_dataset('data lis1', shape=data_lis1.shape, data=data_lis1)
            map_ris_lis.create_dataset('data lis2', shape=data_lis2.shape, data=data_lis2)
            map_ris_lis.create_dataset('data lis3', shape=data_lis3.shape, data=data_lis3)

            map_ris_lis.create_dataset('calibration', data=self.calibration_ris_lis)

        if data_swir is not None:
            m_swir = self.metadata_swir(comments)
            map_swir = f.create_group('map swir')
            for k in m_swir.keys():
                map_swir.attrs[k] = m_swir[k]
            map_swir.create_dataset('data swir', shape=data_swir.shape, data=data_swir)

    def edf_saver(self, data_xrf=None, data_ris=None, data_lis1=None, data_lis2=None, data_lis3=None, data_swir=None, comments=''):
        pass

    def raw_saver(self, data_xrf=None, data_ris=None, data_lis1=None, data_lis2=None, data_lis3=None, data_swir=None, comments=''):
        pass

    def config_saver(self, cfg):
        json.dump(cfg, open(self.path + '\\' + datetime.today().strftime('%Y-%m-%d') + '_MITHRA.cfg', 'w'), indent=4)

    def backup_line_saver(self, data, line_number):
        # map = edf.EdfFile('G:\\DATA\\PyCharm Projects\\MITHRA\\temp\\BackupFiles\\backup_inprogress_'
        #                   + str(line_number) + '.edf', access="ab+")

        map = edf.EdfFile('C:\\DATA\\MITHRA\\temp\\BackupFiles\\backup_inprogress_'
                          + str(line_number) + '.edf', access="ab+")

        map.WriteImage({}, data, Append=0)

    def backup_directory_cleaner(self):
        # path = 'G:\\DATA\\PyCharm Projects\\MITHRA\\temp\\BackupFiles\\'
        path = 'C:\\DATA\\MITHRA\\temp\\BackupFiles\\'
        for f in os.listdir(path):
            file = path + f
            if os.path.isfile(file):
                os.remove(file)


# saver = DataSaver(1, 1, 500, 80, 'G:\DATA\PyCharm Projects\MITHRA\core_app', 'test_final', 'Raph', 'Antre du C2RMF')
# test = saver.build_config()
# print(test)
# saver.save_cfg(test)