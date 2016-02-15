import wpilib
import yeti


class BasicDrive(yeti.Module):
    """
    A bare-bones example of an arcade drive module.
    """

    def module_init(self):
        # Setup a device references
        self.joystick = wpilib.Joystick(0)
        self.left_motor = wpilib.CANTalon(0)
        self.right_motor = wpilib.CANTalon(1)

    def teleop_periodic(self):
        # Get the joystick values and drive the motors.
        turn = self.joystick.getX()
        power = self.joystick.getY()

        self.left_motor.set(power-turn)
        self.right_motor.set(-(power+turn))

    def module_deinit(self):
        # Free the device reference
        self.left_motor.free()
        self.right_motor.free()
