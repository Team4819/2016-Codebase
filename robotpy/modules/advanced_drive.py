import wpilib
import yeti

class AdvancedDrive(yeti.Module):
    """
    A bare-bones example of an arcade drive module.
    """

    def module_init(self):
        # Setup a device references
        self.joystick = wpilib.Joystick(0)
        self.dynamics = self.engine.get_module('dynamics_module')

    def teleop_periodic(self):
        # Get the joystick values and drive the motors.
        turn = self.joystick.getX()
        power = self.joystick.getY()

        self.dynamics["left_drive_0"].set_percent_vbus(power-turn)
        self.dynamics["left_drive_1"].set_percent_vbus(power-turn)
        self.dynamics["right_drive_0"].set_percent_vbus(-(power+turn))
        self.dynamics["right_drive_1"].set_percent_vbus(-(power+turn))

    def module_deinit(self):
        # Free the device reference
        self.left_motor.free()
        self.right_motor.free()

