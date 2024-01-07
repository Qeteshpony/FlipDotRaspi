import smbus
import time

DEVICE_ADDRESS = 0x52
REG_MODE = 0x00
REG_ARGS = 0x01
REG_RED = 0x02
REG_GREEN = 0x03
REG_BLUE = 0x04
REG_CTRL = 0x05

class Light:
    def __init__(self, address: int = DEVICE_ADDRESS):
        self.bus = smbus.SMBus(1)
        self.address = address
        self.mode = 0x01
        self.modearg = 0x00
        self.red = 0x00
        self.green = 0xFF
        self.blue = 0x00
        self.eof = 0x17
        self.lastbrightness = 0.0
        self.on = False


    def send_data(self, register: int, data: int):
        success = False
        failcount = 0
        while not success and failcount < 10:
            try:
                self.bus.write_byte_data(self.address, register, data)
                success = True
            except IOError as e:
                print(e)
                failcount += 1
                time.sleep(0.1)

    def set_color(self, red: int, green: int, blue: int):
        self.red = red
        self.green = green
        self.blue = blue
        self.send_data(REG_RED, int(red * self.lastbrightness))
        self.send_data(REG_GREEN, int(green * self.lastbrightness))
        self.send_data(REG_BLUE, int(blue * self.lastbrightness))

    def brightness(self, brightness: float = None) -> float:
        if brightness is not None:
            if brightness > 1.0 or brightness < 0.0:
                raise ValueError("Brightness needs to be between 0.0 and 1.0")
            self.lastbrightness = brightness
            self.set_color(self.red, self.green, self.blue)
            if self.lastbrightness > 0.0:
                self.on = True
        return self.lastbrightness

    def percent(self, brightness: float) -> float:
        if 0.0 <= brightness <= 100.0:
            return self.brightness(brightness=brightness / 100)
        else:
            raise ValueError("percent must be between 0.0 and 100.0")

    def switch_off(self) -> bool:
        self.send_data(REG_MODE, 0)
        self.on = False
        return self.on

    def switch_on(self) -> bool:
        self.send_data(REG_MODE, 1)
        self.on = True
        return self.on

    def switch(self, switch: bool = None) -> bool:
        if switch is not None:
            if switch:
                return self.switch_on()
            else:
                return self.switch_off()
        return self.on
