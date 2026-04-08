import time

import ctypes
import ctypes.wintypes
import struct
import core_app.controllers_TOREMOVE.controller_AVANTES.globals_avs as globals_avs
from PyQt5.QtCore import *

AVS_SERIAL_LEN = 10
VERSION_LEN = 16
USER_ID_LEN = 64
WM_MEAS_READY = 0x8001

# dll = 'G:\\DATA\\PyCharm Projects\\MITHRA\\core_app\\controllers_TOREMOVE\\controller_AVANTES\\dll\\avaspecx64.dll'
dll = 'C:\\DATA\\MITHRA\\core_app\\controllers_TOREMOVE\\controller_AVANTES\\dll\\avaspecx64.dll'


class Device:
    def connect_optical_spectrometer(self): #, inttime, avg, winid
        AVS_Init(0)
        AVS_GetNrOfDevices()
        req = 0
        mylist = AvsIdentityType * 1
        ret = AVS_GetList(75, req, mylist)

        serienummer = str(ret[1].SerialNumber.decode("utf-8"))
        print("Found Serialnumber: " + serienummer)

        globals_avs.dev_handle = AVS_Activate(ret[1])
        # devcon = DeviceConfigType
        # reqsize = 0
        # ret = AVS_GetParameter(globals_avs.dev_handle, 63484, reqsize, devcon)
        #
        # globals_avs.pixels = ret[1].m_Detector_m_NrPixels
        # print(ret[1])
        # print(globals_avs.pixels)
        # ret = AVS_GetLambda(globals_avs.dev_handle, globals_avs.wavelength)
        # print(ret)
        # x = 0
        # while x < globals_avs.pixels: # 0 through 2047
        #     globals_avs.wavelength[x] = ret[x]
        #     x += 1
        # print(globals_avs.wavelength)
        # ret = AVS_UseHighResAdc(globals_avs.dev_handle, True)
        # print(ret)
        # measconfig = MeasConfigType
        # measconfig.m_StartPixel = 0
        # measconfig.m_StopPixel = globals_avs.pixels - 1
        # measconfig.m_IntegrationTime = float(40) # in ms
        # measconfig.m_IntegrationDelay = 0
        # measconfig.m_NrAverages = int(2)
        # measconfig.m_CorDynDark_m_Enable = 0  # nesting of types does NOT work!!
        # measconfig.m_CorDynDark_m_ForgetPercentage = 0
        # measconfig.m_Smoothing_m_SmoothPix = 0
        # measconfig.m_Smoothing_m_SmoothModel = 0
        # measconfig.m_SaturationDetection = 0
        # measconfig.m_Trigger_m_Mode = 0
        # measconfig.m_Trigger_m_Source = 0
        # measconfig.m_Trigger_m_SourceType = 0
        # measconfig.m_Control_m_StrobeControl = 0
        # measconfig.m_Control_m_LaserDelay = 0
        # measconfig.m_Control_m_LaserWidth = 0
        # measconfig.m_Control_m_LaserWaveLength = 0.0
        # measconfig.m_Control_m_StoreToRam = 0
        # print(measconfig)
        # ret = AVS_PrepareMeasure(globals_avs.dev_handle, measconfig)
        # print(globals_avs.dev_handle)
        # print(ret)
        # """Test"""
        # # nummeas = int(1)
        # ret = AVS_Measure(globals_avs.dev_handle, int(0), 2)
        # # time.sleep(0.5)
        # print('measure:')
        # print(ret)
        # # print(int(winid))
        # timestamp = 0
        # print(globals_avs.dev_handle)
        # for i in range(2):
        #     time.sleep(0.1)
        #     ret = AVS_GetScopeData(globals_avs.dev_handle, timestamp, globals_avs.spectral_data)
        #     timestamp = ret[0]
        #     x = 0
        #     while x < globals_avs.pixels:  # 0 through 2047
        #         globals_avs.spectral_data[x] = ret[1][x]
        #         x += 1
        #     print(globals_avs.spectral_data)
        #
        # ret = AVS_StopMeasure(globals_avs.dev_handle)


    def set_configuration(self, integration_time, average): #, winid
        devcon = DeviceConfigType
        reqsize = 0
        ret = AVS_GetParameter(globals_avs.dev_handle, 63484, reqsize, devcon)

        globals_avs.pixels = ret[1].m_Detector_m_NrPixels
        # print(ret[1])
        # print(globals_avs.pixels)
        ret = AVS_GetLambda(globals_avs.dev_handle, globals_avs.wavelength)
        # print(ret)
        x = 0
        while x < globals_avs.pixels: # 0 through 2047
            globals_avs.wavelength[x] = ret[x]
            x += 1
        # print(globals_avs.wavelength)
        ret = AVS_UseHighResAdc(globals_avs.dev_handle, True)
        # print(ret)
        measconfig = MeasConfigType
        measconfig.m_StartPixel = 0
        measconfig.m_StopPixel = globals_avs.pixels - 1
        measconfig.m_IntegrationTime = float(integration_time) # in ms
        measconfig.m_IntegrationDelay = 0
        measconfig.m_NrAverages = int(average)
        measconfig.m_CorDynDark_m_Enable = 0  # nesting of types does NOT work!!
        measconfig.m_CorDynDark_m_ForgetPercentage = 0
        measconfig.m_Smoothing_m_SmoothPix = 0
        measconfig.m_Smoothing_m_SmoothModel = 0
        measconfig.m_SaturationDetection = 0
        measconfig.m_Trigger_m_Mode = 0
        measconfig.m_Trigger_m_Source = 0
        measconfig.m_Trigger_m_SourceType = 0
        measconfig.m_Control_m_StrobeControl = 0
        measconfig.m_Control_m_LaserDelay = 0
        measconfig.m_Control_m_LaserWidth = 0
        measconfig.m_Control_m_LaserWaveLength = 0.0
        measconfig.m_Control_m_StoreToRam = 0
        ret = AVS_PrepareMeasure(globals_avs.dev_handle, measconfig)
        # print(ret)
        # nummeas = int(1)
        # ret = AVS_Measure(globals_avs.dev_handle, int(winid), nummeas)
        # # print(ret)
        # timestamp = 0
        # # print(globals_avs.dev_handle)
        # ret = AVS_GetScopeData(globals_avs.dev_handle, timestamp, globals_avs.spectral_data)
        # timestamp = ret[0]
        # x = 0
        # while x < globals_avs.pixels:  # 0 through 2047
        #     globals_avs.spectral_data[x] = ret[1][x]
        #     x += 1
        # print(globals_avs.spectral_data)

    def start_acq(self, win_id, num_spectra):
        ret = AVS_Measure(globals_avs.dev_handle, int(win_id), num_spectra)

    def stop_acq(self):
        ret = AVS_StopMeasure(globals_avs.dev_handle)

    def get_spectrum(self):
        timestamp = 0
        # print(globals_avs.dev_handle)
        ret = AVS_GetScopeData(globals_avs.dev_handle, timestamp, globals_avs.spectral_data)
        timestamp = ret[0]
        x = 0
        while x < globals_avs.pixels:  # 0 through 2047
            globals_avs.spectral_data[x] = ret[1][x]
            x += 1
        # print(globals_avs.spectral_data)
        return globals_avs.spectral_data, timestamp

