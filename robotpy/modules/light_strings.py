import yeti
import wpilib
import asyncio
import time

class LightStrings(yeti.Module):

    LED_COUNT = 180

    def module_init(self):
        self.spi_out = wpilib.SPI(1)
        self.spi_out.setMSBFirst()
        self.teleop_stage = 0
        self.LED_values = [(0, 0, 0) for _ in range(self.LED_COUNT)]
        self.autonomous = self.engine.get_module("autonomous")
        self.auto_code = False, False, False, False
        self.regions = {
           "all": (0, self.LED_COUNT),
           "bumper": (59, 97),
           "bumper1": (59, 69),
           "bumper2": (70, 79),
           "bumper3": (80, 89),
           "bumper4": (90, 97),
           "left_rail": (97, self.LED_COUNT),
           "right_rail": (0, 59)
        }
        #self.set_region("all", 0, 0, 255)
        self.disabled_init()

    async def main_loop(self):
        while True:
            self.show()
            await asyncio.sleep(0.5)

    def teleop_init(self):
        self.teleop_time = time.time()
        self.teleop_stage = 0
        self.set_region("all", 0, 255, 0)
        self.set_region("bumper", 0, 0, 255)

    def teleop_periodic(self):
        current_time = time.time()
        if current_time > self.teleop_time + 90 and self.teleop_stage < 1:
            print("Last 45 seconds!")
            self.teleop_stage = 1
            self.set_region("all", 255, 255, 0)
        elif current_time > self.teleop_time + 120 and self.teleop_stage < 2:
            print("Last 15 seconds!")
            self.teleop_stage = 2
            self.set_region("all", 255, 0, 0)

    def autonomous_init(self):
        self.set_region("all", 255, 255, 0)
        self.set_region("bumper", 0, 0, 255)

    def disabled_init(self):
        self.auto_code = False, False, False, False
        self.set_region("all", 0, 0, 255)
        self.disabled_periodic()

    def disabled_periodic(self):
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
        self.spi_out.write([0x00 for _ in range(4)])
        for r, g, b in self.LED_values:
            self.spi_out.write(bytes([255, b, g, r]))
        self.spi_out.write([0xff for _ in range(4)])
