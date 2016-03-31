import yeti
import asyncio


class BallAuto(yeti.Module):

    def module_init(self):
        self.drivetrain = self.engine.get_module("advanced_drive")
        self.intake = self.engine.get_module("advanced_intake")
        self.debug.set_code((True, False, True), "disabled")

    @yeti.singleton
    async def autonomous_init(self):
        print("CHARGE!")
        self.drivetrain.reset_encoders()
        self.set_step(0)
        await self.intake.wait_for_setpoint(0)
        self.set_step(1)
        await self.drivetrain.drive_straight_to(10, -0.65)
        self.set_step(2)
        await self.drivetrain.turn_to(60)
        self.set_step(3)
        self.drivetrain.reset_encoders()
        await self.drivetrain.drive_straight_to(7, -0.65)
        self.set_step(4)
        await self.intake.run_intake_for(1, 10)

    def set_step(self, step_num):
        self.debug.set_code([i == step_num for i in range(5)], "auto")