class AvsIdentityType(ctypes.Structure):
    _pack_ = 1
    _fields_ = [("SerialNumber", ctypes.c_char * AVS_SERIAL_LEN),
                ("UserFriendlyName", ctypes.c_char * USER_ID_LEN),
                ("Status", ctypes.c_char)]


class MeasConfigType(ctypes.Structure):
    _pack_ = 1
    # _fields_ = []
    _fields_ = [("m_StartPixel", ctypes.c_uint16),
                ("m_StopPixel", ctypes.c_uint16),
                ("m_IntegrationTime", ctypes.c_float),
                ("m_IntegrationDelay", ctypes.c_uint32),
                ("m_NrAverages", ctypes.c_uint32),
                ("m_CorDynDark_m_Enable", ctypes.c_uint8),  # nesting of types does NOT work!!
                ("m_CorDynDark_m_ForgetPercentage", ctypes.c_uint8),
                ("m_Smoothing_m_SmoothPix", ctypes.c_uint16),
                ("m_Smoothing_m_SmoothModel", ctypes.c_uint8),
                ("m_SaturationDetection", ctypes.c_uint8),
                ("m_Trigger_m_Mode", ctypes.c_uint8),
                ("m_Trigger_m_Source", ctypes.c_uint8),
                ("m_Trigger_m_SourceType", ctypes.c_uint8),
                ("m_Control_m_StrobeControl", ctypes.c_uint16),
                ("m_Control_m_LaserDelay", ctypes.c_uint32),
                ("m_Control_m_LaserWidth", ctypes.c_uint32),
                ("m_Control_m_LaserWaveLength", ctypes.c_float),
                ("m_Control_m_StoreToRam", ctypes.c_uint16)]


