import yeti
import wpilib
import asyncio
import math
import time
import random
import threading


class LightStrings(yeti.Module):

    #LED_COUNT = 158
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
            "demo": [(0, 0, 0) for _ in range(self.LED_COUNT)],
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
        self.active_buffer = "demo"
        self.show()

        colors = [(0, 0, 255), (255, 0, 0), (255, 255, 255), (0, 255, 0), (255, 255, 0)]
        lights = []
        last_time = time.time()
        last_spawn_check = 0
        total_energy = 600
        usable_energy = total_energy
        while True:
            await asyncio.sleep(0.01)
            current_time = time.time()
            dt = min(current_time - last_time, 1)
            if self.active_buffer != "demo":
                usable_energy = total_energy
                lights = []
                continue
            if current_time - last_spawn_check > 4:
                last_spawn_check = current_time
                velocity = random.uniform(7, 10) * random.choice((-1, 1))
                mass = random.uniform(4, 5)
                energy = velocity**2 * mass * 0.5
                if energy < usable_energy:
                    usable_energy -= energy
                    lights.append({
                        "color": random.choice(colors),
                        "position": 79,
                        "velocity": velocity,
                        "mass": mass,
                        "age": 0
                    })
            to_kill = []
            for light in lights:
                light["age"] += dt
                if light["age"] > 40:
                    to_kill.append(light)
                light["position"] = (light["position"] + light["velocity"]*dt) % self.LED_COUNT
            for light in to_kill:
                usable_energy += 0.5*light["mass"]*(light["velocity"]**2)
                lights.remove(light)
            #for light in lights:
            #    if light["position"] < light["mass"] and light["velocity"] < 0:
            #        light["velocity"] *= -1
            #    elif light["position"] > self.LED_COUNT - light["mass"] and light["velocity"] > 0:
            #        light["velocity"] *= -1
            for light in lights:
                for colliding_light in lights:
                    if colliding_light["velocity"] - light["velocity"] < 0 < \
                                    colliding_light["position"] - light["position"] <= \
                                    light["mass"]+colliding_light["mass"]:
                        m1 = light["mass"]
                        m2 = colliding_light["mass"]
                        m3 = m1 + m2
                        light["velocity"] = ((m1 - m2)/m3)*light["velocity"] + (2*m2/m3)*colliding_light["velocity"]
                        colliding_light["velocity"] = (2*m1/m3)*light["velocity"] + ((m2 - m1)/m3)*colliding_light["velocity"]

            for i in range(self.LED_COUNT):
                r = 0
                g = 0
                b = 0
                for light in lights:
                    value = max(1 - ((light["position"] - i)%self.LED_COUNT / light["mass"])**2, 0)*abs(light["velocity"])/20
                    r += light["color"][0]*value
                    g += light["color"][1]*value
                    b += light["color"][2]*value
                self.buffers["demo"][i] = (min(int(r), 255), min(int(g), 255), min(int(b), 255))
            self.show()
            last_time = current_time

    @yeti.autorun
    async def alliance_check_loop(self):
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
            self.active_buffer = "demo"
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
