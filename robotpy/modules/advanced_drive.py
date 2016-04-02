import wpilib
import yeti
import asyncio
import math
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
            "right_drive_0": wpilib.CANTalon(4),
            "right_drive_1": wpilib.CANTalon(3)
        }
        self.motors["left_drive_0"].setFeedbackDevice(wpilib.CANTalon.FeedbackDevice.QuadEncoder)
        #self.motors["left_drive_0"].configEncoderCodesPerRev(1440)
        self.motors["right_drive_0"].setFeedbackDevice(wpilib.CANTalon.FeedbackDevice.QuadEncoder)
        #self.motors["right_drive_0"].configEncoderCodesPerRev(1440)
        for motor in self.motors:
            self.motors[motor].enableBrakeMode(True)
        self.navx = navx.AHRS.create_spi()
        self.angle_setpoint = 0
        self.input_x = 0
        self.input_y = 0
        self.breach_mode = False
        self.speed_mode = False

    async def main_loop(self):
        while True:
            left_enc, right_enc = self.get_enc_pos()
            wpilib.SmartDashboard.putNumber("left_encoder", left_enc)
            wpilib.SmartDashboard.putNumber("right_encoder", right_enc)
            wpilib.SmartDashboard.putBoolean("navx connected", self.navx.isConnected())
            wpilib.SmartDashboard.putBoolean("navx calibrating", self.navx.isCalibrating())
            wpilib.SmartDashboard.putNumber("navx incline", self.get_incline())
            wpilib.SmartDashboard.putNumber("navx angle", self.navx.getAngle())
            wpilib.SmartDashboard.putNumber("navx setpoint", self.angle_setpoint)
            await asyncio.sleep(0.2)

    def get_enc_pos(self):
        return self.motors["left_drive_0"].getEncPosition()/(700*0.5*math.pi), -self.motors["right_drive_0"].getEncPosition()/(700*0.5*math.pi)

    def reset_encoders(self):
        self.motors["left_drive_0"].setEncPosition(0)
        self.motors["right_drive_0"].setEncPosition(0)

    def zero_gyro(self):
        self.navx.zeroYaw()

    async def drive_straight_to(self, distance, power, timeout=5):
        init_distance = self.get_enc_pos()[0]
        error = distance - init_distance
        direction = abs(error)/error
        self.breach_mode = True
        self.input_y = power
        counter = 0
        while self.gameclock.is_autonomous() and direction*(distance - self.get_enc_pos()[0]) > 0 and counter <= timeout:
            wpilib.SmartDashboard.putNumber("value", direction*(distance - self.get_enc_pos()[0]))
            await asyncio.sleep(0.05)
            counter += 0.05
        self.breach_mode = False
        self.input_y = 0
        if counter > timeout:
            self.logger.warn("Timeout reached before distance was reached! Distance is {}, while encoder pos is {}!".format(distance, self.get_enc_pos()[0]))
            return False
        else:
            return True

    async def turn_to(self, setpoint, range=3, timeout=5):
        self.input_y = 0
        self.angle_setpoint = setpoint
        self.breach_mode = True
        counter = 0
        while self.gameclock.is_autonomous() and counter <= timeout:
            error = (self.navx.getAngle() - self.angle_setpoint)
            while error > 90:
                error -= 180
            while error < -90:
                error += 180
            if error < range:
                break
            await asyncio.sleep(0.05)
            counter += 0.05
        self.breach_mode = False
        if counter > timeout:
            self.logger.warn(
                "Timeout reached before angle was reached! Setpoint is {}, while angle is {}!".format(self.angle_setpoint, self.navx.getAngle())
            )
            return False
        else:
            return True

    def autonomous_init(self):
        self.zero_gyro()

    def enabled_init(self):
        self.angle_setpoint = 0
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
            self.zero_gyro()

    def set_drive(self, x=0, y=0, breach=False):
        self.input_x = x
        self.input_y = y
        self.breach_mode = breach

    def get_incline(self):
        return self.navx.getPitch()

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
                turn = max(-0.5, min(error*0.025 + self.navx.getRate() * 0.1, 0.5))
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