class DeviceConfigType(ctypes.Structure):
    _pack_ = 1
    _fields_ = [("m_Len", ctypes.c_uint16),
                ("m_ConfigVersion", ctypes.c_uint16),
                ("m_aUserFriendlyId", ctypes.c_char * USER_ID_LEN),
                ("m_Detector_m_SensorType", ctypes.c_uint8),
                ("m_Detector_m_NrPixels", ctypes.c_uint16),
                ("m_Detector_m_aFit", ctypes.c_float * 5),
                ("m_Detector_m_NLEnable", ctypes.c_bool),
                ("m_Detector_m_aNLCorrect", ctypes.c_double * 8),
                ("m_Detector_m_aLowNLCounts", ctypes.c_double),
                ("m_Detector_m_aHighNLCounts", ctypes.c_double),
                ("m_Detector_m_Gain", ctypes.c_float * 2),
                ("m_Detector_m_Reserved", ctypes.c_float),
                ("m_Detector_m_Offset", ctypes.c_float * 2),
                ("m_Detector_m_ExtOffset", ctypes.c_float),
                ("m_Detector_m_DefectivePixels", ctypes.c_uint16 * 30),
                ("m_Irradiance_m_IntensityCalib_m_Smoothing_m_SmoothPix", ctypes.c_uint16),
                ("m_Irradiance_m_IntensityCalib_m_Smoothing_m_SmoothModel", ctypes.c_uint8),
                ("m_Irradiance_m_IntensityCalib_m_CalInttime", ctypes.c_float),
                ("m_Irradiance_m_IntensityCalib_m_aCalibConvers", ctypes.c_float * 4096),
                ("m_Irradiance_m_CalibrationType", ctypes.c_uint8),
                ("m_Irradiance_m_FiberDiameter", ctypes.c_uint32),
                ("m_Reflectance_m_Smoothing_m_SmoothPix", ctypes.c_uint16),
                ("m_Reflectance_m_Smoothing_m_SmoothModel", ctypes.c_uint8),
                ("m_Reflectance_m_CalInttime", ctypes.c_float),
                ("m_Reflectance_m_aCalibConvers", ctypes.c_float * 4096),
                ("m_SpectrumCorrect", ctypes.c_float * 4096),
                ("m_StandAlone_m_Enable", ctypes.c_bool),
                ("m_StandAlone_m_Meas_m_StartPixel", ctypes.c_uint16),
                ("m_StandAlone_m_Meas_m_StopPixel", ctypes.c_uint16),
                ("m_StandAlone_m_Meas_m_IntegrationTime", ctypes.c_float),
                ("m_StandAlone_m_Meas_m_IntegrationDelay", ctypes.c_uint32),
                ("m_StandAlone_m_Meas_m_NrAverages", ctypes.c_uint32),
                ("m_StandAlone_m_Meas_m_CorDynDark_m_Enable", ctypes.c_uint8),
                ("m_StandAlone_m_Meas_m_CorDynDark_m_ForgetPercentage", ctypes.c_uint8),
                ("m_StandAlone_m_Meas_m_Smoothing_m_SmoothPix", ctypes.c_uint16),
                ("m_StandAlone_m_Meas_m_Smoothing_m_SmoothModel", ctypes.c_uint8),
                ("m_StandAlone_m_Meas_m_SaturationDetection", ctypes.c_uint8),
                ("m_StandAlone_m_Meas_m_Trigger_m_Mode", ctypes.c_uint8),
                ("m_StandAlone_m_Meas_m_Trigger_m_Source", ctypes.c_uint8),
                ("m_StandAlone_m_Meas_m_Trigger_m_SourceType", ctypes.c_uint8),
                ("m_StandAlone_m_Meas_m_Control_m_StrobeControl", ctypes.c_uint16),
                ("m_StandAlone_m_Meas_m_Control_m_LaserDelay", ctypes.c_uint32),
                ("m_StandAlone_m_Meas_m_Control_m_LaserWidth", ctypes.c_uint32),
                ("m_StandAlone_m_Meas_m_Control_m_LaserWaveLength", ctypes.c_float),
                ("m_StandAlone_m_Meas_m_Control_m_StoreToRam", ctypes.c_uint16),
                ("m_StandAlone_m_Nmsr", ctypes.c_int16),
                ("m_StandAlone_m_Reserved", ctypes.c_uint8 * 12),  # SD Card, do not use
                ("m_Temperature_1_m_aFit", ctypes.c_float * 5),
                ("m_Temperature_2_m_aFit", ctypes.c_float * 5),
                ("m_Temperature_3_m_aFit", ctypes.c_float * 5),
                ("m_TecControl_m_Enable", ctypes.c_bool),
                ("m_TecControl_m_Setpoint", ctypes.c_float),
                ("m_TecControl_m_aFit", ctypes.c_float * 2),
                ("m_ProcessControl_m_AnalogLow", ctypes.c_float * 2),
                ("m_ProcessControl_m_AnalogHigh", ctypes.c_float * 2),
                ("m_ProcessControl_m_DigitalLow", ctypes.c_float * 10),
                ("m_ProcessControl_m_DigitalHigh", ctypes.c_float * 10),
                ("m_EthernetSettings_m_IpAddr", ctypes.c_uint32),
                ("m_EthernetSettings_m_NetMask", ctypes.c_uint32),
                ("m_EthernetSettings_m_Gateway", ctypes.c_uint32),
                ("m_EthernetSettings_m_DhcpEnabled", ctypes.c_uint8),
                ("m_EthernetSettings_m_TcpPort", ctypes.c_uint16),
                ("m_EthernetSettings_m_LinkStatus", ctypes.c_uint8),
                ("m_Reserved", ctypes.c_uint8 * 9720),
                ("m_OemData", ctypes.c_uint8 * 4096)]


