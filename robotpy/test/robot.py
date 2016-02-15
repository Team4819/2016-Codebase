import wpilib

class Robot(wpilib.IterativeRobot):

    def robotInit(self):
        self.leftRear = wpilib.CANTalon(1)
        self.leftRear.enableControl()
        self.rightRear = wpilib.CANTalon(3)
        self.rightRear.enableControl()
        self.leftFront = wpilib.CANTalon(2)
        self.leftFront.enableControl()
        self.rightFront = wpilib.CANTalon(4)
        self.rightFront.enableControl()
        self.robotDrive = wpilib.RobotDrive(frontLeftMotor=self.leftFront,
                                            frontRightMotor=self.rightFront,
                                            rearLeftMotor=self.leftRear,
                                            rearRightMotor=self.rightRear)
        self.joystick = wpilib.Joystick(0)

    def teleopPeriodic(self):
        self.robotDrive.arcadeDrive(self.joystick)

if __name__ == "__main__":
    wpilib.run(Robot)