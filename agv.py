# import paho.mqtt.client as mqtt
# import time
# import threading 

# class AGV:
#     # def __init__(self, broker_ip="172.20.10.4", port=1883):
#     def __init__(self, broker_ip="localhost", port=1883):
#         # MQTT config
#         self.broker_ip = broker_ip
#         self.port = port
#         self.topic_request = "/agv/request"
#         self.topic_response = "/agv/response"

#         # Status: carry cargo or not
#         self.has_cargo = False

#         # Init MQTT client
#         self.client = mqtt.Client()
#         self.client.on_connect = self.on_connect
#         self.client.on_message = self.on_message
#         self.client.connect(self.broker_ip, self.port, 60)

#         # wait for load
#         threading.Thread(target=self.wait_for_load, daemon=True).start()

#     def wait_for_load(self):
#         """ 监听键盘输入，模拟人工装载货物 """
#         while True:
#             input("Press Enter to load cargo onto AGV...")
#             self.has_cargo = True
#             print("Cargo loaded! Requesting least occupied shelf...")
#             self.client.publish(self.topic_request, "Where should I go?")

#     def on_connect(self, client, userdata, flags, rc):
#         """ Connect to MQTT server """
#         print("AGV Connected")
#         self.client.subscribe(self.topic_response)

#         # Send request to central system if AGV has cargo
#         # if self.has_cargo:
#         #     print("AGV requesting least occupied shelf...")
#         #     self.client.publish(self.topic_request, "Where should I go?")

#     def on_message(self, client, userdata, msg):
#         """ Handle response from Central System """
#         if msg.topic == self.topic_response:
#             target_shelf = msg.payload.decode()
#             print(f"AGV received response: Delivering to {target_shelf}")
            
#             # Simulate transport process
#             # time.sleep(2)

#             # Transport complete
#             self.has_cargo = False
#             print(f"AGV has delivered cargo to {target_shelf}")

#     def run(self):
#         """ Run AGV """
#         print("AGV is running...")
#         self.client.loop_forever()


# if __name__ == "__main__":
#     agv = AGV()
#     agv.run()


import paho.mqtt.client as mqtt
import time
import threading

class AGV:
    def __init__(self, broker_ip="localhost", port=1883):
        # MQTT 配置
        self.broker_ip = broker_ip
        self.port = port
        self.topic_request = "/agv/request"
        self.topic_response = "/agv/response"

        # AGV 状态
        self.has_cargo = False       # 是否装载货物
        self.returning = False       # 是否正在返回起点
        self.at_destination = False  # 是否到达目标货架

        # 初始化 MQTT 客户端
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(self.broker_ip, self.port, 60)

        # 开启线程监听键盘输入
        threading.Thread(target=self.listen_keyboard, daemon=True).start()

    def listen_keyboard(self):
        """ 监听键盘输入 (适用于 PC 测试) """
        while True:
            cmd = input("Enter 'L' to load cargo, 'R' to return to start: ").strip().upper()
            if cmd == "L":
                self.load_cargo()
            elif cmd == "R":
                self.return_to_start()

    def load_cargo(self):
        """ 装载货物，发送货架请求 """
        if not self.has_cargo and not self.returning and not self.at_destination:
            self.has_cargo = True
            print("\nCargo loaded! Requesting least occupied shelf...\n")
            self.client.publish(self.topic_request, "Where should I go?")

    def return_to_start(self):
        """ 召回 AGV 到起点 """
        if self.at_destination and not self.returning:
            self.returning = True
            print("\nReturning to start position...\n")
            time.sleep(3)  # 模拟返回起点
            self.returning = False
            self.at_destination = False  # 复位状态
            print("\nAGV has returned to start position. Waiting for cargo...\n")
        else:
            print("\nAGV has not yet reached the destination. Cannot return.\n")

    def on_connect(self, client, userdata, flags, rc):
        """ 连接到 MQTT 服务器 """
        print("AGV Connected")
        self.client.subscribe(self.topic_response)

    def on_message(self, client, userdata, msg):
        """ 处理中央系统的响应 """
        if msg.topic == self.topic_response and self.has_cargo:
            target_shelf = msg.payload.decode()
            print(f"\nAGV received response: Delivering to {target_shelf}...\n")
            
            # 模拟行驶到货架
            time.sleep(3)  # 假设行驶过程需要 3 秒
            self.has_cargo = False
            self.at_destination = True  # 货物送达
            print(f"\nAGV has delivered cargo to {target_shelf}. Waiting for return command...\n")

    def run(self):
        """ 运行 AGV """
        print("AGV is running...")
        self.client.loop_forever()


if __name__ == "__main__":
    try:
        agv = AGV()
        agv.run()
    except KeyboardInterrupt:
        print("\nExiting...")