def AVS_Init(x):
    lib = ctypes.WinDLL(dll)
    prototype = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_int)
    paramflags = (1, "port",),
    AVS_Init = prototype(("AVS_Init", lib), paramflags)
    ret = AVS_Init(x)
    return ret


def AVS_GetNrOfDevices():
    lib = ctypes.WinDLL(dll)
    prototype = ctypes.WINFUNCTYPE(ctypes.c_int)
    AVS_GetNrOfDevices = prototype(("AVS_GetNrOfDevices", lib), )
    ret = AVS_GetNrOfDevices()
    return ret


def AVS_GetList(listsize, requiredsize, IDlist):
    lib = ctypes.WinDLL(dll)
    prototype = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_int),
                                   ctypes.POINTER(AvsIdentityType))
    paramflags = (1, "listsize",), (2, "requiredsize",), (2, "IDlist",),
    AVS_GetList = prototype(("AVS_GetList", lib), paramflags)
    ret = AVS_GetList(listsize)
    # looks like you only pass the '1' parameters here
    # the '2' parameters are returned in 'ret' !!!
    return ret


def AVS_Activate(deviceID):
    lib = ctypes.WinDLL(dll)
    prototype = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.POINTER(AvsIdentityType))
    paramflags = (1, "deviceId",),
    AVS_Activate = prototype(("AVS_Activate", lib), paramflags)
    ret = AVS_Activate(deviceID)
    return ret


