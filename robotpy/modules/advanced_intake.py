import wpilib
import asyncio
import yeti


class AdvancedIntake(yeti.Module):

    DOUBLE_SOLENOID = True
    USE_CAN = False

    MIDPOINT = 0.770
    RANGE = 0.4

    def module_init(self):
        self.intake_solenoid_1 = wpilib.DoubleSolenoid(0, 1)
        if self.DOUBLE_SOLENOID:
            self.intake_solenoid_2 = wpilib.DoubleSolenoid(2, 3)
        if self.USE_CAN:
            self.intake_motor = wpilib.CANTalon(6)
            self.intake_motor.enableControl()
        else:
            self.intake_motor = wpilib.Talon(9)
        self.auto_override = False
        self.intake_potentiometer = wpilib.AnalogPotentiometer(0)
        self.setpoint = 0
        self.auto_intake_out = 0
        self.joystick = wpilib.Joystick(1)

    def set_override(self, value):
        self.auto_override = value

    async def main_loop(self):
        while True:
            wpilib.SmartDashboard.putNumber("intake input", self.get_input())
            await asyncio.sleep(0.1)

    def autonomous_init(self):
        self.set_setpoint(0)

    def teleop_periodic(self):
        if not self.auto_override:
            self.setpoint = self.joystick.getY()

    def get_input(self):
        sensor_read = self.intake_potentiometer.get()
        wpilib.SmartDashboard.putNumber("intake pot", sensor_read)
        return (self.MIDPOINT - sensor_read) / self.RANGE

    @yeti.singleton
    async def enabled_init(self):
        await asyncio.sleep(0.25)
        last_input = 0
        last_value = 0
        while self.gameclock.is_enabled():
            if self.gameclock.is_teleop():
                if self.joystick.getRawButton(3):
                    self.intake_motor.set(1)
                elif self.joystick.getRawButton(2):
                    self.intake_motor.set(-1)
                else:
                    self.intake_motor.set(0)
            else:
                self.intake_motor.set(self.auto_intake_out)

            input = self.get_input()
            analog_pos = self.intake_potentiometer.get()

            error = input - self.setpoint
            velocity = (input - last_input)/0.05
            if abs(last_value) < 1:
                velocity = 0
            value_out = error*8 + velocity*1.75

            if value_out*error < 0:
                value_out = 0

            val_1 = value_out
            if self.DOUBLE_SOLENOID:
                val_2 = val_1
                if analog_pos < 0.51:
                    val_1 = 0
                    if analog_pos < 0.47:
                        val_1 = -val_2
                elif analog_pos > 0.80:
                    val_2 = 0
                    if analog_pos > 00.86:
                        val_2 = -val_1

                self.intake_solenoid_2.set(self.num_to_solenoid(val_2))
            self.intake_solenoid_1.set(self.num_to_solenoid(val_1))

            last_input = input
            last_value = value_out
            await asyncio.sleep(0.01)

    async def wait_for_setpoint(self, setpoint, range=0.2, timeout=2):
        self.set_setpoint(setpoint)
        counter = 0
        while abs(self.get_input() - self.setpoint) > range and self.gameclock.is_enabled() and counter <= timeout:
            counter += 0.1
            await asyncio.sleep(0.1)
        if counter > timeout:
            self.logger.warn("Timeout reached before setpoint was reached! Input is {}, while setpoint is {}!".format(self.get_input(), self.setpoint))
            return False
        else:
            return True

    async def run_intake_for(self, power, time=5):
        self.auto_intake_out = power
        await asyncio.sleep(time)
        self.auto_intake_out = 0

    @staticmethod
    def num_to_solenoid(value):
        if value > 1:
            return wpilib.DoubleSolenoid.Value.kForward
        elif value < -1:
            return wpilib.DoubleSolenoid.Value.kReverse
        else:
            return wpilib.DoubleSolenoid.Value.kOff

    def set_setpoint(self, setpoint):
        self.setpoint = min(1, max(-1, setpoint))

    def module_deinit(self):
        self.intake_solenoid_1.free()
        if self.DOUBLE_SOLENOID:
            self.intake_solenoid_2.free()
        self.intake_motor.free()
        self.intake_potentiometer.free()
