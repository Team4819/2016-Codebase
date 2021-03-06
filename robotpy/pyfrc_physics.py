#
# See the notes for the other physics sample
#


from pyfrc.physics import drivetrains


class PhysicsEngine(object):
    '''
       Simulates a 4-wheel robot using Tank Drive joystick control
    '''


    def __init__(self, physics_controller):
        '''
            :param physics_controller: `pyfrc.physics.core.Physics` object
                                       to communicate simulation effects to
        '''

        self.physics_controller = physics_controller

    def update_sim(self, hal_data, now, tm_diff):
        '''
            Called when the simulation parameters for the program need to be
            updated.

            :param now: The current time as a float
            :param tm_diff: The amount of time that has passed since the last
                            time that this function was called
        '''
        # Simulate the drivetrain
        if 1 in hal_data['CAN']:
            lr_motor = hal_data['CAN'][1]['value']/1024
            rr_motor = hal_data['CAN'][3]['value']/1024
            lf_motor = hal_data['CAN'][2]['value']/1024
            rf_motor = hal_data['CAN'][4]['value']/1024
        else:
            lr_motor = 0
            rr_motor = 0
            lf_motor = 0
            rf_motor = 0

        speed, rotation = drivetrains.four_motor_drivetrain(-lr_motor, -rr_motor, -lf_motor, -rf_motor)
        self.physics_controller.drive(speed, rotation, tm_diff)