def AVS_UseHighResAdc(handle, enable):
    lib = ctypes.WinDLL(dll)
    prototype = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_int, ctypes.c_bool)
    paramflags = (1, "handle",), (1, "enable",),
    AVS_UseHighResAdc = prototype(("AVS_UseHighResAdc", lib), paramflags)
    ret = AVS_UseHighResAdc(handle, enable)
    return ret


def AVS_GetVersionInfo(handle, FPGAversion, FWversion, DLLversion):
    lib = ctypes.WinDLL(dll)
    prototype = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_int, ctypes.c_char * VERSION_LEN, ctypes.c_char * VERSION_LEN,
                                   ctypes.c_char * VERSION_LEN)
    paramflags = (1, "handle",), (2, "FPGAversion",), (2, "FWversion",), (2, "DLLversion",),
    AVS_GetVersionInfo = prototype(("AVS_GetVersionInfo", lib), paramflags)
    ret = AVS_GetVersionInfo(handle)
    return ret


def AVS_PrepareMeasure(handle, measconf):
    lib = ctypes.WinDLL(dll)
    datatype = ctypes.c_byte * 41
    data = datatype()
    temp = datatype()
    temp = struct.pack("HHfIIBBHBBBBBHIIfH", measconf.m_StartPixel,
                       measconf.m_StopPixel,
                       measconf.m_IntegrationTime,
                       measconf.m_IntegrationDelay,
                       measconf.m_NrAverages,
                       measconf.m_CorDynDark_m_Enable,
                       measconf.m_CorDynDark_m_ForgetPercentage,
                       measconf.m_Smoothing_m_SmoothPix,
                       measconf.m_Smoothing_m_SmoothModel,
                       measconf.m_SaturationDetection,
                       measconf.m_Trigger_m_Mode,
                       measconf.m_Trigger_m_Source,
                       measconf.m_Trigger_m_SourceType,
                       measconf.m_Control_m_StrobeControl,
                       measconf.m_Control_m_LaserDelay,
                       measconf.m_Control_m_LaserWidth,
                       measconf.m_Control_m_LaserWaveLength,
                       measconf.m_Control_m_StoreToRam)

    # copy bytes from temp to data, otherwise you will get a typing error below
    # why is this necessary?? they have the same type to start with ??
    x = 0
    while (x < 41):  # 0 through 40
        data[x] = temp[x]
        x += 1
    prototype = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_int, ctypes.c_byte * 41)
    paramflags = (1, "handle",), (1, "measconf",),
    AVS_PrepareMeasure = prototype(("AVS_PrepareMeasure", lib), paramflags)
    ret = AVS_PrepareMeasure(handle, data)
    return ret


def AVS_Measure(handle, windowhandle, nummeas):
    lib = ctypes.WinDLL(dll)
    prototype = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_int, ctypes.wintypes.HWND, ctypes.c_uint16)
    paramflags = (1, "handle",), (1, "windowhandle",), (1, "nummeas"),
    AVS_Measure = prototype(("AVS_Measure", lib), paramflags)
    ret = AVS_Measure(handle, windowhandle, nummeas)
    return ret


