import wpilib
from advanced_drive import AdvancedDrive


class DynamicDrive(AdvancedDrive):
    """
    A slightly more advanced drive module.
    """

    def module_init(self):
        # Setup joystick reference
        self.joystick = wpilib.Joystick(0)
        self.dynamics = self.engine.get_module("dynamics")
        self.motors = self.dynamics.controllers
        self.navx = self.dynamics.sensors["navx"]
