import yeti
import wpilib
import asyncio

class LightStrings(yeti.Module):

    LED_COUNT = 60*3

    def module_init(self):
        self.spi_out = wpilib.SPI(1)
        self.spi_out.setMSBFirst()
        self.LED_values = [(0, 0, 0) for _ in range(self.LED_COUNT)]
        self.autonomous = self.engine.get_module("autonomous")
        self.auto_code = False, False, False, False
        self.regions = {
           "all": (0, self.LED_COUNT),
           "bumper": (0, 40),
           "bumper1": (0, 10),
           "bumper2": (10, 20),
           "bumper3": (20, 30),
           "bumper4": (30, 40),
           "left_rail": (40, 100),
           "right_rail": (100, 160)
        }
        self.set_region("all", 0, 0, 255)

    async def main_loop(self):
        while True:
            self.show()
            await asyncio.sleep(0.5)

    def teleop_init(self):
        self.set_region("all", 0, 255, 0)

    def autonomous_init(self):
        self.set_region("all", 255, 0, 0)

    def disabled_init(self):
        self.set_region("all", 0, 0, 255)

    def disabled_periiodic(self):
        try:
            auto_code = self.autonomous.get_led_code()
        except ValueError:
            return
        if auto_code is not self.auto_code:
            self.auto_code = auto_code
            if auto_code[0]:
                self.set_region("bumper1", 255, 255, 255)
            else:
                self.set_region("bumper1", 0, 0, 0)
            if auto_code[1]:
                self.set_region("bumper2", 255, 255, 255)
            else:
                self.set_region("bumper2", 0, 0, 0)
            if auto_code[2]:
                self.set_region("bumper3", 255, 255, 255)
            else:
                self.set_region("bumper3", 0, 0, 0)
            if auto_code[3]:
                self.set_region("bumper4", 255, 255, 255)
            else:
                self.set_region("bumper4", 0, 0, 0)

    def set_region(self, region, r, g, b):
        for i in range(*self.regions[region]):
            self.LED_values[i] = (r, g, b)
        self.show()

    def show(self):
        data = []
        data.extend([0x00 for _ in range(4)])
        for r, g, b in self.LED_values:
            data.extend(bytes([255, r, g, b]))
        data.extend([0xff for _ in range(4)])
        self.spi_out.write(data)
