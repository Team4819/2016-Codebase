import yeti
import asyncio
import wpilib
import json


class AutoSwitcher(yeti.Module):

    auto_module_paths = []
    sd_prefix = "autonomous/"

    def module_init(self):
        self.chooser = wpilib.SendableChooser()
        for path in self.engine.module_sets["autonomous"]:
            self.chooser.addObject(path, path)
        wpilib.SmartDashboard.putData("Autonomous Mode", self.chooser)

    async def main_loop(self):
        last_selected_auto = ""
        while True:
            selected_auto = self.chooser.getSelected()
            if last_selected_auto != selected_auto:
                if last_selected_auto != "":
                    await self.engine.stop_module(last_selected_auto)
                await self.engine.start_module(selected_auto)
                last_selected_auto = selected_auto

            await asyncio.sleep(.5)


