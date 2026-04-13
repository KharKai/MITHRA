import numpy as np

from core_app.MITHRA_utils.data_acquisition import DataAcquisition


class DataHandling(DataAcquisition):
    def __init__(self, datacube, *args, **kwargs):
        super(DataHandling, self).__init__(*args, **kwargs)

        self.datacube = datacube

        self.datacube_xrf = None
        self.datacube_ris = None
        self.datacube_lis1 = None
        self.datacube_lis2 = None
        self.datacube_lis3 = None
        self.datacube_swir = None

    def data_classifier(self, white_ris_lis, dark_ris_lis, white_swir, dark_swir):
        if self.data_acquisition_xrf and self.data_acquisition_ris_lis and self.data_acquisition_swir:
            self.datacube_xrf = np.copy(self.datacube[:, :, :511])
            self.datacube_ris = (np.copy(self.datacube[:, :, 3643:4687]) - dark_ris_lis) / (white_ris_lis - dark_ris_lis)
            self.datacube_lis1 = np.copy(self.datacube[:, :, 1555:2599])
            self.datacube_lis2 = np.copy(self.datacube[:, :, 2599:3643])
            self.datacube_lis3 = np.copy(self.datacube[:, :, 511:1555])
            self.datacube_swir = (np.copy(self.datacube[:, :, 4687:]) - dark_swir) / (white_swir - dark_swir)

        elif self.data_acquisition_xrf and self.data_acquisition_ris_lis:
            self.datacube_xrf = np.copy(self.datacube[:, :, :511])
            self.datacube_ris = (np.copy(self.datacube[:, :, 3643:4687]) - dark_ris_lis) / (white_ris_lis - dark_ris_lis)
            self.datacube_lis1 = np.copy(self.datacube[:, :, 1555:2599])
            self.datacube_lis2 = np.copy(self.datacube[:, :, 2599:3643])
            self.datacube_lis3 = np.copy(self.datacube[:, :, 511:1555])

        elif self.data_acquisition_xrf and self.data_acquisition_swir:
            self.datacube_xrf = np.copy(self.datacube[:, :, :511])
            self.datacube_swir = (np.copy(self.datacube[:, :, 511:]) - dark_swir) / (white_swir - dark_swir)

        elif self.data_acquisition_ris_lis and self.data_acquisition_swir:
            self.datacube_ris = (np.copy(self.datacube[:, :, 3132:4176]) - dark_ris_lis) / (white_ris_lis - dark_ris_lis)
            self.datacube_lis1 = np.copy(self.datacube[:, :, 1044:2088])
            self.datacube_lis2 = np.copy(self.datacube[:, :, 2088:3132])
            self.datacube_lis3 = np.copy(self.datacube[:, :, :1044])
            self.datacube_swir = (np.copy(self.datacube[:, :, 4176:])- dark_swir) / (white_swir - dark_swir)

        elif self.data_acquisition_xrf:
            self.datacube_xrf = np.copy(self.datacube[:, :, :])

        elif self.data_acquisition_ris_lis:
            self.datacube_ris = (np.copy(self.datacube[:, :, 3132:]) - dark_ris_lis) / (white_ris_lis - dark_ris_lis)
            self.datacube_lis1 = np.copy(self.datacube[:, :, 1044:2088])
            self.datacube_lis2 = np.copy(self.datacube[:, :, 2088:3132])
            self.datacube_lis3 = np.copy(self.datacube[:, :, :1044])

        elif self.data_acquisition_swir:
            self.datacube_swir = (np.copy(self.datacube[:, :, :]) - dark_swir) / (white_swir - dark_swir)