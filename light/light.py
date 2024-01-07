from i2c_light_rgb import Light
import paho.mqtt.client as mqtt
import json
import uuid
import socket
import signal
import sys
import logging
from logging.handlers import RotatingFileHandler

# todo: change HASS discovery for dual color light

MQTT_SERVER = "mqtt.kadsen.de"
MQTT_COMMAND_TOPIC = "flipdot/command"
MQTT_STATE_TOPIC = "flipdot/state"
MQTT_BRIGHTNESS_STATE_TOPIC_W = "flipdot/state/brightness"
MQTT_BRIGHTNESS_STATE_TOPIC_UV = "flipdot/state/brightness"
MQTT_LWT_TOPIC = "flipdot/LWT"
MQTT_DISCOVERY_TOPIC = "homeassistant/light/flipdot/config"

SOCKET_ADDRESS = "127.0.0.1"
SOCKET_PORT = 1254

START_BRIGHTNESS = 0.3

LOGFILE = "/run/light/log"
STATEFILE = "/run/light/brightness"


def mqtt_connect(_client, _userdata, _flags, rc):
    logger.info("MQTT connected with redult code " + str(rc))
    client.subscribe(MQTT_COMMAND_TOPIC)
    client.publish(MQTT_LWT_TOPIC, "online", retain=True)
    hass_discovery()


def mqtt_message(_client: mqtt, _userdata, msg: mqtt.MQTTMessage):
    logger.info("MQTT: " + msg.topic + "=" + msg.payload.decode())
    message = msg.payload.decode()
    parse_message(message)


def parse_message(message: str) -> None:
    if message.lower() == "on":
        light.switch_on()
    elif message.lower() == "off":
        light.switch_off()
    elif message.isnumeric():
        newbrightness = int(message)
        if 0 <= newbrightness <= 255:
            light.brightness(newbrightness / 255)
        else:
            logger.error("Invalid Brightness Value", newbrightness)
    publish_state()


def hass_discovery() -> None:
    logger.info("Sending HASS Discovery Message")
    mac = '-'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff) for ele in range(0, 8 * 6, 8)][::-1])
    payload = {
        "name": "FlipDotLight",
        "device_class": "light",
        "state_topic": MQTT_STATE_TOPIC,
        "command_topic": MQTT_COMMAND_TOPIC,
        "unique_id": mac + "-light",
        "brightness": True,
        "brightness_scale": 255,
        "brightness_state_topic": MQTT_BRIGHTNESS_STATE_TOPIC_W,
        "brightness_command_topic": MQTT_COMMAND_TOPIC,
        "device": {
            "name": "FlipDotDisplay",
            "identifiers": [mac],
            "manufacturer": "Qetesh",
            "model": "FlipDotController Raspi Edition",
            "hw_version": "2.1",
            "sw_version": "2.0",
        },
        "availability_topic": MQTT_LWT_TOPIC,
    }
    client.publish(MQTT_DISCOVERY_TOPIC, json.dumps(payload), retain=True)
    publish_state()


def publish_state() -> None:
    logger.debug("Publish state")
    client.publish(MQTT_STATE_TOPIC, "ON" if light.switch() and light.brightness() else "OFF")
    client.publish(MQTT_BRIGHTNESS_STATE_TOPIC_W, int(light.brightness()*255))
    try:
        with open(STATEFILE, "w") as statefile:
            statefile.write(str(int(light.brightness() * 255)) if light.on else "0")
    except:
        pass


def cleanup(_sig=None, _frame=None) -> None:
    logger.info("Cleaning up")
    client.loop_stop()
    server.close()
    light.switch_off()
    sys.exit(0)


def loop() -> None:
    try:
        while True:
            conn, addr = server.accept()
            data = conn.recv(32)
            socketmessage = data.decode()
            logger.info("Socket: " + socketmessage)
            parse_message(socketmessage)
            conn.send(str(int(light.brightness() * 255)).encode() if light.on else "0".encode())
            conn.close()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    # set up logger
    logger = logging.getLogger()
    try:
        handler = RotatingFileHandler(LOGFILE, maxBytes=10000, backupCount=5)
    except FileNotFoundError:
        print("Can't open Logfile. Logging to stderr")
        logger.addHandler(logging.StreamHandler())
    else:
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    # catch termination signal and quit gracefully
    signal.signal(signal.SIGTERM, cleanup)

    # initialize the I2C light
    light = Light()
    light.brightness(START_BRIGHTNESS)
    light.switch_on()

    # initialize the mqtt client
    logger.info("Setting up MQTT")
    client = mqtt.Client()
    client.enable_logger(logger)
    client.on_connect = mqtt_connect
    client.on_message = mqtt_message
    client.will_set(MQTT_LWT_TOPIC, "offline", retain=True)

    # start the mqtt client and run it in background
    client.connect_async(MQTT_SERVER)
    client.loop_start()

    # initialize the socket for receiving local commands
    logger.info("Setting up socket")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # reuse socket address in case of script crash/restart
    server.bind((SOCKET_ADDRESS, SOCKET_PORT))
    server.listen(5)

    # start the loop
    loop()

    # clean up in case the loop gets interrupted
    cleanup()
