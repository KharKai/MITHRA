import time

import serial
import serial.tools.list_ports


class Device:
    def __init__(self):
        self.dev = None

        self.portCOM = None

        self.offset_mm = 0.0
        self.laser_range_mm = 70
        self.out_of_range_flag = True

        self.measured_distance_mm = None

    def connect(self):
        ports = serial.tools.list_ports.comports()
        for port, desc, hwid in sorted(ports):
            # print("{}: {} [{}]".format(port, desc, hwid))
            if 'VID:PID=2341:0043' in hwid:
                self.portCOM = port
                self.dev = serial.Serial(self.portCOM,9600, timeout=1)

    def read_distance(self, sampling_rate_secs=0.01): # 0.05
        # Flush buffer
        self.dev.read_all()
        self.dev.readline()
        time.sleep(sampling_rate_secs)

        # Read single line from buffer
        str_val = str(self.dev.readline()[:-2])
        if not str_val == "b''":
            str_val = str_val.lstrip("b").strip("'")
            raw_measure_mm = int(str_val) * 0.0684931 + 65
            self.measured_distance_mm = self.offset_mm + raw_measure_mm
        return self.measured_distance_mm


# if __name__ == '__main__':
#     laser = Device()
#     laser.connect()
#     for i in range(3):
#         d = laser.read_distance()
#         print(d)
