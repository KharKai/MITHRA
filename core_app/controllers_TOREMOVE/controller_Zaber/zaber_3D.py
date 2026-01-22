import numpy as np
import serial

# from zaber_motion import Library, DeviceDbSourceType
from zaber_motion.exceptions.connection_failed_exception import ConnectionFailedException
from zaber_motion.exceptions.no_device_found_exception import NoDeviceFoundException
from zaber_motion.ascii import Connection
from zaber_motion import Units, Measurement

import copy
import open3d as o3d
from scipy.interpolate import griddata
import sys

# Library.enable_device_db_store()
# Library.set_device_db_source(DeviceDbSourceType.FILE, "C:\\Program Files (x86)\\Zaber Technologies\\Device Database\\"
#                                                       "devices-public.sqlite")


class MotorZaber:

    def __init__(self):
        self.portCOM = None
        self.connection = None
        self.device_list = None
        self.device_x = None
        self.device_y = None
        self.device_z = None
        self.axis_x = None
        self.axis_y = None
        self.axis_z = None

    def connect_motor(self, on_flight_correction):
        ports = serial.tools.list_ports.comports()
        for port, desc, hwid in sorted(ports):
            # print('zaber')
            # print("{}: {} [{}]".format(port, desc, hwid))
            if 'VID:PID=0XXX:0XXX' in hwid:
                self.portCOM = port
                self.connection = Connection.open_serial_port(self.portCOM)
                self.device_list = self.connection.detect_devices()
        if self.portCOM is None:
            return False
        # self.device_x = self.device_list[1]
        # self.axis_x = self.device_x.get_axis(1)

        self.device_x = self.device_list[1]
        self.device_y = self.device_list[2]

        self.axis_x = self.device_x.get_axis(1)
        self.axis_y = self.device_y.get_axis(1)

        self.axis_x.settings.set('maxspeed', 30, Units.VELOCITY_MILLIMETRES_PER_SECOND)
        self.axis_y.settings.set('maxspeed', 30, Units.VELOCITY_MILLIMETRES_PER_SECOND)

        if on_flight_correction is False:
            self.device_z = self.device_list[3]
            self.axis_z = self.device_z.get_axis(1)

            self.axis_z.settings.set('maxspeed', 30, Units.VELOCITY_MILLIMETRES_PER_SECOND)
        return True

    def park_axis(self, on_flight_correction):
        self.axis_x.park()
        self.axis_y.park()
        if on_flight_correction is False:
            self.axis_z.park()

    def unpark_axis(self, on_flight_correction):
        self.axis_x.unpark()
        self.axis_y.unpark()
        if on_flight_correction is False:
            self.axis_z.unpark()

    def move_X(self, x, speed, idle):
        self.axis_x.settings.set('maxspeed', speed, Units.VELOCITY_MILLIMETRES_PER_SECOND)
        self.axis_x.settings.set('accel', 50, Units.ACCELERATION_MILLIMETRES_PER_SECOND_SQUARED)
        self.axis_x.move_relative(x, Units.LENGTH_MICROMETRES, wait_until_idle=idle)

    def move_Y(self, y, speed, idle):
        self.axis_y.settings.set('maxspeed', speed, Units.VELOCITY_MILLIMETRES_PER_SECOND)
        self.axis_y.settings.set('accel', 50, Units.ACCELERATION_MILLIMETRES_PER_SECOND_SQUARED)
        self.axis_y.move_relative(y, Units.LENGTH_MICROMETRES, wait_until_idle=idle)

    def move_Z(self, z, speed, idle): #accel,
        self.axis_z.move_relative(position=z,
                                  unit=Units.LENGTH_MICROMETRES,
                                  velocity=speed,
                                  velocity_unit=Units.VELOCITY_MILLIMETRES_PER_SECOND,
                                  # acceleration=accel,
                                  # acceleration_unit=Units.ACCELERATION_MILLIMETRES_PER_SECOND_SQUARED,
                                  wait_until_idle=idle)

    def get_position(self):
        position_x = self.axis_x.get_position(unit=Units.LENGTH_CENTIMETRES)
        position_y = self.axis_y.get_position(unit=Units.LENGTH_CENTIMETRES)
        position_z = self.axis_z.get_position(unit=Units.LENGTH_CENTIMETRES)
        return [position_x, position_y, position_z]

    def stream(self, number_pixel, pos_line, speed_line, is_even=True):
        stream = self.device_z.get_stream(1)
        stream_buffer = self.device_z.get_stream_buffer(1)
        stream.disable()
        stream_buffer.erase()
        stream.setup_store(stream_buffer, 1)
        if is_even is True:
            for i in range(number_pixel - 1):
                stream.set_max_speed(speed_line[i], unit=Units.VELOCITY_MILLIMETRES_PER_SECOND)
                stream.line_absolute(Measurement(round(pos_line[i + 1], 4), Units.LENGTH_CENTIMETRES))
        else:
            for i in range(number_pixel - 1, 0, -1):
                stream.set_max_speed(speed_line[i-1], unit=Units.VELOCITY_MILLIMETRES_PER_SECOND)
                stream.line_absolute(Measurement(round(pos_line[i - 1], 4), Units.LENGTH_CENTIMETRES))
        stream.disable()
        stream.setup_live(1)
        stream.call(stream_buffer)


