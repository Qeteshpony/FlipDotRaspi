import paho.mqtt.client as mqtt


class Client:
    def __init__(self):
        self.display = True

        # initialize mqtt client
        self.client = mqtt.Client()
        self.client.on_connect = self._mqtt_connect
        self.client.on_message = self._mqtt_message

        # start the mqtt client and run it in background
        self.client.connect_async("mqtt.kadsen.de")
        self.client.loop_start()

    def get_display_state(self) -> bool:
        return self.display

    def get_standby(self) -> bool:
        return not self.display

    def _mqtt_connect(self, _client, _userdata, _flags, _rc):
        print("MQTT Connected")
        self.client.subscribe("home/living/displays")

    def _mqtt_message(self, _client: mqtt, _userdata, msg: mqtt.MQTTMessage):
        message = msg.payload.decode()
        print("MQTT: " + msg.topic + "=" + message)
        if msg.topic == "home/living/displays":
            if message.lower() == "on":
                self.display = True
            if message.lower() == "off":
                self.display = False
