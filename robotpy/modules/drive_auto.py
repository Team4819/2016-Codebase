import yeti
import asyncio


class DriveAuto(yeti.Module):

    def module_init(self):
        self.drivetrain = self.engine.get_module("advanced_drive")
        self.intake = self.engine.get_module("advanced_intake")
        self.debug.set_code((True, False, False), "disabled")
        self.debug.set_auto_steps(3)

    @yeti.singleton
    async def autonomous_init(self):
        print("CHARGE!")
        self.drivetrain.reset_encoders()
        self.debug.set_auto_progress(0)
        await self.intake.wait_for_setpoint(0)
        self.debug.set_auto_progress(1)
        await self.drivetrain.drive_straight_to(10, -0.65)
        self.debug.set_auto_progress(2)

