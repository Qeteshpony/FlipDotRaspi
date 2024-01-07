import smbus

DEVICE_ADDRESS = 0x20


class Light:
    def __init__(self, address: int = DEVICE_ADDRESS):
        self.bus = smbus.SMBus(1)
        self.address = address
        self.lastbrightness = 0.0
        self.on = False

    def brightness(self, brightness: float = None) -> float:
        if brightness is not None:
            if brightness > 1.0 or brightness < 0.0:
                raise ValueError("Brightness needs to be between 0.0 and 1.0")
            self.bus.write_byte(self.address, int(255 * brightness))
            self.lastbrightness = brightness
            if self.lastbrightness > 0.0:
                self.on = True
        return self.lastbrightness

    def percent(self, brightness: float) -> float:
        if 0.0 <= brightness <= 100.0:
            return self.brightness(brightness=brightness / 100)
        else:
            raise ValueError("percent must be between 0.0 and 100.0")

    def switch_off(self) -> bool:
        self.bus.write_byte(self.address, 0)
        self.on = False
        return self.on

    def switch_on(self) -> bool:
        if self.lastbrightness > 0.0:
            self.brightness(self.lastbrightness)
        else:
            self.brightness(1.0)
        self.on = True
        return self.on

    def switch(self, switch: bool = None) -> bool:
        if switch is not None:
            if switch:
                return self.switch_on()
            else:
                return self.switch_off()
        return self.on
