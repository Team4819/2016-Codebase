import wpilib
import yeti
import asyncio
from robotpy_ext.common_drivers import navx


class AdvancedDrive(yeti.Module):
    """
    A slightly more advanced drive module.
    """

    PID_DEFENCE_DRIVE = False
    GYRO_DEFENCE_DRIVE = True

    def module_init(self):
        # Setup a device references
        self.joystick = wpilib.Joystick(0)
        self.motors = {
            "left_drive_0": wpilib.CANTalon(1),
            "left_drive_1": wpilib.CANTalon(2),
            "right_drive_0": wpilib.CANTalon(3),
            "right_drive_1": wpilib.CANTalon(4)
        }
        self.motors["left_drive_0"].setFeedbackDevice(wpilib.CANTalon.FeedbackDevice.QuadEncoder)
        self.motors["right_drive_0"].setFeedbackDevice(wpilib.CANTalon.FeedbackDevice.QuadEncoder)
        self.navx = navx.AHRS.create_i2c()
        self.angle_setpoint = 0
        self.input_x = 0
        self.input_y = 0
        self.breach_mode = False
        self.speed_mode = False

    async def main_loop(self):
        while True:
            wpilib.SmartDashboard.putNumber("navx incline", self.get_incline())
            wpilib.SmartDashboard.putNumber("navx angle", self.navx.getAngle())
            wpilib.SmartDashboard.putNumber("navx setpoint", self.angle_setpoint)
            await asyncio.sleep(0.2)

    def autonomous_init(self):
        self.angle_setpoint = self.navx.getAngle()

    def enabled_init(self):
        for motor in self.motors:
            self.motors[motor].enableControl()

    def teleop_periodic(self):
        turn = self.joystick.getX()
        power = self.joystick.getY()
        if abs(power) > 0:
            power = power**2 * abs(power)/power
        if abs(turn) > 0:
            turn = turn**2 * abs(turn)/turn
        self.input_y = power
        self.input_x = turn
        self.breach_mode = self.joystick.getTrigger()
        if self.joystick.getRawButton(2):
            self.angle_setpoint = self.navx.getAngle()

    def set_drive(self, x=0, y=0, breach=False):
        self.input_x = x
        self.input_y = y
        self.breach_mode = breach

    def get_incline(self):
        return self.navx.getRoll()

    def zero_drive_enc(self):
        self.motors["left_drive_0"].setEncPosition(0)
        self.motors["right_drive_0"].setEncPosition(0)

    def get_drive_enc(self):
        return self.motors["right_drive_0"].get()

    def enabled_periodic(self):
        # Get the joystick values and drive the motors.
        if not self.breach_mode:
            if self.speed_mode:
                for motor in self.motors:
                    self.motors[motor].setControlMode(wpilib.CANTalon.ControlMode.PercentVbus)
                self.speed_mode = False
            turn = self.input_x
            power = self.input_y
            self.set_lr(power-turn, power+turn)
        else:
            if self.PID_DEFENCE_DRIVE:
                if not self.speed_mode:
                    for motor in self.motors:
                        self.motors[motor].setControlMode(wpilib.CANTalon.ControlMode.Speed)
                    self.speed_mode = True
            turn = self.input_x
            power = self.input_y
            if self.GYRO_DEFENCE_DRIVE:
                error = (self.navx.getAngle() - self.angle_setpoint)
                while error > 90:
                    error -= 180
                while error < -90:
                    error += 180
                turn = error*0.1
            if self.PID_DEFENCE_DRIVE:
                power *= 10
                turn *= 10
            self.set_lr(power+turn, power-turn)

    def disabled_init(self):
        self.input_y = 0
        self.input_x = 0
        for motor in self.motors:
            self.motors[motor].disableControl()

    def set_lr(self, left_value, right_value):
        self.motors["left_drive_0"].set(-left_value)
        self.motors["left_drive_1"].set(-left_value)
        self.motors["right_drive_0"].set(right_value)
        self.motors["right_drive_1"].set(right_value)

    def module_deinit(self):
        # Free the device references
        for motor in self.motors:
            self.motors[motor].free()
        self.navx.free()
