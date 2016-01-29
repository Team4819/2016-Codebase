#!/usr/bin/env python3

import wpilib

class MyRobot(wpilib.IterativeRobot):
    '''Main robot class'''

    def robotInit(self):
        '''Robot-wide initialization code should go here'''

        self.lstick = wpilib.Joystick(0)

        self.l_motor = wpilib.Jaguar(0)
        self.r_motor = wpilib.Jaguar(1)


        self.robot_drive = wpilib.RobotDrive(self.l_motor, self.r_motor)



    def teleopPeriodic(self):
        '''Called when operation control mode is enabled'''

        self.robot_drive.arcadeDrive(self.lstick)


    def disabledPeriodic(self):
        pass


if __name__ == '__main__':

    wpilib.run(MyRobot,
               physics_enabled=True)


