import base64
import json
from datetime import datetime
import pandas as pd

import paho.mqtt.client as mqtt
import logging,sys
from enum import IntEnum
config = {"host" : "10.8.9.27", "token":"TFyCMKn7IOl0JhYUk1J0"}

type_data = pd.DataFrame(columns=['Datetime','Traffic Type','SF_BW','RSSI','PACKET RATE'])


"""

+-----+  (LoRa)   +------+   (GATEWAY_IP/PORT)    +-------------------+  (BROKER IP/PORT)   +-------------+
| DEV |  ·····)   |  GW  |----------------------> | GW-MQTT CONNECTOR |-------------------> | MQTT BROKER | ----> your app...
+-----+           +------+                        +-------------------+                     +-------------+

"""



                                #establish connection
time = []
time2 = []
typed = []
rssi_received = []
sf = []
i = 0
quality=[]


class TYPE(IntEnum):
    LIDAR = 0
    TEXT = 1
    AUDIO = 2
    HR = 3
import math
import g729a
class ControllerMQTT():
    GATEWAY_UDP_IP = "10.8.9.27";GATEWAY_UDP_PORT = 1680
    broker = "10.8.9.27"; port = 1883

    def __audioEncode(self,inputAudio,type="encode"):
        coder = g729a.G729Aencoder() if type == 'encode' else g729a.G729Adecoder()  # type: G729Acoder
        outputAudio = []

        N = math.ceil(len(inputAudio) / coder.inputSize)
        for n in range(N):
            buff = inputAudio[n * coder.inputSize:(n + 1) * coder.inputSize]

            if len(buff) < coder.inputSize:
                break
            outputAudio.extend(coder.process(bytearray(buff)))
        return outputAudio

    def __init__(self,loggingLevel=logging.INFO):

        self.logging = logging.getLogger(self.__class__.__name__)
        self.logging.setLevel(loggingLevel)
        self.lidar_offsets_ctrl = []
        self.lora =[]
        self.lidar_lora = []
        self.text_lora = []
        self.audio_lora_encoded = []
        self.audio_lora_decoded = []
        self.start_new_audio_message = True
        self.client = None


    def runMQTTSubscriber(self,
            broker=broker, port=port):

        def __on_connect(client, userdata, flags, rc):  # The callback for when the client connects to the broker
            #client.subscribe("/sawedemo/controlchannel/lidar_offset/")
            self.client.subscribe("/sawedemo/#")


        def __on_message(client, userdata,
                         msg):  # The callback for when a PUBLISH message is received from the server.
            #print("Message received-> " + msg.topic + " " + str(msg.payload))  # Print a received msg

            #Control channel topic: for control data tramsitted out of lora channel
            if msg.topic == "/sawedemo/controlchannel/lidar_offset/":
                self.lidar_offsets_ctrl=str(json.loads(msg.payload))
            #Lora channel Topic: data sent by LoRa Device
            if msg.topic == "/sawedemo/firstresponder/bundledata/":
                #print("Message received-> " + msg.topic + " " + str(msg.payload))  # Print a received msg
                pkt_lora = str(json.loads(msg.payload))
                pkt_lora = json.loads(pkt_lora.replace("\'", "\""))
                #Header check
                #LIDAR


                pkt_lora = base64.b64decode(pkt_lora["data"])  # .decode(encoding='utf-8')


                app_header=pkt_lora[0:2] #get header
                app_data = pkt_lora[2:len(pkt_lora)] # get payload
                if app_header[0]==int(TYPE.LIDAR):
                    self.logging.info("LIDAR")
                    self.lidar_lora = list(app_data)
                elif app_header[0]==int(TYPE.TEXT):
                    self.logging.info("TEXT")
                    self.text_lora = {"date":datetime.now(),"value": bytes(list(app_data)).decode()}
                    self.logging.info(self.text_lora)
                elif app_header[0]==int(TYPE.AUDIO):
                    self.logging.info("AUDIO")
                    self.logging.info("self.start_new_audio_message:",self.start_new_audio_message)
                    self.logging.info("app_header[1]",app_header[1])

                    if self.start_new_audio_message==True and app_header[1]==0:
                        self.audio_lora_encoded = list(app_data)
                        self.start_new_audio_message=False
                    else:
                        self.audio_lora_encoded.append(list(app_data))
                    self.logging.info(self.audio_lora_encoded)
                    if app_header[1]==1:
                        self.logging.info("message finished")

                        #decode g729a payload

                        self.audio_lora_decoded = self.__audioEncode(self.audio_lora_encoded,type="decode")
                        #self.audio_lora_decoded =Controller.g729a.audioEncode(self.audio_lora_encoded, type="decode")
                        #self.start_new_audio_message=True #Ready for next audio message
                        self.logging.info("===========================================")
                        self.logging.info(f"self.audio_lora_encoded:{self.audio_lora_encoded}")
                        self.logging.info(f"len(self.audio_lora_encoded): {len(self.audio_lora_encoded)}")

                        self.logging.info(f"self.audio_lora_decoded:{self.audio_lora_decoded}")
                        self.logging.info(f"len(self.audio_lora_decoded):{len(self.audio_lora_decoded)}")
                        self.logging.info("===========================================")

                    #self.text_lora = {"date":datetime.now(),"value": bytes(list(app_data)).decode()}

        self.client = mqtt.Client("MQTT-MongoDB-client")  # Create instance of client with client ID “digi_mqtt_test”
        self.client.on_connect = __on_connect  # Define callback function for successful connection
        self.client.on_message = __on_message  # Define callback function for receipt of a message
        # client.connect("m2m.eclipse.org", 1883, 60)  # Connect to (broker, port, keepalive-time)

        self.client.connect(broker, port)
        #self.client.loop_forever(timeout=1000,max_packets=100)  # Start networking daemon
        #self.client.loop_start()
        self.client.loop_start()
        #self.client.loop_stop()
        #client.loop()

