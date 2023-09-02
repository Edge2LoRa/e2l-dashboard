import random
import traceback

import numpy as np
import pandas as pd
import time
import logging
import paho.mqtt.client as paho
from scipy.signal import savgol_filter

SENS=[       -137,     -134.5,       -132,      -129,      -126,      -123,      -122]

#SENS=[       -137,     -134.5,       -133,      -132,      -131,      -130,      -119]
SENS=[       -137,     -134.5,       -132,      -129,      -128,      -126,      -120]
datr=["SF12BW125","SF11BW125","SF10BW125","SF9BW125","SF8BW125","SF7BW125","SF7BW250"]



class AdaptiveAlgorithm:
    def setDevRSSI(self,value):
        mqtt = paho.Client("DEVICE-MQTT-controller")
        # client1.on_publish = __on_publish  # assign function to callback
        mqtt.connect("10.8.9.27", 1883)
        mqtt.publish("/sawedemo/configuredevice/", "{},{},{}".format(-1, -1, value))  # publish

    def setDR(self, DR):
        mqtt = paho.Client("DEVICE-MQTT-controller")
        # client1.on_publish = __on_publish  # assign function to callback
        mqtt.connect("10.8.9.27", 1883)
        if DR < 2:
            DR=2
        if DR > 6:
            DR = 6
        SF= 12 - DR
        BW=7 #125
        if DR == 6:
            SF=7
            BW=8

        #self.logging.info("SF={},BW={},DR={}".format(SF, (125 if (BW==7) else 250),DR))
        mqtt.publish("/sawedemo/configuredevice/", "{},{},{}".format(SF, BW, -1))  # publish



    def __init__(self,controllerDB=None,loggingLevel=logging.INFO):
        self.controllerDB=controllerDB
        self.obs_window=1
        self.T_reaction=1
        self.logging = logging.getLogger(self.__class__.__name__)
        self.logging.setLevel(loggingLevel)

    def scaleRSSI(self,df,reset_index=True):
        ret_rssi=[]
        RSSI_MAX=-28
        RSS_STEP=-2

        for ii in range(len(df)):
            rssi = df["rssi"].iloc[ii]


            #LEV_START = 90
            #LEV_START = 81
            LEV_START = 55
            if rssi >= -RSSI_MAX:
                curr_rssi = (rssi - (LEV_START))
            elif (rssi < RSSI_MAX) and (rssi >= RSSI_MAX+RSS_STEP):
                curr_rssi = (rssi - (LEV_START+2))
            elif (rssi < RSSI_MAX+RSS_STEP) and (rssi >= RSSI_MAX+2*RSS_STEP):
                curr_rssi = (rssi - (LEV_START+4))
            elif (rssi < RSSI_MAX+2*RSS_STEP) and (rssi >= RSSI_MAX+4*RSS_STEP):
                curr_rssi =(rssi - (LEV_START+6))
            elif (rssi < RSSI_MAX+4*RSS_STEP) and (rssi >= RSSI_MAX+6*RSS_STEP):
                curr_rssi = (rssi - (LEV_START+8))
            elif (rssi < RSSI_MAX+6*RSS_STEP) and (rssi >= RSSI_MAX+8*RSS_STEP):
                curr_rssi = (rssi - (LEV_START+10))
            else:
                curr_rssi = (rssi - (LEV_START+12.5))

            dr = datr.index(df["datr"].iloc[ii])
            epsilon=1


            # Drop frame under Sensitivity
            if curr_rssi <=SENS[dr]-epsilon:
                curr_rssi=None

            ret_rssi.append(curr_rssi)
        df["rssi"]=ret_rssi

        df=df[df["rssi"].notna()]
        if reset_index:
            df = df.reset_index()
        return df
    def pippoLoop(self):
        while True:
            print("ciao")
            time.sleep(1)


    def RSSIAdaptationLoop(self):
        t_ = time.time()
        dr_=2
        while True:

            dt = time.time() - t_
            if dt > 10:
                t_ = time.time()
            try:
                df = pd.DataFrame(self.controllerDB.extractEventsDataFrame(T_window=self.obs_window))
                df = self.scaleRSSI(df)
                try:
                    df['rssi_filter'] = df[["rssi"]].apply(savgol_filter, window_length=10, polyorder=1)
                except:
                    df['rssi_filter'] = df["rssi"]
                if len(df) == 0:
                    last_rssi = np.NaN
                else:
                    last_rssi = df["rssi"].iloc[len(df) - 1]

                if pd.isna(last_rssi):
                    dr_=max(2,dr_-1)
                    self.setDR(dr_)
                else:
                    dr = max([idx for idx, v in enumerate(SENS) if v <= df['rssi_filter'].min()])
                    print("df['rssi_filter'].mean()={}, df['rssi_filter']={}".format(df['rssi_filter'].mean(),df['rssi_filter']))
                    print(max([idx for idx, v in enumerate(SENS) if v <= df['rssi_filter'].min()]))
                    if dr:
                        self.setDR(dr)
                    dr_ = dr
            except:
                traceback.print_exc()
                pass
            time.sleep(self.T_reaction)  # 10 seconds
            print(dr_)

    def AdaptationLoop(self):
        dr_penalty=list(np.zeros(len(datr)))
        t_ = time.time()
        while True:

            dt = time.time() - t_
            if dt > 10:
                dr_penalty = list(np.zeros(len(datr)))
                t_=time.time()
            try:
                action_msg="-"
                df = pd.DataFrame(self.controllerDB.extractEventsDataFrame(T_window=self.obs_window))
                #df_start['rssi'] = df_start[["rssi"]].apply(savgol_filter, window_length=10, polyorder=1)
                dr = datr.index(df["datr"].iloc[len(df) - 1])
                dr_next=dr
                df = self.scaleRSSI(df)
                try:
                    df['rssi_filter'] = df[["rssi"]].apply(savgol_filter, window_length=10, polyorder=1)
                except:
                    df['rssi_filter']=df["rssi"]
                if len(df)==0:
                    last_rssi=np.NaN
                    dr_penalty[dr]+=1
                else:
                    last_rssi= df["rssi"].iloc[len(df)-1]

                if pd.isna(last_rssi):
                    action_msg="D"
                    dr_next = max(2,(dr-1))
                    if dr_next!=dr:
                        self.setDR(dr_next)

                else:
                    if last_rssi > SENS[dr]+3: #se RSSI medio è il doppio della Sensitivity allora posso aumentare il DR
                        action_msg="U"
                        dr_next = min(6,(dr + 1))
                        if dr_next != dr:
                            self.setDR(dr_next)
                self.logging.info("dt={}\t len_df={}\t last_rssi={}  \t action={}\t DR_= {} DR={} \t penalty={}".format(np.round(dt,2),len(df),np.round(last_rssi),action_msg,dr,dr_next,dr_penalty))

            except:
                traceback.print_exc()
                pass
            time.sleep(self.T_reaction) # 10 seconds




