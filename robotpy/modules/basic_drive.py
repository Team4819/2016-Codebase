import wpilib
import yeti
import asyncio


class BasicDrive(yeti.Module):
    """
    A bare-bones arcade drive module.
    """

    def module_init(self):
        # Setup a device references
        self.joystick = wpilib.Joystick(0)
        self.left_front_motor = wpilib.CANTalon(1)
        self.left_front_motor.enableControl()
        self.left_rear_motor = wpilib.CANTalon(2)
        self.left_rear_motor.enableControl()
        self.right_front_motor = wpilib.CANTalon(3)
        self.right_front_motor.enableControl()
        self.right_rear_motor = wpilib.CANTalon(4)
        self.right_rear_motor.enableControl()

    async def teleop_init(self):
        while self.gameclock.is_teleop():
            # Get the joystick values and drive the motors.
            turn_in = self.joystick.getX()
            power_in = self.joystick.getY()

            if power_in > 0:
                power = power_in**2
            else:
                power = -power_in**2

            if turn_in > 0:
                turn = turn_in**2
            else:
                turn = -turn_in**2

            self.left_front_motor.set(-(power-turn))
            self.left_rear_motor.set(-(power-turn))
            self.right_front_motor.set(power+turn)
            self.right_rear_motor.set(power+turn)
            await asyncio.sleep(0.05)


    def module_deinit(self):
        # Free the device references
        self.left_front_motor.free()
        self.right_front_motor.free()
        self.left_rear_motor.free()
        self.right_rear_motor.free()
