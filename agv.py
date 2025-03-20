import paho.mqtt.client as mqtt
import time

class AGV:
    def __init__(self, broker_ip="172.20.10.4", port=1883):
        # MQTT config
        self.broker_ip = broker_ip
        self.port = port
        self.topic_request = "/agv/request"
        self.topic_response = "/agv/response"

        # Status: carry cargo or not
        self.has_cargo = True

        # Init MQTT client
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(self.broker_ip, self.port, 60)

    def on_connect(self, client, userdata, flags, rc):
        """ Connect to MQTT server """
        print("AGV Connected")
        self.client.subscribe(self.topic_response)

        # Send request to central system if AGV has cargo
        if self.has_cargo:
            print("AGV requesting least occupied shelf...")
            self.client.publish(self.topic_request, "Where should I go?")

    def on_message(self, client, userdata, msg):
        """ Handle response from Central System """
        if msg.topic == self.topic_response:
            target_shelf = msg.payload.decode()
            print(f"AGV received response: Delivering to {target_shelf}")
            
            # Simulate transport process
            time.sleep(2)

            # Transport complete
            self.has_cargo = False
            print(f"AGV has delivered cargo to {target_shelf}")

    def run(self):
        """ Run AGV """
        print("AGV is running...")
        self.client.loop_forever()


if __name__ == "__main__":
    agv = AGV()
    agv.run()
