import wpilib
import asyncio
import yeti


class AdvancedIntake(yeti.Module):

    DOUBLE_SOLENOID = True

    MIDPOINT = 0.775
    RANGE = 0.4

    def module_init(self):
        self.intake_solenoid_1 = wpilib.DoubleSolenoid(0, 1)
        if self.DOUBLE_SOLENOID:
            self.intake_solenoid_2 = wpilib.DoubleSolenoid(2, 3)
        self.intake_motor = wpilib.CANTalon(6)
        self.intake_motor.enableControl()
        self.intake_potentiometer = wpilib.AnalogPotentiometer(0)
        self.setpoint = 0
        self.joystick = wpilib.Joystick(1)

    def teleop_periodic(self):
        self.setpoint = self.joystick.getY()

    @yeti.singleton
    async def enabled_init(self):
        last_input = 0
        last_value = 0
        while self.gameclock.is_enabled:
            if self.joystick.getRawButton(3):
                self.intake_motor.set(1)
            elif self.joystick.getRawButton(2):
                self.intake_motor.set(-1)
            else:
                self.intake_motor.set(0)

            sensor_read = self.intake_potentiometer.get()
            wpilib.SmartDashboard.putNumber("intake pot", sensor_read)
            input = (self.MIDPOINT - sensor_read) / self.RANGE
            wpilib.SmartDashboard.putNumber("intake input", input)
            error = input - self.setpoint
            velocity = (input - last_input)/0.05
            if abs(last_value) < 1:
                velocity = 0
            value_out = error*5 + velocity*0.5

            val_1 = value_out
            if self.DOUBLE_SOLENOID:
                val_2 = val_1
                if input > 0.6:
                    val_1 = 0
                    if input > 0.7:
                        val_1 = -val_2
                elif input < -0.15:
                    val_2 = 0
                    if input < -0.2:
                        val_2 = -val_1

                self.intake_solenoid_2.set(self.num_to_solenoid(val_2))
            self.intake_solenoid_1.set(self.num_to_solenoid(val_1))

            last_input = input
            last_value = value_out
            await asyncio.sleep(0.01)

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
