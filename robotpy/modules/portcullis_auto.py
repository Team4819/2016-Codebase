import yeti
import asyncio


class PortcullisAuto(yeti.Module):

    def module_init(self):
        self.drivetrain = self.engine.get_module("advanced_drive")
        self.intake = self.engine.get_module("advanced_intake")

    def get_led_code(self):
        return True, True, True, False

    @yeti.singleton
    async def autonomous_init(self):
        print("CHARGE!")
        self.drivetrain.set_drive(0, -0.65, True)
        await self.triggers.wait_for_value(self.drivetrain.get_incline, 20, value_tolerance=5)
        #await asyncio.sleep(1)
        self.drivetrain.set_drive(0, 0, True)
        self.intake.set_setpoint(-1)
        await asyncio.sleep(.25)
        self.drivetrain.set_drive(0, -0.2, True)
        await asyncio.sleep(.5)
        self.intake.set_setpoint(1)
        self.drivetrain.set_drive(0, -0.65, True)
        await asyncio.sleep(3)
        self.drivetrain.set_drive(0, 0, False)


