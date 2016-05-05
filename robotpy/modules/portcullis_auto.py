import yeti
import asyncio


class PortcullisAuto(yeti.Module):

    def module_init(self):
        self.drivetrain = self.engine.get_module("advanced_drive")
        self.intake = self.engine.get_module("advanced_intake")
        self.debug.set_code((False, False, True), "disabled")
        self.debug.set_auto_steps(6)

    @yeti.singleton
    async def autonomous_init(self):
        print("CHARGE!")
        # Drive forward and lower intake
        self.debug.set_auto_progress(0)
        self.intake.set_setpoint(-1)
        self.drivetrain.set_drive(0, -0.25, True)
        while self.drivetrain.get_incline() < 5 and self.gameclock.is_autonomous():
            await asyncio.sleep(0.05)

        # Stop and wait for intake to lower
        self.debug.set_auto_progress(1)
        self.drivetrain.set_drive(0, 0, True)
        await self.intake.wait_for_setpoint(-1)

        # Drive slowly to portcullis
        self.debug.set_auto_progress(2)
        self.drivetrain.reset_encoders()
        await asyncio.sleep(0.2)
        await self.drivetrain.drive_straight_to(0.9, -0.25)

        # Raise intake
        self.debug.set_auto_progress(3)
        await self.intake.wait_for_setpoint(0.2)

        # Drive through
        self.debug.set_auto_progress(4)
        await self.drivetrain.drive_straight_to(5, -0.65)

        # Release ball if commanded
        self.debug.set_auto_progress(4)
        await self.intake.run_intake_for(1, 10)

        # Stop
        self.debug.set_auto_progress(5)


