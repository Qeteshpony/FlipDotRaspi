#!/usr/bin/env python3
import sys
print(sys.prefix, sys.base_prefix)
import time
import flipdot
from server import Server
# from getip import get_ip
from mqtt import Client
import signal


def stop(_sig=None, _frame=None):
    global running
    running = False


# catch termination signal and quit gracefully
signal.signal(signal.SIGTERM, stop)

running = True

# initialize display
display = flipdot.FlipDot()
# initialize webserver
server = Server(display)
# start mqtt client
mqtt = Client()

# display.text("IP: "+get_ip())
# time.sleep(2)
# display.clear()
display.mode = "dayclock"

if __name__ == "__main__":
    try:
        starttime = time.time()
        while running:
            server.accept_http()
            display.loop(standby=mqtt.get_standby())
            time.sleep(.01)

    except KeyboardInterrupt:
        pass

    print("Shutting down.")
    display.stop()
    exit(0)
