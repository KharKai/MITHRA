from ctypes import cdll, c_double


class Device:
    def __init__(self):
        self.lib_avaspec = cdll.LoadLibrary("G:\\DATA\\PyCharm Projects\\MITHRA\\core_app\\controllers_TOREMOVE\\controller_AVANTES\\dll\\avaspecx64.dll")


if __name__ == '__main__':
    dev = Device()