import yeti
import asyncio


class ChevalDeFriseAuto(yeti.Module):

    def module_init(self):
        self.drivetrain = self.engine.get_module("advanced_drive")
        self.intake = self.engine.get_module("advanced_intake")
        self.debug.set_code((False, True, False), "disabled")

    @yeti.singleton
    async def autonomous_init(self):
        print("CHARGE!")
        # Drive forward
        self.intake.set_setpoint(1)
        self.debug.set_code((True, False, False, False), "auto")
        self.drivetrain.set_drive(0, -0.25, True)
        while self.drivetrain.get_incline() < 5 and self.gameclock.is_autonomous():
            await asyncio.sleep(0.05)

        # Stop and wait for intake to lower
        self.debug.set_code((False, True, False, False), "auto")
        self.drivetrain.set_drive(0, 0, True)
        await self.intake.wait_for_setpoint(-1)

        # Drive slowly over cheval
        self.debug.set_code((False, False, True, False), "auto")
        self.drivetrain.reset_encoders()
        await self.drivetrain.drive_straight_to(1, -0.35)

        # Raise intake and drive normally
        self.debug.set_code((False, False, False, True), "auto")
        self.intake.set_setpoint(0)
        self.drivetrain.reset_encoders()
        await self.drivetrain.drive_straight_to(5, -0.65)

        # Stop
        self.debug.set_code((True, True, True, True), "auto")
        self.drivetrain.set_drive(0, 0, False)