def AVS_StopMeasure(handle):
    lib = ctypes.WinDLL(dll)
    prototype = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_int)
    paramflags = (1, "handle",),
    AVS_StopMeasure = prototype(("AVS_StopMeasure", lib), paramflags)
    ret = AVS_StopMeasure(handle)
    return ret


def AVS_PollScan(handle):
    lib = ctypes.WinDLL(dll)
    prototype = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int)
    paramflags = (1, "handle",),
    AVS_PollScan = prototype(("AVS_PollScan", lib), paramflags)
    ret = AVS_PollScan(handle)
    return ret


def AVS_GetScopeData(handle, timelabel, spectrum):
    lib = ctypes.WinDLL(dll)
    prototype = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_uint32),
                                   ctypes.POINTER(ctypes.c_double * 4096))
    paramflags = (1, "handle",), (2, "timelabel",), (2, "spectrum",),
    AVS_GetScopeData = prototype(("AVS_GetScopeData", lib), paramflags)
    ret = AVS_GetScopeData(handle)
    return ret


def AVS_GetLambda(handle, wavelength):
    lib = ctypes.WinDLL(dll)
    prototype = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_double * 4096))
    paramflags = (1, "handle",), (2, "wavelength",),
    AVS_GetLambda = prototype(("AVS_GetLambda", lib), paramflags)
    ret = AVS_GetLambda(handle)
    return ret


def AVS_GetParameter(handle, size, reqsize, deviceconfig):
    lib = ctypes.WinDLL(dll)
    prototype = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_int, ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint32),
                                   ctypes.POINTER(DeviceConfigType))
    paramflags = (1, "handle",), (1, "size",), (2, "reqsize",), (2, "deviceconfig",),
    AVS_GetParameter = prototype(("AVS_GetParameter", lib), paramflags)
    ret = AVS_GetParameter(handle, size)
    return ret


