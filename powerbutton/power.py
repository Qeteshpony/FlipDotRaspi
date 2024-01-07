import RPi.GPIO as GPIO
import time
import signal
import os

buttonpin = 22


def stop(_sig=None, _frame=None):
    GPIO.cleanup()
    exit(0)


# catch termination signal and quit gracefully
signal.signal(signal.SIGTERM, stop)

GPIO.setmode(GPIO.BCM)
GPIO.setup(buttonpin, GPIO.IN)

presstime = 0

try:
    print("Waiting for button-press on GPIO", buttonpin)
    while True:
        if GPIO.input(buttonpin) is GPIO.HIGH:
            if presstime > 0:
                if presstime + 1 < time.time():
                    print(" initiating reboot...")
                    os.system("reboot")
                    stop()
                presstime = 0
                print(" shutdown aborted")
        else:
            if presstime == 0:
                presstime = time.time()
                print("Button pressed ", end="")
            print(".", end="")
            if presstime + 5 < time.time():
                print(" initiating system shutdown...")
                os.system("shutdown now -h")
                stop()
        time.sleep(0.5)

except KeyboardInterrupt:
    pass

stop()
