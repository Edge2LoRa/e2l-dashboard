import json
import traceback
import pandas as pd
import pymongo
import paho.mqtt.client as mqtt
from scipy.signal import savgol_filter
from datetime import datetime, timedelta
import logging
import numpy as np


class ControllerMongoDB():

    broker = "10.8.9.27"; port = 1883
    mongoDBHost = "10.8.9.27"
    DB_NAME_DEF = "SECON2022_DEMO"
    COLLECTION_DEF = "dev_data"
    TOPIC_DEF = "/sawedemo/firstresponder/bundledata/"


    def __init__(self,loggingLevel=logging.INFO,
                 broker=broker, port=port, topic=TOPIC_DEF, mongoDBHost=mongoDBHost, db_name=DB_NAME_DEF, db_collection=COLLECTION_DEF):
        self.logging = logging.getLogger(self.__class__.__name__)
        self.logging.setLevel(loggingLevel)
        #Connect to DB
        self.cli = pymongo.MongoClient("mongodb://{}:27017/".format(mongoDBHost))
        self.db = self.cli[db_name]
        self.col = self.db[db_collection]

    def bindMQTTtoDB(self, broker=broker, port=port, topic=TOPIC_DEF, mongoDBHost=mongoDBHost, db_name=DB_NAME_DEF, db_collection=COLLECTION_DEF  # CONF MONGO
                     ):
        self.logging.info("run MQTT-MongoDB binder")
        self.logging.info(f"broker:{broker}")
        def on_connect(client, userdata, flags, rc):  # The callback for when the client connects to the broker
            client.subscribe(topic)

        def on_message(client, userdata, msg):  # The callback for when a PUBLISH message is received from the server.
            #print("Message received-> " + msg.topic + " " + str(msg.payload))  # Print a received msg
            # Open MongoDB
            try:
                data = json.loads(msg.payload)
                data = data
                data["timestamp"]=datetime.now()
                self.logging.info(data)
                self.col.insert_one(data)
            except:
                traceback.print_exc()
                pass


        client = mqtt.Client("MQTT-MongoDB-client")  # Create instance of client with client ID “digi_mqtt_test”
        client.on_connect = on_connect  # Define callback function for successful connection
        client.on_message = on_message  # Define callback function for receipt of a message
        # client.connect("m2m.eclipse.org", 1883, 60)  # Connect to (broker, port, keepalive-time)
        client.connect(broker, port)
        client.loop_forever()  # Start networking daemon


    def getLastFrame(self):
        return self.col.find_one().sort({'_id': pymongo.DESCENDING});

    def getLatestFrames(self,N=500):

        return self.col.find({}, sort=[('_id', pymongo.DESCENDING)]).limit(N)


    def extractEventsDataFrame(self,T_window=1):
        x=[]
        if T_window!=0:
            end_df = self.col.find_one({},sort=[('_id', pymongo.DESCENDING)])
            #end_df["timestamp"]=datetime.strptime(end_df["timestamp"], "%Y-%m-%d %H:%M:%S.%f")

            start = end_df["timestamp"] - timedelta(seconds=T_window)
            end = end_df["timestamp"]
            #start = datetime.now() - timedelta(seconds=T_window)
            #end = datetime.now()

            x = self.col.find({"timestamp": {"$gt": start, "$lte": end}})

        else:
            x = self.col.find({})
        return x