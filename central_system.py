# import paho.mqtt.client as mqtt
# import sqlite3
# import time

# class CentralSystem:
#     def __init__(self, broker_ip="172.20.10.4", port=1883):
#         # MQTT config
#         self.broker_ip = broker_ip
#         self.port = port
#         self.topic_request = "/agv/request"
#         self.topic_response = "/agv/response"

#         # Init database
#         self.init_db()

#         # Init MQTT client
#         self.client = mqtt.Client()
#         self.client.on_connect = self.on_connect
#         self.client.on_message = self.on_message
#         self.client.connect(self.broker_ip, self.port, 60)

#     def init_db(self):
#         """ Init database and create shelves table """
#         conn = sqlite3.connect("warehouse.db")
#         cursor = conn.cursor()
#         cursor.execute("""
#             CREATE TABLE IF NOT EXISTS shelves (
#                 id INTEGER PRIMARY KEY AUTOINCREMENT,
#                 name TEXT UNIQUE,
#                 item_count INTEGER DEFAULT 0
#             )
#         """)
#         cursor.execute("INSERT OR IGNORE INTO shelves (name, item_count) VALUES ('Shelf_A', 0)")
#         cursor.execute("INSERT OR IGNORE INTO shelves (name, item_count) VALUES ('Shelf_B', 0)")
#         conn.commit()
#         conn.close()
#     def print_database(self):
#         """ Print current database status """
#         conn = sqlite3.connect("warehouse.db")
#         cursor = conn.cursor()
#         cursor.execute("SELECT * FROM shelves")
#         data = cursor.fetchall()
#         conn.close()
        
#         print("Current Shelf Status:")
#         for row in data:
#             print(f"ID: {row[0]}, Name: {row[1]}, Item Count: {row[2]}")
#         print("-" * 30)
#     def get_least_occupied_shelf(self):
#         """ Query the least occupied shelf """
#         conn = sqlite3.connect("warehouse.db")
#         cursor = conn.cursor()
#         cursor.execute("SELECT name FROM shelves ORDER BY item_count ASC LIMIT 1")
#         shelf = cursor.fetchone()
#         conn.close()
#         return shelf[0] if shelf else None

#     def update_shelf(self, shelf_name):
#         """ Update the shelf count immediately after assigning it to an AGV """
#         conn = sqlite3.connect("warehouse.db")
#         cursor = conn.cursor()
#         cursor.execute("UPDATE shelves SET item_count = item_count + 1 WHERE name = ?", (shelf_name,))
#         conn.commit()
#         conn.close()
#         print(f"Updated {shelf_name}: item_count +1")

#     def on_connect(self, client, userdata, flags, rc):
#         """ Connect to MQTT server """
#         print("Central System Connected")
#         self.client.subscribe(self.topic_request)  # Subscribe to AGV's request

#     def on_message(self, client, userdata, msg):
#         """ Handle AGV requests """
#         if msg.topic == self.topic_request:
#             print("Received request from AGV")
#             least_occupied_shelf = self.get_least_occupied_shelf()
#             if least_occupied_shelf:
#                 self.update_shelf(least_occupied_shelf)  # Directly update the shelf count
#                 self.client.publish(self.topic_response, least_occupied_shelf)
#                 print(f"Sent response: {least_occupied_shelf}")
import paho.mqtt.client as mqtt
import sqlite3
import time
import threading  # 让数据库打印在后台运行，不阻塞 MQTT

class CentralSystem:
    def __init__(self, broker_ip="172.20.10.4", port=1883):
        # MQTT config
        self.broker_ip = broker_ip
        self.port = port
        self.topic_request = "/agv/request"
        self.topic_response = "/agv/response"

        # Init database
        self.init_db()

        # Init MQTT client
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(self.broker_ip, self.port, 60)

    def init_db(self):
        """ Reset and initialize database """
        conn = sqlite3.connect("warehouse.db")
        cursor = conn.cursor()

        # 确保表存在
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS shelves (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                item_count INTEGER DEFAULT 0
            )
        """)

        # **重置数据库数据**
        cursor.execute("UPDATE shelves SET item_count = 0")
        
        # 确保 Shelf_A 和 Shelf_B 存在
        cursor.execute("INSERT OR IGNORE INTO shelves (name, item_count) VALUES ('Shelf_A', 0)")
        cursor.execute("INSERT OR IGNORE INTO shelves (name, item_count) VALUES ('Shelf_B', 0)")
        
        conn.commit()
        conn.close()

    def print_database(self):
        """ Periodically print the current database status """
        while True:
            conn = sqlite3.connect("warehouse.db")
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM shelves")
            data = cursor.fetchall()
            conn.close()
            
            print("Current Shelf Status:")
            for row in data:
                print(f"ID: {row[0]}, Name: {row[1]}, Item Count: {row[2]}")
            print("-" * 30)
            time.sleep(10)  # 每 10 秒打印一次

    def get_least_occupied_shelf(self):
        """ Query the least occupied shelf """
        conn = sqlite3.connect("warehouse.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM shelves ORDER BY item_count ASC LIMIT 1")
        shelf = cursor.fetchone()
        conn.close()
        return shelf[0] if shelf else None

    def update_shelf(self, shelf_name):
        """ Update the shelf count immediately after assigning it to an AGV """
        conn = sqlite3.connect("warehouse.db")
        cursor = conn.cursor()
        cursor.execute("UPDATE shelves SET item_count = item_count + 1 WHERE name = ?", (shelf_name,))
        conn.commit()
        conn.close()
        print(f"Updated {shelf_name}: item_count +1")

    def on_connect(self, client, userdata, flags, rc):
        """ Connect to MQTT server """
        print("Central System Connected")
        self.client.subscribe(self.topic_request)  # Subscribe to AGV's request

    def on_message(self, client, userdata, msg):
        """ Handle AGV requests """
        if msg.topic == self.topic_request:
            print("Received request from AGV")
            least_occupied_shelf = self.get_least_occupied_shelf()
            if least_occupied_shelf:
                self.update_shelf(least_occupied_shelf)  # Directly update the shelf count
                self.client.publish(self.topic_response, least_occupied_shelf)
                print(f"Sent response: {least_occupied_shelf}")

    def run(self):
        """ Run MQTT listener and periodically print database status in a separate thread """
        print("Central System is running...")
        
        # **使用后台线程打印数据库，不阻塞 MQTT**
        threading.Thread(target=self.print_database, daemon=True).start()
        
        self.client.loop_forever()  # 让 MQTT 在前台运行


if __name__ == "__main__":
    system = CentralSystem()
    system.run()

#     def run(self):
#         """ Run MQTT listener """
#         print("Central System is running...")
#         self.client.loop_forever()


# if __name__ == "__main__":
#     system = CentralSystem()
#     system.run()


