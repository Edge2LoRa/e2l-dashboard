import base64
import json
import traceback
import pandas as pd
import pymongo
import paho.mqtt.client as mqtt
from scipy.signal import savgol_filter
from datetime import datetime, timedelta
import logging
import numpy as np

from enum import IntEnum
class MessageType(IntEnum):
    LIDAR = 0
    TEXT = 1
    AUDIO = 2
    HR = 3
    ERROR = -1
class AppMessage():
    def __init__(self,msg=[],loggingLevel=logging.INFO,):
        self.logging = logging.getLogger(self.__class__.__name__)
        self.logging.setLevel(loggingLevel)

        self.msg = base64.b64decode(msg)  # .decode(encoding='utf-8')

    def getHeader(self):
        return self.msg[0:2]
    def getType(self):
        try:
            return MessageType(int(self.msg[0]))
        except:
            return MessageType.ERROR
        return 0 #MessageType(int(self.msg[0]))
    def getEOP(self):
        return self.msg[1]
    def __getAppData(self):
        return self.msg[2:len(self.msg)]  # get payload

    def isLidar(self):
        return self.getHeader()[0] == int(MessageType.LIDAR)

    def isAudio(self):
        return self.getHeader()[0] == int(MessageType.AUDIO)

    def isText(self):
        return self.getHeader()[0] == int(MessageType.TEXT)
    def isHR(self):
        return self.getHeader()[0] == int(MessageType.HR)

    def getText(self):
        if self.isText():
            return bytes(list(self.msg[2:len(self.msg)])).decode()
    def getHR(self):
        if self.isHR():
            return list(self.msg[2:len(self.msg)])


    def getLidar(self):
        if self.isLidar():
            return list(self.msg[2:len(self.msg)])

    def getAudio(self):
        if self.isAudio():
            return None

    def convertRawHRtoDataFrame(self):
        data_raw = self.getHR()
        len_mac_addr = 6
        len_rssi = 1
        len_hr = 1
        row_len = len_mac_addr+len_rssi+len_hr
        data_raw_reshaped = np.array(data_raw).reshape(int(len(data_raw) /row_len), row_len)
        mac_addr=[]
        rssi=[]
        hr = []
        for i in range(len(data_raw_reshaped)):
            mac_addr_str = ''.join([hex(d)[2:] + ":" for d in data_raw_reshaped[i][0:6]])[0:-1]
            mac_addr.append(mac_addr_str)
            rssi.extend([-1 * d for d in data_raw_reshaped[i][6:7]])
            hr.extend([d for d in data_raw_reshaped[i][7:8]])

        df = pd.DataFrame()
        df["mac_address"]=mac_addr
        df["RSSI"] = rssi
        df["HR"] = hr
        return df
