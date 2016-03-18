from robot_dynamics.dynamics import MyRobotDynamics
import yeti
import asyncio


class DynamicsModule(yeti.Module):

    def module_init(self):
        self.dynamics = MyRobotDynamics.cached_init("estimation")
        self.dynamics.init_wpilib_devices()
        self.dynamics.SINK_TO_SIMPLESTREAMER = True

    async def main_loop(self):
        while True:
            self.dynamics.estimation_update(self.dynamics.tic_time + 0.05)
            await asyncio.sleep(0.05)
