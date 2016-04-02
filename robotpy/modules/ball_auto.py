import yeti
import asyncio


class BallAuto(yeti.Module):

    def module_init(self):
        self.drivetrain = self.engine.get_module("advanced_drive")
        self.intake = self.engine.get_module("advanced_intake")
        self.debug.set_code((True, False, True), "disabled")
        self.debug.set_auto_steps(6)

    @yeti.singleton
    async def autonomous_init(self):
        print("CHARGE!")
        self.drivetrain.reset_encoders()
        self.debug.set_auto_progress(0)
        await self.intake.wait_for_setpoint(0)
        self.debug.set_auto_progress(1)
        await self.drivetrain.drive_straight_to(15, -0.65)
        self.debug.set_auto_progress(2)
        await self.drivetrain.turn_to(60)
        self.debug.set_auto_progress(3)
        #return
        self.drivetrain.reset_encoders()
        await asyncio.sleep(0.3)
        await self.drivetrain.drive_straight_to(7, -0.65)
        self.debug.set_auto_progress(4)
        await self.intake.run_intake_for(1, 10)
        self.debug.set_auto_progress(5)
