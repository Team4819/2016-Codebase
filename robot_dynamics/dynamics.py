from int_dynamics import dynamics
import math


class MyRobotDynamics(dynamics.DynamicsEngine):

    DEBUG_VERBOSITY = 0

    def build_loads(self):
        # Init drivetrain components (the assembly does this for us)

        # Two CIM
        left_front_motor = dynamics.CIMMotor()
        right_front_motor = dynamics.CIMMotor()
        left_rear_motor = dynamics.CIMMotor()
        right_rear_motor = dynamics.CIMMotor()

        # Two 10:1 gearboxes
        left_gearbox = dynamics.GearBox([left_front_motor, left_rear_motor], 10, 1)
        right_gearbox = dynamics.GearBox([right_front_motor, right_rear_motor], 10, 1)

        left_wheels = dynamics.KOPWheels(left_gearbox, 3, 6, 60)
        right_wheels = dynamics.KOPWheels(right_gearbox, 3, 6, 60)
        #left_wheels = dynamics.SimpleWheels(left_gearbox, 6)
        #right_wheels = dynamics.SimpleWheels(right_gearbox, 6)

        self.loads["drivetrain"] = dynamics.TwoDimensionalLoad(120)
        self.loads["drivetrain"].add_wheel(left_wheels, x_origin=-.5)
        self.loads["drivetrain"].add_wheel(right_wheels, x_origin=.5, r_origin=math.pi)

        # Init drivetrain sensors
        self.sensors['navx'] = dynamics.NavX(self.loads['drivetrain'])
        self.sensors['left_encoder'] = dynamics.CANTalonEncoder(left_gearbox)
        self.sensors['right_encoder'] = dynamics.CANTalonEncoder(right_gearbox)

        # Set drivetrain controllers
        self.controllers['left_drive_0'] = dynamics.CANTalonSpeedController(left_front_motor, 1)
        self.controllers['left_drive_0'].add_encoder(self.sensors['left_encoder'])
        self.controllers['left_drive_1'] = dynamics.CANTalonSpeedController(left_rear_motor, 2)
        self.controllers['right_drive_0'] = dynamics.CANTalonSpeedController(right_front_motor, 3)
        self.controllers['right_drive_0'].add_encoder(self.sensors['right_encoder'])
        self.controllers['right_drive_1'] = dynamics.CANTalonSpeedController(right_front_motor, 4)
