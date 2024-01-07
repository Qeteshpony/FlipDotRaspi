import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)


def cleanup():
    GPIO.cleanup()


class Pin:
    """
    Simplify the GPIO API and make it compatible with the micropython implementation
    """

    OUT = GPIO.OUT
    IN = GPIO.IN

    def __init__(self, gpio: int, direction: int, value: int = None) -> None:
        self.gpio = gpio
        GPIO.setwarnings(False)
        GPIO.setup(self.gpio, direction)
        if value is not None:
            GPIO.output(self.gpio, value)

    def value(self, value: int) -> None:
        GPIO.output(self.gpio, value)

    def on(self) -> None:
        GPIO.output(self.gpio, 1)

    def off(self) -> None:
        GPIO.output(self.gpio, 0)
