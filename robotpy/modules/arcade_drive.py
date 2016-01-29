import wpilib
import yeti
import asyncio


class ArcadeDrive(yeti.Module):
    """
    A bare-bones example of an arcade drive module.
    """

    def module_init(self):
        # Setup a device references
        self.joystick = wpilib.Joystick(0)
        self.left_motor = wpilib.Jaguar(0)
        self.right_motor = wpilib.Jaguar(1)
        self.robot_drive = wpilib.RobotDrive(leftMotor=self.left_motor, rightMotor=self.right_motor)

    async def teleop_init(self):
        while True:
            # Get the joystick values and drive the motors.
            self.arcade_drive(-self.joystick.getY(), -self.joystick.getX())
            await asyncio.sleep(0.05)

    def autonomous_init(self):
        self.robot_drive.setSafetyEnabled(False)

    def arcade_drive(self, y, x):
        self.robot_drive.arcadeDrive(y, x)

    def module_deinit(self):
        # Free the device reference
        self.robot_drive.free()

