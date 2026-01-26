import numpy as np
import cv2
import math
import time

from multiprocessing.shared_memory import SharedMemory

class WebcamProcess:
    def __init__(self, source_video):
        self.source_video = source_video
        try:
            # create shared memory if available
            self.sh_mem = SharedMemory(create=True, size=921600, name='shared_memory_webcam')
        except FileExistsError:
            # if shared memory already exists, connect to it, destroy it and recreate
            self.sh_mem = SharedMemory(name='shared_memory_webcam')

            # self.sh_mem.close()
            # self.sh_mem.unlink()
            #
            # self.sh_mem = SharedMemory(create=True, size=921600, name='shared_memory_webcam')

    def get_frame(self):
        cap = cv2.VideoCapture(self.source_video)
        success, frame = cap.read()
        framebuffer = np.ndarray(frame.shape, dtype=np.uint8, buffer=self.sh_mem.buf)
        framebuffer[:] = frame
        try:
            while True:
                cap.read(framebuffer)
        except KeyboardInterrupt:
            pass
        finally:
            self.sh_mem.close()
            self.sh_mem.unlink()


class TelemetricLaserProcess:
    def __init__(self):
        self.corr_angle = math.sin(45 * (math.pi / 180))

    def get_distance(self, telemetric_laser, q_laser, q_z_lock_status, motor):
        try:
            while True:
                # print('getting distance...')
                time.sleep(0.1)
                # val = telemetric_laser.read_distance()
                val = np.random.randint(0, 10, 1, dtype=np.uint16)
                q_laser.put(val)
                z_lock_status = q_z_lock_status.get()
                print(z_lock_status)
                if z_lock_status[0]:
                    pass
                    # print('correcting')
                    # self.correct_distance(val, z_lock_status[1], motor)
        except KeyboardInterrupt:
            pass

    def correct_distance(self, val, z_lock_distance, motor):
        if val < 130:
                if z_lock_distance + 0.5 < val:
                    motor.move_Z(z=(z_lock_distance - val) * 100 * self.corr_angle, speed=30, idle=False)
                elif val < z_lock_distance - 0.50:
                    motor.move_Z(z=(z_lock_distance - val) * 100 * self.corr_angle, speed=30, idle=False)
