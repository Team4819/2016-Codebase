from int_dynamics import dynamics
import math
import numpy as np
import os


class MyRobotDynamics:

    def __init__(self):
        self.drivetrain = dynamics.KOPAssembly(125)#, imu_class=dynamics.sensors.NavX, build_ekf=True)
        self.get_state()
        self.get_sensors()
        self.get_controls()

    def get_sensors(self, hal_data=None, add_noise=False):
        self.sensors = {
            "gyro": self.drivetrain.imu.angle.get_value(),
            #"accel": np.array([self.drivetrain.imu.accel_x.get_value(),
            #                   self.drivetrain.imu.accel_y.get_value()]),
            "left_encoder": self.drivetrain.left_gearbox.position.get_value(),
            "right_encoder": self.drivetrain.right_gearbox.position.get_value()
        }
        if add_noise:
            self.sensors["gyro"] += np.random.normal(0, .05)
        if hal_data is not None:
            hal_data['robot']['navxmxp_i2c_1_angle'] = math.degrees(self.sensors["gyro"])
            hal_data['robot']['navxmxp_spi_4_angle'] = math.degrees(self.sensors["gyro"])
            hal_data['encoder'][0]['count'] = math.degrees(self.sensors["left_encoder"])
            hal_data['encoder'][1]['count'] = math.degrees(self.sensors["right_encoder"])
        return self.sensors

    def update_sensors(self):
        self.drivetrain.imu.angle.set_value(self.sensors["gyro"])
        #self.drivetrain.imu.accel_x.set_value(self.sensors["accel"][0])
        #self.drivetrain.imu.accel_y.set_value(self.sensors["accel"][1])
        self.drivetrain.left_encoder.position.set_value(self.sensors["left_encoder"])
        self.drivetrain.right_encoder.position.set_value(self.sensors["right_encoder"])

    def get_controls(self):
        self.controls = {
            "left_drive_cim": self.drivetrain.left_speed_controller.percent_vbus.get_value(),
            "right_drive_cim": self.drivetrain.right_speed_controller.percent_vbus.get_value(),
        }
        return self.controls

    def update_controls(self, hal_data=None, add_noise=False):
        if hal_data is not None:
            self.controls = {
                "left_drive_cim": hal_data['pwm'][0]['value'],
                "right_drive_cim": hal_data['pwm'][1]['value'],
            }
        if add_noise:
            self.controls["left_drive_cim"] += np.random.normal(0, .1)
            self.controls["right_drive_cim"] += np.random.normal(0, .1)
        self.drivetrain.set_values(self.controls["left_drive_cim"],
                                   self.controls["right_drive_cim"])

    def update_physics(self, dt, do_ekf=False):
        self.drivetrain.update_physics(dt, do_ekf)

    def get_state(self):
        self.state = {
            "drivetrain": self.drivetrain.get_state(),
        }
        return self.state

    def set_vector_controls(self, u):
        self.drivetrain.set_values(u[0], u[1])

    def get_vector_data(self):
        state_derivatives = self.drivetrain.get_state_derivatives()
        states = self.drivetrain.get_state()
        control_derivatives = self.drivetrain.drivetrain_integrator.control_derivative.get_value()
        return states, state_derivatives, control_derivatives


def get_dynamics():
    return dynamics.utilities.cache_object(MyRobotDynamics, file_path=os.path.abspath(__file__))

