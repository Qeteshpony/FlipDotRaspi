#!/usr/bin/env python3
import sys
print(sys.prefix, sys.base_prefix)
import time
# from random import random
import flipdot
from server import Server
from getip import get_ip
from mqtt import Client
import signal
import cProfile


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

# display.text("IP: "+get_ip(), show=False)
# display.transition_scroll()
# time.sleep(2)
# display.clear()
# display.transition_scroll(reverse=True)
# display.ticker("FAKE MEWS!!!! FAKE MEWS!!!!")
display.mode = "dayclock"

if __name__ == "__main__":
    try:
        # nextcode = 0
        starttime = time.time()
        while running:
            # if nextcode < time.time():
            #    nextcode = time.time() + random()*10+10
            #    display.text("abcabdabcs")
            #    display.lastClock = ""
            server.accept_http()
            display.loop(standby=mqtt.get_standby())
            time.sleep(.01)

    except KeyboardInterrupt:
        pass

    print("Shutting down.")
    display.stop()
    exit(0)
