import wpilib
import yeti


class BasicIntake(yeti.Module):

    USE_CAN = False

    def module_init(self):
        self.intake_solenoid_1 = wpilib.DoubleSolenoid(0, 1)
        self.intake_solenoid_2 = wpilib.DoubleSolenoid(2, 3)
        if self.USE_CAN:
            self.intake_motor = wpilib.CANTalon(6)
            self.intake_motor.enableControl()
        else:
            self.intake_motor = wpilib.Talon(7)
        self.joystick = wpilib.Joystick(1)

    def teleop_periodic(self):
        if self.joystick.getRawButton(3):
            self.intake_solenoid_1.set(wpilib.DoubleSolenoid.Value.kForward)
            self.intake_solenoid_2.set(wpilib.DoubleSolenoid.Value.kForward)
        elif self.joystick.getRawButton(2):
            self.intake_solenoid_1.set(wpilib.DoubleSolenoid.Value.kReverse)
            self.intake_solenoid_2.set(wpilib.DoubleSolenoid.Value.kReverse)
        else:
            self.intake_solenoid_1.set(wpilib.DoubleSolenoid.Value.kOff)
            self.intake_solenoid_2.set(wpilib.DoubleSolenoid.Value.kOff)
        self.intake_motor.set(-self.joystick.getY())

    def module_deinit(self):
        self.intake_solenoid_1.free()
        self.intake_solenoid_2.free()
        self.intake_motor.free()
