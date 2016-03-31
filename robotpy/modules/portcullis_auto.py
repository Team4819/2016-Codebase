import yeti
import asyncio


class PortcullisAuto(yeti.Module):

    def module_init(self):
        self.drivetrain = self.engine.get_module("advanced_drive")
        self.intake = self.engine.get_module("advanced_intake")
        self.debug.set_code((False, False, True), "disabled")

    @yeti.singleton
    async def autonomous_init(self):
        print("CHARGE!")
        # Drive forward and lower intake
        self.debug.set_code((True, False, False, False, False, False), "auto")
        self.intake.set_setpoint(-1)
        self.drivetrain.set_drive(0, -0.65, True)
        while self.drivetrain.get_incline() < 5 and self.gameclock.is_autonomous():
            await asyncio.sleep(0.05)

        self.debug.set_code((False, True, False, False, False, False), "auto")
        await asyncio.sleep(.5)

        # Stop and wait for intake to lower
        self.debug.set_code((False, False, True, False, False, False), "auto")
        self.drivetrain.set_drive(0, 0, True)
        await self.intake.wait_for_setpoint(-1)

        # Drive slowly to portcullis
        self.debug.set_code((False, False, False, True, False, False), "auto")
        self.drivetrain.set_drive(0, -0.35, True)
        await asyncio.sleep(.5)

        # Raise intake and wait
        self.debug.set_code((False, False, False, False, True, False), "auto")
        self.drivetrain.set_drive(0, 0, True)
        await self.intake.wait_for_setpoint(1)

        # Drive through
        self.debug.set_code((False, False, False, False, False, True), "auto")
        self.drivetrain.set_drive(0, -0.65, True)
        await asyncio.sleep(3)

        # Stop
        self.debug.set_code((True, True, True, True, True, True), "auto")
        self.drivetrain.set_drive(0, 0, False)



