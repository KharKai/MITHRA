import os
import sys
from importlib.metadata import metadata

import numpy as np

from core_app.utils.mapping_parameters import MappingParameters

import h5py as h5
import PyMca5.PyMcaIO.EdfFile as edf



class DataSaving(MappingParameters):
    def __init__(self, path, filename, operator, location, *args, **kwargs):
        super(DataSaving, self).__init__(*args, **kwargs)

        self.path: str = path
        self.filename: str = filename

        self.operator: str = operator
        self.location: str = location

    def build_metadata(self, xrf=False, ris_lis=False, swir=False):

        pass

    def build_config(self):
        config = {"project info": {"name": self.filename,
                                   "operator": self.operator,
                                   "localisation": self.location,},
                  "mapping parameters":{"x": self.x,
                                        "y": self.y,
                                        "pixel_size": self.pixel_size,
                                        "acquisition_time": self.acquisition_time},}
        return config

    def metadata_xrf(self, v, mA, comments):
        metadata_xrf = {'operator': self.operator, 'location': self.location, 'size x': self.x, 'size y': self.y,
                    'resolution': self.pixel_size, 'acquisition time': self.acquisition_time,
                    'mapping duration': self.mapping_duration_str(),
                    'X Ray Tube': {'device': 'Micro-focus X-ray source iMOXS with power supply CSU', 'X Ray kV': v, 'X Ray mA': mA},
                    'X Ray Detector': 'Amptek FastSDD 123', 'comments': comments}
        # TODO implement detector and tube info as dict
        return metadata_xrf

    def metadata_ris_lis(self, comments):
        metadata_ris_lis = {'operator': self.operator, 'location': self.location, 'size x': self.x, 'size y': self.y,
                            'resolution': self.pixel_size, 'acquisition time': self.acquisition_time,
                            'mapping duration': self.mapping_duration_str(),
                            'Source1': '', 'Source2': '', 'Source3': '', 'Source4': '',
                            'Optical Spectrometer': {'device':'QePro OceanInsight', 'grating': '', 'slit':''},
                            'comments': comments}
        # TODO implement spectro and tube info as dict
        return metadata_ris_lis

    def metadata_swir(self, comments):
        metadata_ris_lis = {'operator': self.operator, 'location': self.location, 'size x': self.x, 'size y': self.y,
                            'Source1': '',
                            'Source2': '', 'Source3': '', 'Source4': '',
                            'resolution': self.pixel_size, 'acquisition time': self.acquisition_time,
                            'mapping duration': self.mapping_duration_str(),
                            'Source': '',
                            'Optical Spectrometer': {'device': 'Avantes', 'grating': '', 'slit': ''},
                            'comments': comments}
        # TODO implement spectro info as dict
        return metadata_ris_lis

    def save_as(self, hdf5=False, edf=False, raw=False):
        if hdf5:
            self.hdf5()
        if edf:
            self.edf()
        if raw:
            self.raw()

    def hdf5(self, data_xrf=None, data_ris_lis=None, data_swir=None, comments=''):
        f = h5.File(self.path, 'w')
        if data_xrf is not None:
            m_xrf = self.metadata_xrf(self.V, self.mA, comments)
            map_xrf = f.create_group('map xrf')
            for k in m_xrf.keys():
                map_xrf.attrs[k] = m_xrf[k]
            map_xrf.create_dataset('data xrf', shape=data_xrf.shape, data=data_xrf)
            map_xrf.create_dataset('calibration', data=self.calibration_xrf)

        if data_ris_lis is not None:
            m_ris_lis = self.metadata_ris_lis(comments)
            map_ris_lis = f.create_group('map ris lis')
            for k in m_ris_lis.keys():
                map_ris_lis.attrs[k] = m_ris_lis[k]
            map_ris_lis.create_dataset('data ris lis', shape=data_ris_lis.shape, data=data_ris_lis)
            map_ris_lis.create_dataset('calibration', data=self.calibration_ris_lis)

        if data_swir is not None:
            m_swir = self.metadata_swir(comments)
            map_swir = f.create_group('map swir')
            for k in m_swir.keys():
                map_swir.attrs[k] = m_swir[k]
            map_swir.create_dataset('data swir ')

    def edf(self):
        pass

    def raw(self):
        pass

    def save_cfg(self, cfg):
        full_path = self.path + self.filename
        with open(full_path, 'w') as f:
            f.write('{')
            for main_key, sub_key in cfg.items():
                f.write('"')
                f.write(str(main_key))
                f.write('": \n\n{\n')
                for key, value in sub_key.items():
                    f.write('"')
                    f.write(str(key) + ': ')
                    if type(value) is int:
                        f.write(str(value))
                    else:
                        f.write('"' + str(value) + '"')
                    f.write(',\n')
                f.write('},\n\n')
            f.write('}')


    def save_backup_line(self):
        pass

    def backup_directory_cleaner(self):
        pass

# test = {'project info': {'name': 'Test_1', 'operator': 'Raphael Moreau', 'Localisation': 'C2RMF'}, 'mapping parameters': {'x': 1, 'y': 1, 'pixel_size': 500, 'acquisition_time': 80}}
#
# DataSaving('G:\DATA\PyCharm Projects\MITHRA\core_app', '\\test.cfg', 1, 1, 500, 80).save_cfg(test)