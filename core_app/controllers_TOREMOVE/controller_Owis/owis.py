import time
import os
import ctypes
from ctypes import cdll, c_double
import serial.tools.list_ports

class MotorOwis:

    def __init__(self):
        self.lib_ps35 = cdll.LoadLibrary('C:\\DATA\\AppMITHRA\\core_AppMITHRA\\controllers_TOREMOVE\\controller_Owis\\dll\\ps35.dll')
        # self.lib_ps35 = ctypes.CDLL('C:\\DATA\\AppMITHRA\\core_AppMITHRA\\controllers_TOREMOVE\\controller_Owis\\dll\\ps35.dll', winmode=0)
        self.connection = None
        self.ps35 = None
        self.portCOM = None

        self.status = []

        self.axis_X = None
        self.axis_Y = None
        self.axis_Z = None

    def get_motor_status(self):
        self.status = []
        for i in range(3):
            state = self.lib_ps35.PS35_GetMoveState(1, i + 1)
            self.status.append(state)

    def idle(self):
        self.get_motor_status()
        while 1 in self.status:
            self.get_motor_status()
            # time.sleep(0.001)

    def connect_motor(self):
        ports = serial.tools.list_ports.comports()
        for port, desc, hwid in sorted(ports):
            # print('owis')
            # print("{}: {} [{}]".format(port, desc, hwid))
            if 'VID:PID=0403:6001' in hwid:
                self.portCOM = int(port[-1])
                # print('connected')
                self.connection = self.lib_ps35.PS35_Connect(1, 0, self.portCOM, 9600, 0, 0, 8, 0)
        if self.portCOM is None:
            return False
        self.lib_ps35.PS35_SetStageAttributes(1, 1, c_double(1.0), 2, c_double(0.1))
        self.lib_ps35.PS35_SetStageAttributes(1, 2, c_double(1.0), 2, c_double(0.1))
        self.lib_ps35.PS35_SetStageAttributes(1, 3, c_double(1.0), 2, c_double(0.1))

        self.lib_ps35.PS35_MotorInit(1, 1)
        self.lib_ps35.PS35_MotorInit(1, 2)
        self.lib_ps35.PS35_MotorInit(1, 3)

        self.lib_ps35.PS35_SetTargetMode(1, 1, 0)
        self.lib_ps35.PS35_SetTargetMode(1, 2, 0)
        self.lib_ps35.PS35_SetTargetMode(1, 3, 0)

        self.lib_ps35.PS35_SetAccelEx(1, 1, c_double(100 * 1000))
        self.lib_ps35.PS35_SetAccelEx(1, 2, c_double(100 * 1000))
        self.lib_ps35.PS35_SetAccelEx(1, 3, c_double(100 * 1000))

        self.lib_ps35.PS35_SetDecelEx(1, 1, c_double(100 * 1000))
        self.lib_ps35.PS35_SetDecelEx(1, 2, c_double(100 * 1000))
        self.lib_ps35.PS35_SetDecelEx(1, 3, c_double(100 * 1000))
        return True

    def set_z_correction_param(self):
        self.lib_ps35.PS35_SetPosFEx(1, 3, c_double(30 * 1000))
        self.lib_ps35.PS35_SetAccelEx(1, 3, c_double(100 * 1000))
        self.lib_ps35.PS35_SetDecelEx(1, 3, c_double(50 * 1000))
        pass


    def move_X(self, x, speed, idle):
        self.lib_ps35.PS35_SetPosFEx(1, 1, c_double(speed * 1000))
        self.lib_ps35.PS35_MoveEx(1, 1, c_double(x *10), 0) #lenght in micrometer
        if idle is True:
            self.idle()

    def move_Y(self, y, speed, idle):
        self.lib_ps35.PS35_SetPosFEx(1, 2, c_double(speed * 1000))
        self.lib_ps35.PS35_MoveEx(1, 2, c_double(y * 10), 0)
        if idle is True:
            self.idle()

    def move_Z(self, z, speed, idle):
        self.lib_ps35.PS35_SetPosFEx(1, 3, c_double(speed * 1000))
        self.lib_ps35.PS35_MoveEx(1, 3, c_double(z * 10), 0)
        if idle is True:
            self.idle()

    def stop_motor(self, axis):
        self.lib_ps35.PS35_Stop(1, axis)

if __name__ == '__main__':
    motor = MotorOwis()
    motor.connect_motor()

    motor.move_X(2000, 10, True)
    # motor.move_X(2000, 10, True) # shitty owis behavior
    # motor.move_X(1000, 10, True)
    motor.move_X(-500, 10, True)
    # motor.move_X(500, 10, False)
    # motor.stop_motor(1)
    # motor.move_X(-1000, 10, True)
    print('end')

