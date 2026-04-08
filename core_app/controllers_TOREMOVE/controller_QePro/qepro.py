"""A USB interface to Ocean Insight's QE Pro Spectrometer"""

import usb.core
import usb.util
import hashlib

import matplotlib.pyplot as plt

def checksum(data):
    """Calculate MD5 hash to return as the checksum 16 bytes block"""
    checksum = bytearray(16)
    md5 = hashlib.md5()
    md5.update(data)
    hexstr = md5.hexdigest()
    for i in range(0, len(hexstr) - 1, 2):
        e = hexstr[i:i + 2]
        checksum[i // 2] = int(e, base=16)
    # print(checksum.hex())
    return checksum


# pack and unpack integer

def int2bytes_big(unsint, size):
    """convert integer to 'size' bytes (big endian)"""
    ba = bytearray(unsint.to_bytes(size, 'big'))
    return ba


def int2bytes_little(unsint, size):
    """convert integer to 'size' bytes (little endian)"""
    ba = bytearray(unsint.to_bytes(size, 'little'))
    return ba


def bytes2int_big(ba):
    """convert bytes array to integer (from big endian)"""
    num = int.from_bytes(ba, 'big')
    return num


def bytes2int_little(ba):
    """convert byte array to integer (from little endian)"""
    num = int.from_bytes(ba, 'little')
    return num


def bytes2float_little(ba):
    """convert byte array to float (from little endian)"""
    num = int.from_bytes(ba, 'little')
    return 1.0 * num


def packmsg(header, footer):
    """packmsg prepares a msg to send it to the device"""
    cs = checksum(header)
    ba = header + cs + footer
    return ba


class status():

    def __init__(self, raw):
        self.DEVICE_ID = '2457:4004'
        self.Firmware = raw[0]
        self.FPGA = raw[1]
        self.SerialNumber = raw[2]
        self.integration_time = raw[3]
        self.Trigger_mode = raw[4]
        self.MaxBufferSize = raw[5]
        self.BufferSize = raw[6]
        self.lamp_enable = raw[7]
        self.device_status = raw[8]


def printStatus(status):
        print('================= QEPro status ====================\n' +
              'Device ID        : ' + str(status.DEVICE_ID) + '\n' +
              'Firmware         : ' + str(status.Firmware) + '\n' +
              'FPGA             : ' + str(status.FPGA) + '\n' +
              'Serial Number    : ' + str(status.SerialNumber)+'\n' +
              'Integration time : ' + str(status.integration_time) + ' msec' + '\n' +
              'Trigger Mode     : ' + str(status.Trigger_mode) + '\n' +
              'Max Buffer size  : ' + str(status.MaxBufferSize) + '\n' +
              'Buffer size      : ' + str(status.BufferSize) + '\n' +
              'Lamp Enable      : ' + str(status.lamp_enable) + '\n' +
              'Device status    : ' + str(status.device_status) + '\n' +
              '===================================================')

def printplaintextStatus(status):
        strStatus = ('==== QEPro status ====\n' +
                     'Device ID        : ' + str(status.DEVICE_ID) + '\n' +
                     'Firmware         : ' + str(status.Firmware) + '\n' +
                     'FPGA             : ' + str(status.FPGA) + '\n' +
                     'Serial Number    : ' + str(status.SerialNumber)+'\n' +
                     'Integration time : ' + str(status.integration_time) + ' msec' + '\n' +
                     'Trigger Mode     : ' + str(status.Trigger_mode) + '\n' +
                     'Max Buffer size  : ' + str(status.MaxBufferSize) + '\n' +
                     'Buffer size      : ' + str(status.BufferSize) + '\n' +
                     'Lamp Enable      : ' + str(status.lamp_enable) + '\n' +
                     'Device status    : ' + str(status.device_status) + '\n' +
                     '=================')

        return strStatus


class Device:
    """device provides request commands and responses from QE Pro spectrometer"""

    def __init__(self):
        self.dev = None

        self.eout = 1       # 0x01
        self.ein = 129      # 0x81
        self.timeout = 2000

    # def __del__(self):
    #     if self.dev is None:
    #         raise ValueError('Device not found')
    #
    #     self.dev.reset()
    #     usb.util.dispose_resources(self.dev)

    def connect_optical_spectrometer(self):
        self.dev = usb.core.find(idVendor=0x2457, idProduct=0x4004)
        if self.dev is None:
            raise ValueError('Spectrometer not found')
        self.dev.set_configuration()

    def disconnect_optical_spectrometer(self):
        try:
            usb.util.dispose_resources(self.dev)
        except Exception as e:
            print(e)

    def sendCmd(self, message_opcode_1, message_opcode_2, message_opcode_3, message_opcode_4, data=None, data_length=None):
        """sends raw cmd over usb"""
        footer = bytearray(4)

        if data is None:
            data = 0
        if data_length is None:
            data_length = 0

        start = bytearray(2)
        protocol = bytearray(2)
        flags = bytearray(2)
        error_number = bytearray(2)
        message_opcode = bytearray(4)
        regarding = bytearray(4)
        reserved = bytearray(6)

        start[0] = 0xC1  # START
        start[1] = 0xC0  # START
        protocol[0] = 0x00  # Protocol version
        protocol[1] = 0x11  # Protocol version
        flags[0] = 0x00  # Flags
        flags[1] = 0x00  # Flags
        error_number[0] = 0x00  # Error number
        error_number[1] = 0x00  # Error number

        message_opcode[0] = message_opcode_1
        message_opcode[1] = message_opcode_2
        message_opcode[2] = message_opcode_3
        message_opcode[3] = message_opcode_4

        checksum_type = b'\x01'    # Checksum type : 0 = Disable, 1 = Enable

        ba = int2bytes_little(data, 16)

        ck = int2bytes_little(data_length, 1)

        immediate_data_length = ck  # Length of immediate data
        immediate_data = ba      # Immediate data

        bytes_remaining = int2bytes_little(20, 4)  # Bytes remaining -> rem = lenght_payload + lenght_checksum + lenght_footer

        header = start + protocol + flags + error_number + message_opcode + regarding + reserved + checksum_type + \
                 immediate_data_length + immediate_data + bytes_remaining  # + payload

        footer[0] = 0xC5
        footer[1] = 0xC4
        footer[2] = 0xC3
        footer[3] = 0xC2

        pout = packmsg(header, footer)  # POUT = final bytes array sent to device (header + payload + checksum + footer))
        res = self.dev.write(self.eout, pout, self.timeout)  # Two endpoints available, might be interesting to use

        return res

    def recvCmd(self):
        """receives raw cmd over usb"""
        #TEST
        # for i in range(1, 4500):
        #     print(i)
        #     try:
        #         devmsg = self.dev.read(self.ein, i, self.timeout)
        #         print('yay')
        #         chksm = (devmsg[-20:-4])
        #         cntrl = checksum(devmsg[:-20])
        #         assert chksm == cntrl
        #         return devmsg
        #     except:
        #         print('passed')

        devmsg = self.dev.read(self.ein, 4272, self.timeout) #4272

        chksm = (devmsg[-20:-4])
        cntrl = checksum(devmsg[:-20])
        assert chksm == cntrl
        return devmsg

# Request

    def start_acq(self):
        self.sendCmd(0x02, 0x09, 0x10, 0x00)

    def abort_acq(self):
        self.sendCmd(0x00, 0x00, 0x10, 0x00)

    def set_integration_time(self, integration_time):
        integration_time = integration_time * 1000  # conversion from milliseconds to microseconds
        if integration_time < 8000:
            print('Error : Minimum integration time is 8ms')
        else:
            self.sendCmd(0x10, 0x00, 0x11, 0x00, integration_time, data_length=4)  # microseconds

    def set_single_strobe(self, enable):
        self.sendCmd(0x12, 0x00, 0x30, 0x00, enable, data_length=1)            # 0: disable or 1: enable

    def set_single_strobe_width(self, width):
        self.sendCmd(0x11, 0x00, 0x30, 0x00, width, data_length=4)             # width in microseconds

    def set_single_strobe_delay(self, delay):
        self.sendCmd(0x10, 0x00, 0x30, 0x00, delay, data_length=4)             # delay in microseconds

    def set_lamp_enable(self, enable):
        self.sendCmd(0x10, 0x04, 0x11, 0x00, enable, data_length=1)            # 0: disable or 1: enable

    def clear_buffer(self):
        self.sendCmd(0x30, 0x08, 0x10, 0x00)

    def set_buffer_size(self, buffer_size):
        if buffer_size == 0:
            print('Error : Minimum buffer size is 1')
        else:
            self.sendCmd(0x32, 0x08, 0x10, 0x00, buffer_size, data_length=4)    # buffer_size : from 1 to

    def set_trigger_mode(self, mode):
        self.sendCmd(0x10, 0x01, 0x11, 0x00, mode, data_length=1)  # 0 = 'Normal', 1 = 'Level trigger', 2 = 'Synchronization', 3 = 'Edge trigger'

    def get_spectrum(self):
        """get spectrum and metadata associated"""
        self.sendCmd(0x28, 0x09, 0x10, 0x00)

        res = self.recvCmd()
        spectrum_count = bytes2int_little(res[44:48])
        tick_count = bytes2int_little(res[48:56])
        integration_time = bytes2int_little(res[56:60])
        trigger_mode = res[62]
        pixel_data = res[76:4252]
        spectrum = []

        for indx in range(0, 4176, 4):
            spc = bytearray(pixel_data)
            spectrum.append(bytes2int_little(spc[indx:(indx + 4)]))

        return spectrum, spectrum_count, tick_count, integration_time, trigger_mode

    def set_TEC_enable(self, enable):
        self.sendCmd(0x10, 0x00, 0x42, 0x00, enable, data_length=1)         # 0: disable or 1: enable

    def set_TEC_setpoint(self, setpoint):
        self.sendCmd(0x11, 0x00, 0x42, 0x00, setpoint)       # /!\ Set point in °C : negative values ?

# Response

    def get_firmware(self):
        self.sendCmd(0x90, 0x00, 0x00, 0x00)
        res = self.recvCmd()
        firmware = bytes2int_little(bytearray(res[24:26]))
        return firmware

    def get_FPGA(self):
        self.sendCmd(0x91, 0x00, 0x00, 0x00)
        res = self.recvCmd()
        print(res)
        FPGA = bytes2int_little(bytearray(res[24:26]))
        return FPGA

    def get_serial_number(self):
        self.sendCmd(0x00, 0x01, 0x00, 0x00)
        res = self.recvCmd()
        serial_number = str(res[24:32], 'utf-8')
        return serial_number

    def max_buffer_size(self):
        self.sendCmd(0x20, 0x08, 0x10, 0x00)
        res = self.recvCmd()
        max_buffer_size = bytes2int_little(bytearray(res[24:28]))
        return max_buffer_size

    def get_lamp_enable(self):
        self.sendCmd(0x00, 0x04, 0x11, 0x00)
        res = self.recvCmd()
        if res[24] == 1:
            state = 'enable'
        else:
            state = 'disable'
        return state

    def get_trigger_mode(self):
        self.sendCmd(0x00, 0x01, 0x11, 0x00)
        res = self.recvCmd()
        if res[24] == 0:
            trigger_mode = 'Normal'
        elif res[24] == 1:
            trigger_mode = 'Level trigger'
        elif res[24] == 2:
            trigger_mode = 'Synchronization'
        else:
            trigger_mode = 'Edge trigger'
        return trigger_mode

    def get_integration_time(self):
        self.sendCmd(0x00, 0x00, 0x11, 0x00)
        print('sent')
        res = self.recvCmd()
        print('res')
        print(res)
        integration_time = bytes2int_little(bytearray(res[24:28]))
        integration_time = integration_time // 1000
        return integration_time

    def get_buffer_size(self):
        self.sendCmd(0x22, 0x08, 0x10, 0x00)
        res = self.recvCmd()
        buffer_size = bytes2int_little(bytearray(res[24:28]))
        return buffer_size

    def get_nb_spectra_buffer(self):
        self.sendCmd(0x00, 0x09, 0x10, 0x00)
        res = self.recvCmd()
        nb_spectra_buffer = bytes2int_little(bytearray(res[24:28]))
        return nb_spectra_buffer

    def get_TEC_temperature(self):
        self.sendCmd(0x04, 0x00, 0x42, 0x00)
        res = self.recvCmd()
        TEC_temperature = bytes2int_little(bytearray(res[24:28]))  # /!\ Set point in °C : negative values --> single floating ?
        return TEC_temperature

    def get_acq(self):
        self.sendCmd(0x08, 0x09, 0x10, 0x00)
        res = self.recvCmd()
        if res[24] == 1:
            state = 'Idle state'
        else:
            state = 'Acquiring'
        return state

    def get_status_device(self):
        device_status = []
        device_status.append(self.get_firmware())
        device_status.append(self.get_FPGA())
        device_status.append(self.get_serial_number())
        device_status.append(self.get_integration_time())
        device_status.append(self.get_trigger_mode())


if __name__ == '__main__':
    dev = Device()
    dev.connect_optical_spectrometer()
    dev.abort_acq()
    dev.start_acq()

    s, n, tick, i, t  = dev.get_spectrum()# [0], dev.get_spectrum()[1]
    print(n)
    s, n, tick, i, t  = dev.get_spectrum()# [0], dev.get_spectrum()[1]
    print(n)
    s, n, tick, i, t  = dev.get_spectrum()# [0], dev.get_spectrum()[1]
    print(n)

    dev.abort_acq()

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(s)
    plt.show()


