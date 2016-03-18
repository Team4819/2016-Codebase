import yeti
import asyncio


class DriveAuto(yeti.Module):

    def module_init(self):
        self.drivetrain = self.engine.get_module("advanced_drive")

    def get_led_code(self):
        return False, True, True, False

    @yeti.singleton
    async def autonomous_init(self):
        print("CHARGE!")
        self.drivetrain.set_drive(0, 1, True)
        await asyncio.sleep(3.5)
        self.drivetrain.set_drive(0, 0, False)

