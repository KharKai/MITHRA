class AcquisitionParameters:
    def __init__(self, x, y, pixel_size, acquisition_time, path, filename, operator, localisation):
        self.path: str = path
        self.filename: str = filename

        self.operator: str = operator
        self.localisation: str = localisation


        self.x = x # in cm
        self.y = y # in cm

        self.pixel_size = pixel_size # in µm
        self.acquisition_time = acquisition_time # in ms

        self.V = 50 # in kV
        self.mA = 600 # in µA

        self.calibration_xrf = [0.03957, 0.05987, 0]
        self.calibration_ris_lis = [205.80195, 0.76349, 0]
        self.calibration_swir = [0, 1, 0]

    def motor_speed(self):
        pixel_size = float(self.pixel_size) * 0.001  # conversion from µm to mm
        acquisition_time = float(self.acquisition_time) * 0.001  # conversion from ms to s
        motor_speed = pixel_size / acquisition_time
        return motor_speed  # in mm/s

    def mapping_duration(self):
        x = self.x * 10  # conversion from cm to mm
        y = self.y * 10  # conversion from cm to mm

        motor_speed = self.motor_speed()  # in mm/s
        pixel_size = self.pixel_size * 0.001 # in mm
        line_number = self.line_number()
        transition_time = pixel_size/motor_speed

        mapping_duration = (((x / motor_speed) * (y / (float(pixel_size))))  # map size duration
                            + (transition_time * line_number)) # line transition

        h = mapping_duration / 3600
        min = (h - int(h)) * 60
        sec = (min - int(min)) * 60
        return mapping_duration, h, min, sec

    def mapping_duration_str(self):
        total, h, min, sec = self.mapping_duration()
        return '{:}h {:}min {:}s'.format(int(h), int(min), int(sec))

    def pixel_number(self):
        x = self.x * 10000  # conversion from cm to µm
        pixel_number = x / self.pixel_size
        return int(pixel_number)

    def line_number(self):
        y = self.y * 10000 # conversion from cm to µm
        line_number = y / self.pixel_size
        return int(line_number)

# d = MappingParameters(10, 10, 500, 80)
# print(d.mapping_duration_str())