class Module_3D:

    def __init__(self):

        # Build stages virtual space, axis of basis (mesh frame), and target coordinates as pcd
        self.mesh_frame = o3d.geometry.TriangleMesh.create_coordinate_frame(size=1.0, origin=[0, 0, 0])
        self.virtual_space_points = [[0, 0, 0], [45, 0, 0], [0, 30, 0], [45, 30, 0],
                                     [0, 0, 15], [45, 0, 15], [0, 30, 15], [45, 30, 15]]
        self.virtual_space_lines = [[0, 1], [0, 2], [1, 3], [2, 3],
                                    [4, 5], [4, 6], [5, 7], [6, 7],
                                    [0, 4], [1, 5], [2, 6], [3, 7]]
        self.colors = [[1, 0, 0] for i in range(len(self.virtual_space_lines))]
        self.virtual_space = o3d.geometry.LineSet(points=o3d.utility.Vector3dVector(self.virtual_space_points),
                                                  lines=o3d.utility.Vector2iVector(self.virtual_space_lines), )
        self.virtual_space.colors = o3d.utility.Vector3dVector(self.colors)

    def visualization(self, object):
        o3d.visualization.draw_geometries(object)

    def interactive_visualization(self, object):
        vis_1 = o3d.visualization.VisualizerWithEditing()
        vis_1.create_window()
        vis_1.add_geometry(object)
        vis_1.run()
        vis_1.destroy_window()
        selected_point = vis_1.get_picked_points()[-1]
        return selected_point

    def rotation_to_view(self, list_pcd):
        rotated_pcds = []
        for pcd in list_pcd:
            pcd_view = copy.deepcopy(pcd)
            R = pcd_view.get_rotation_matrix_from_axis_angle([np.radians(180), 0, 0])
            pcd_view.rotate(R, center=(0, 0, 0))
            rotated_pcds.append(pcd_view)
        return rotated_pcds

    def pcd_transform(self, pcd_source, p1, p2, p3, p4, p5, list_origin, list_x_max, list_xy_max, list_y_max, list_middle):
        coord_target = [list_origin, list_x_max, list_xy_max, list_y_max, list_middle]
        # color_target = [[1.0, 0.0, 0.0],
        #                 [0.0, 1.0, 0.0],
        #                 [0.0, 0.0, 1.0]]
        np_coord_alignment = np.array(coord_target)
        # np_color_alignment = np.array(color_target)

        pcd_target = o3d.geometry.PointCloud()
        pcd_target.points = o3d.utility.Vector3dVector(np_coord_alignment)
        # pcd_target.colors = o3d.utility.Vector3dVector(np_color_alignment)

        picked_index_source = [p1, p2, p3, p4, p5]

        picked_index_target = [0, 1, 2, 3, 4]

        alignment_points_pair = np.zeros((5, 2))
        alignment_points_pair[:, 0] = picked_index_source
        alignment_points_pair[:, 1] = picked_index_target
        p2p = o3d.pipelines.registration.TransformationEstimationPointToPoint()
        trans_init = p2p.compute_transformation(pcd_source, pcd_target,
                                                o3d.utility.Vector2iVector(alignment_points_pair))
        pcd_source.transform(trans_init)
        return pcd_source

    def grid_builder(self, x, y, step_size_3d_x, step_size_3d_y, ref_point, pcd):
        """x, y in cm, step_size in µm"""

        point_number_x = int(x / (step_size_3d_x / 10000))
        point_number_y = int(y / (step_size_3d_y / 10000))
        print(point_number_x)
        print(point_number_y)

        np_pcd = np.asarray(pcd.points)

        x_grid_interp = np.linspace(ref_point[0], ref_point[0] + x, point_number_x)
        y_grid_interp = np.linspace(ref_point[1], ref_point[1] - y, point_number_y)

        X_interp, Y_interp = np.meshgrid(x_grid_interp, y_grid_interp)

        Z_interp = griddata((np_pcd[:, 0], np_pcd[:, 1]), np_pcd[:, 2], (X_interp, Y_interp), method='linear') # *10 in mm??

        point_grid_interp_x = X_interp.flatten()
        point_grid_interp_y = Y_interp.flatten()
        point_grid_interp_z = Z_interp.flatten()

        points_grid_interp = np.vstack((point_grid_interp_x, point_grid_interp_y, point_grid_interp_z)).transpose()

        grid_interp = o3d.geometry.PointCloud()
        grid_interp.points = o3d.utility.Vector3dVector(points_grid_interp)
        # grid_interp.translate((0.0, 0.0, -1))
        np_grid_interp = np.asarray(grid_interp.points)
        return grid_interp, Z_interp, np_grid_interp

    def z_speed_array(self, x, y, integration_time, step_size_3d_x, step_size_3d_y, z):
        point_number_x = int(x / (step_size_3d_x / 10000))
        point_number_y = int(y / (step_size_3d_y / 10000))
        z_interp = z * 10 # convert Z from cm to mm
        speed_array = np.zeros((point_number_y, point_number_x-1))

        for i in range(point_number_y):
            for j in range(point_number_x-1):
                d = abs(z_interp[i, j + 1] - z_interp[i, j])  # distance between each point in millimeters
                speed = round((d / (integration_time * 0.001)), 3)  # speed in millimeters per seconds
                # accel = round(float(d / ((integration_time / 2) ** 2)), 3)
                speed_array[i, j] = speed
        print('speed calculated')
        print(speed_array)
        return speed_array




