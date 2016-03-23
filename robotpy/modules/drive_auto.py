import yeti
import asyncio


class DriveAuto(yeti.Module):

    def module_init(self):
        self.drivetrain = self.engine.get_module("advanced_drive")
        self.intake = self.engine.get_module("advanced_intake")

    def get_led_code(self):
        return False, True, True, False

    @yeti.singleton
    async def autonomous_init(self):
        print("CHARGE!")
        self.intake.set_setpoint(0)
        await asyncio.sleep(4)
        self.drivetrain.set_drive(0, -0.65, True)
        await asyncio.sleep(3)
        self.drivetrain.set_drive(0, 0, False)