def AVS_SetParameter(handle, deviceconfig):
    lib = ctypes.WinDLL(dll)
    datatype = ctypes.c_byte * 63484
    data = datatype()
    temp = datatype()
    temp = struct.pack("HH64B" +
                       "BH5f?8ddd2ff2ff30H" +  # Detector
                       "HBf4096fBI" +  # Irradiance
                       "HBf4096f" +  # Reflectance
                       "4096f" +  # SpectrumCorrect
                       "?HHfIIBBHBBBBBHIIfHH12B" +  # StandAlone
                       "5f5f5f" +  # Temperature
                       "?f2f" +  # TecControl
                       "2f2f10f10f " +  # ProcessControl
                       "IIIBHB" +  # EthernetSettings
                       "9720B" +  # Reserved
                       "4096B",  # OemData
                       deviceconfig.mLen,
                       deviceconfig.m_ConfigVersion,
                       deviceconfig.m_aUserFriendlyId,
                       deviceconfig.m_Detector_m_SensorType,
                       deviceconfig.m_Detector_m_NrPixels,
                       deviceconfig.m_Detector_m_aFit,
                       deviceconfig.m_Detector_m_NLEnable,
                       deviceconfig.m_Detector_m_aNLCorrect,
                       deviceconfig.m_Detector_m_aLowNLCounts,
                       deviceconfig.m_Detector_m_aHighNLCounts,
                       deviceconfig.m_Detector_m_Gain,
                       deviceconfig.m_Detector_m_Reserved,
                       deviceconfig.m_Detector_m_Offset,
                       deviceconfig.m_Detector_m_ExtOffset,
                       deviceconfig.m_Detector_m_DefectivePixels,
                       deviceconfig.m_Irradiance_m_IntensityCalib_m_Smoothing_m_SmoothPix,
                       deviceconfig.m_Irradiance_m_IntensityCalib_m_Smoothing_m_SmoothModel,
                       deviceconfig.m_Irradiance_m_IntensityCalib_m_CalInttime,
                       deviceconfig.m_Irradiance_m_IntensityCalib_m_aCalibConvers,
                       deviceconfig.m_Irradiance_m_CalibrationType,
                       deviceconfig.m_Irradiance_m_FiberDiameter,
                       deviceconfig.m_Reflectance_m_Smoothing_m_SmoothPix,
                       deviceconfig.m_Reflectance_m_Smoothing_m_SmoothModel,
                       deviceconfig.m_Reflectance_m_CalInttime,
                       deviceconfig.m_Reflectance_m_aCalibConvers,
                       deviceconfig.m_SpectrumCorrect,
                       deviceconfig.m_StandAlone_m_Enable,
                       deviceconfig.m_StandAlone_m_Meas_m_StartPixel,
                       deviceconfig.m_StandAlone_m_Meas_m_StopPixel,
                       deviceconfig.m_StandAlone_m_Meas_m_IntegrationTime,
                       deviceconfig.m_StandAlone_m_Meas_m_IntegrationDelay,
                       deviceconfig.m_StandAlone_m_Meas_m_NrAverages,
                       deviceconfig.m_StandAlone_m_Meas_m_CorDynDark_m_Enable,
                       deviceconfig.m_StandAlone_m_Meas_m_CorDynDark_m_ForgetPercentage,
                       deviceconfig.m_StandAlone_m_Meas_m_Smoothing_m_SmoothPix,
                       deviceconfig.m_StandAlone_m_Meas_m_Smoothing_m_SmoothModel,
                       deviceconfig.m_StandAlone_m_Meas_m_SaturationDetection,
                       deviceconfig.m_StandAlone_m_Meas_m_Trigger_m_Mode,
                       deviceconfig.m_StandAlone_m_Meas_m_Trigger_m_Source,
                       deviceconfig.m_StandAlone_m_Meas_m_Trigger_m_SourceType,
                       deviceconfig.m_StandAlone_m_Meas_m_Control_m_StrobeControl,
                       deviceconfig.m_StandAlone_m_Meas_m_Control_m_LaserDelay,
                       deviceconfig.m_StandAlone_m_Meas_m_Control_m_LaserWidth,
                       deviceconfig.m_StandAlone_m_Meas_m_Control_m_LaserWaveLength,
                       deviceconfig.m_StandAlone_m_Meas_m_Control_m_StoreToRam,
                       deviceconfig.m_StandAlone_m_Nmsr,
                       deviceconfig.m_StandAlone_m_Reserved,
                       deviceconfig.m_Temperature_1_m_aFit,
                       deviceconfig.m_Temperature_2_m_aFit,
                       deviceconfig.m_Temperature_3_m_aFit,
                       deviceconfig.m_TecControl_m_Enable,
                       deviceconfig.m_TecControl_m_Setpoint,
                       deviceconfig.m_TecControl_m_aFit,
                       deviceconfig.m_ProcessControl_m_AnalogLow,
                       deviceconfig.m_ProcessControl_m_AnalogHigh,
                       deviceconfig.m_ProcessControl_m_DigitalLow,
                       deviceconfig.m_ProcessControl_m_DigitalHigh,
                       deviceconfig.m_EthernetSettings_m_IpAddr,
                       deviceconfig.m_EthernetSettings_m_NetMask,
                       deviceconfig.m_EthernetSettings_m_Gateway,
                       deviceconfig.m_EthernetSettings_m_DhcpEnabled,
                       deviceconfig.m_EthernetSettings_m_TcpPort,
                       deviceconfig.m_EthernetSettings_m_LinkStatus,
                       deviceconfig.m_Reserved,
                       deviceconfig.m_OemData)
    x = 0
    while (x < 63484):  # 0 through 63483
        data[x] = temp[x]
        x += 1
    prototype = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_int, ctypes.c_byte * 63484)
    paramflags = (1, "handle",), (1, "deviceconfig",),
    AVS_SetParameter = prototype(("AVS_SetParameter", lib), paramflags)
    ret = AVS_SetParameter(handle, data)
    return ret