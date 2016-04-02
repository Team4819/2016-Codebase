import yeti
import wpilib
import asyncio
import math
import time
import threading


class LightStrings(yeti.Module):

    LED_COUNT = 180

    def module_init(self):
        self.spi_out = wpilib.SPI(1)
        self.spi_out.setMSBFirst()
        self.alliance = 5
        self.ds = wpilib.DriverStation.getInstance()
        self.climber = self.engine.get_module("basic_climber")

        self.teleop_stage = 0

        self.regions = {
           "all": (0, self.LED_COUNT),
           "bumper": (59, 97),
           "left_rail": (97, self.LED_COUNT),
           "right_rail": (0, 59)
        }
        self.buffers = {
            "init": [(0, 0, 0) for _ in range(self.LED_COUNT)],
            "auto": [(0, 0, 0) for _ in range(self.LED_COUNT)],
            "teleop": [(0, 0, 0) for _ in range(self.LED_COUNT)],
            "disabled": [(0, 0, 0) for _ in range(self.LED_COUNT)]
        }
        self.active_buffer = "init"
        self.robot_started = False
        self.browned_out = False

        # Prepare buffers

        # disabled buffer: all alliance
        self.set_region("all", "disabled", 0, 0, 0)

        # auto buffer: all yellow, alliance bumper
        self.set_region("all", "auto", 255, 255, 0)

        # teleop buffer: all green, alliance bumper
        self.set_region("all", "teleop", 0, 255, 0)

    def get_alliance_color(self):
        if self.alliance is wpilib.DriverStation.Alliance.Blue:
            return 0, 0, 255
        elif self.alliance is wpilib.DriverStation.Alliance.Red:
            return 255, 0, 0
        else:
            return 0, 0, 0

    def set_alliance_color(self, r, g, b):
        self.set_region("left_rail", "disabled", r, g, b)
        self.set_region("right_rail", "disabled", r, g, b)
        #self.set_region("bumper", "teleop", r, g, b)

    async def main_loop(self):
        # Do init cycle
        self.active_buffer = "init"
        pulse_width = 5
        pulse_center = -pulse_width / 2
        while (pulse_center - self.LED_COUNT/2) < self.LED_COUNT + pulse_width/2:
            self.active_buffer = "init"
            for i in range(self.LED_COUNT):
                blue_value = 1 - ((pulse_center - i) / pulse_width)**2
                red_value = 1 - (((pulse_center - self.LED_COUNT/2) - i) / pulse_width)**2
                if blue_value > 0:
                    self.buffers["init"][i] = (0, 0, int(255 * blue_value))
                elif red_value > 0:
                    self.buffers["init"][i] = (int(255 * red_value), 0, 0)
                else:
                    self.buffers["init"][i] = (0, 0, 0)
            self.show()
            await asyncio.sleep(0.03)
            pulse_center += 4
        self.active_buffer = "disabled"
        self.show()

        while True:
            new_alliance = self.ds.getAlliance()
            if new_alliance is not self.alliance:
                self.alliance = new_alliance
                self.set_alliance_color(*self.get_alliance_color())
            if self.ds.isBrownedOut():
                self.browned_out = True
            await asyncio.sleep(1)

    def set_debug_code(self, code, buffer=None):
        if buffer is None:
            buffer = self.active_buffer
        self.logger.info("New debug code for buffer {} is {}".format(buffer, code))
        light_data = []
        for value in code:
            light_data.append((255, 255, 255) if value else (0, 0, 0))
            #light_data.append((0, 0, 255))
        self.set_region_chain("bumper", buffer, light_data)

    def teleop_init(self):
        self.teleop_time = time.time()
        self.active_buffer = "teleop"
        self.show()

    def teleop_periodic(self):
        current_time = time.time()
        climber_active, lock_active = self.climber.is_activated()
        if climber_active and lock_active:
            if self.teleop_stage != 4:
                self.set_region("all", "teleop", *self.get_alliance_color())
                self.teleop_stage = 4
        elif climber_active:
            if self.teleop_stage != 3:
                self.set_region("all", "teleop", 255, 20, 0)
                self.teleop_stage = 3
        elif current_time > self.teleop_time + 120:
            if self.teleop_stage != 2:
                print("Last 15 seconds!")
                self.teleop_stage = 2
                self.set_region("all", "teleop", 255, 0, 0)
        elif current_time > self.teleop_time + 90:
            if self.teleop_stage != 1:
                print("Last 45 seconds!")
                self.teleop_stage = 1
                self.set_region("all", "teleop", 255, 255, 0)
        elif current_time < self.teleop_time + 90:
            if self.teleop_stage != 0:
                self.teleop_stage = 0
                self.set_region("all", "teleop", 0, 255, 0)

    def autonomous_init(self):
        self.active_buffer = "auto"
        self.show()

    def disabled_init(self):
        self.robot_started = True
        if self.active_buffer != "init":
            self.active_buffer = "disabled"
        self.show()

    def set_region(self, region, buffer, r, g, b):
        for i in range(*self.regions[region]):
            self.buffers[buffer][i] = (r, g, b)
        if self.active_buffer == buffer:
            self.show()

    def set_region_chain(self, region, buffer, data):
        data_len = len(data)
        start, end = self.regions[region]
        led_count = end-start
        for i in range(start, end):
            mapped_index = math.floor(((i-start)/led_count)*data_len)
            self.buffers[buffer][i] = data[mapped_index]
        if self.active_buffer == buffer:
            self.show()

    def show(self):
        self.spi_out.write([0x00 for _ in range(4)])
        if not self.browned_out:
            for r, g, b in self.buffers[self.active_buffer]:
                self.spi_out.write(bytes([255, b, g, r]))
        else:
            for _ in range(self.LED_COUNT):
                self.spi_out.write(bytes([255, 0, 0, 0]))
        self.spi_out.write([0xff for _ in range(4)])
