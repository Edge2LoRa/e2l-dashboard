import base64
import json
import socket
import traceback
from datetime import datetime
import paho.mqtt.client as paho
import pandas as pd

import paho.mqtt.client as mqtt
import logging,sys
from enum import IntEnum

import pymongo

config = {"host" : "10.8.9.27", "token":"TFyCMKn7IOl0JhYUk1J0"}

type_data = pd.DataFrame(columns=['Datetime','Traffic Type','SF_BW','RSSI','PACKET RATE'])


"""

+-----+  (LoRa)   +------+   (GATEWAY_IP/PORT)    +-------------------+  (BROKER IP/PORT)   +-------------+
| DEV |  ·····)   |  GW  |----------------------> | GW-MQTT CONNECTOR |-------------------> | MQTT BROKER | ----> your app...
+-----+           +------+                        +-------------------+                     +-------------+

"""



class TYPE(IntEnum):
    LIDAR = 0
    TEXT = 1
    AUDIO = 2
    HR = 3
import math
import g729a
class ControllerLoRaGW():
    GATEWAY_UDP_IP = "10.8.9.27";GATEWAY_UDP_PORT = 1680
    broker = "10.8.9.27"; port = 1883
    topic = "/sawedemo/firstresponder/bundledata/"

    def __init__(self,controllerMongoDB,loggingLevel=logging.INFO):
        self.logging = logging.getLogger(self.__class__.__name__)
        self.logging.setLevel(loggingLevel)
        self.controllerMongoDB=controllerMongoDB

    def runGWtoMQTTConnector(self, GATEWAY_UDP_IP=GATEWAY_UDP_IP, GATEWAY_UDP_PORT=GATEWAY_UDP_PORT, broker=broker, port=port,
                             topic=topic):

        self.logging.info("Gateway-MQTT connector CONFIGURATION")
        self.logging.info(f"GATEWAY_UDP_IP:{GATEWAY_UDP_IP}")
        self.logging.info(f"GATEWAY_UDP_PORT:{GATEWAY_UDP_PORT}:")
        self.logging.info(f"broker:{broker}")
        self.logging.info(f"port:{port}")
        #def __on_publish(self, client, userdata, result):  # create function for callback
        #    pass
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((GATEWAY_UDP_IP, GATEWAY_UDP_PORT))



        while True:
            data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
            try:

                payload = json.loads(
                    "{" + str(data).split("{", 1)[1][0:-1]
                )
                if "rxpk" in payload:
                    curr_pkt= payload["rxpk"][0]
                    pp={"freq":curr_pkt["freq"],
                        "codr":curr_pkt["codr"],
                        "datr":curr_pkt["datr"],
                        "tmst":curr_pkt["tmst"],
                        "rssi":curr_pkt["rssi"],
                        "lsnr": curr_pkt["lsnr"],
                        "size": curr_pkt["size"],
                        "data":curr_pkt["data"]
                        }
                    publish_via_MQTT=False
                    if publish_via_MQTT:
                        #Connect to Broker and send the message
                        client1 = paho.Client("GW-MQTT-connector")  # create client object
                        # client1.on_publish = __on_publish  # assign function to callback
                        client1.connect(broker, port)
                        ret = client1.publish(topic, json.dumps(pp))  # publish
                    publish_via_DB=True
                    if publish_via_DB:
                        data = pp
                        data["timestamp"] = datetime.now()
                        self.controllerMongoDB.col.insert_one(data)

            except:
                #traceback.print_exc()
                continue
