import yeti
import wpilib


class BasicClimber(yeti.Module):

    def module_init(self):
        self.joystick = wpilib.Joystick(0)
        self.intake = self.engine.get_module("intake")
        self.lift_talon_0 = wpilib.CANTalon(5)
        self.lift_talon_0.enableBrakeMode(True)
        self.lift_talon_1 = wpilib.CANTalon(6)
        self.lift_talon_1.enableBrakeMode(True)
        self.lift_solenoid = wpilib.Solenoid(7)
        self.lock_solenoid = wpilib.Solenoid(6)
        self.lifter_activated = False
        self.lock_activated = True

        self.unreel_for = 0

    def teleop_init(self):
        self.lift_talon_0.enableControl()
        self.lift_talon_1.enableControl()

    def teleop_periodic(self):
        if self.joystick.getRawButton(7) and not self.lifter_activated:
            self.lifter_activated = True
            self.lock_activated = False
            self.intake.set_override(True)
            self.intake.set_setpoint(1)
            self.unreel_for = 0.5
            print("lift activated!")
        elif self.joystick.getRawButton(8) and self.lifter_activated:
            self.lifter_activated = False
            self.intake.set_override(False)
            self.lock_activated = True
        elif self.joystick.getRawButton(9) and self.lifter_activated and not self.lock_activated:
            self.lock_activated = True
        elif self.joystick.getRawButton(10) and self.lifter_activated and self.lock_activated:
            self.lock_activated = False
        self.lock_solenoid.set(not self.lock_activated)
        self.lift_solenoid.set(self.lifter_activated)
        lift_out = 0
        if self.lifter_activated:
            if self.unreel_for > 0:
                self.unreel_for -= 0.05
                lift_out = 0
            elif self.joystick.getRawButton(5):
                lift_out = 0.5
            elif self.joystick.getRawButton(6):
                lift_out = 0.3
            elif self.joystick.getRawButton(3):
                lift_out = -0.5
            elif self.joystick.getRawButton(4):
                lift_out = -0.3
        self.lift_talon_0.set(lift_out)
        self.lift_talon_1.set(lift_out)

    def is_activated(self):
        return self.lifter_activated, self.lock_activated

    def disabled_init(self):
        self.lift_talon_0.disableControl()
        self.lift_talon_1.disableControl()

    def module_deinit(self):
        self.lift_talon_0.free()
        self.lift_talon_1.free()
        self.lift_solenoid.free()



