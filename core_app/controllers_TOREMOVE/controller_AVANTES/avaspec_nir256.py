from ctypes import cdll, c_double


class Device:
    def __init__(self):
        self.lib_avaspec = cdll.LoadLibrary("G:\\DATA\\PyCharm Projects\\MITHRA\\core_app\\controllers_TOREMOVE\\controller_AVANTES\\dll\\avaspecx64.dll")
        self.lib_avaspec.AVS_Init(0)

    def connect_optical_spectrometer(self):
        nb_device = self.lib_avaspec.AVS_UpdateUSBDevices()

        return nb_device

    def get_spectrum(self):
        pass

    def set_integration_time(self):
        pass

if __name__ == '__main__':
    dev = Device()
    i = dev.connect_optical_spectrometer()
    print(i)