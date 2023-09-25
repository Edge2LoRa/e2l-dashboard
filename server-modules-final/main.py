# from Controller.ControllerLoRaGW import ControllerLoRaGW
import time

from Controller.ControllerGRPC import ControllerGRPC
# from View.View import ViewGui
from View.View_v0_6 import ViewGui
# from Model.AdaptiveAlgorithm import AdaptiveAlgorithm
import logging

import threading
from multiprocessing import Process, Queue


bind_address = "0.0.0.0"
grpc_port = "23333"


class MainApp():

    def run(self):
        logLevel=logging.INFO
        # control MQTT
        controllerGRPC = ControllerGRPC(logLevel)

        # Control MongoDB
        controllerMongoDB = None #ControllerMongoDB(logLevel)

        # Control connection between LoRa GW packet forwarder and MQTT or MongoDB
        # controllerLoRaGW = ControllerLoRaGW(controllerMongoDB, logLevel)

        # control View
        viewGui = ViewGui(controllerGRPC=controllerGRPC, controllerDB=controllerMongoDB, loggingLevel=logging.ERROR)


        # Start MQTT subscriber for Raspberry control channel
        p3 = threading.Thread(target=controllerGRPC.runServerGRPC, kwargs={'bind_address': bind_address, 'port': grpc_port})
        p3.start()
        #
        #
        # # Start Gateway-to-MQTT connector
        # p1 = Process(target=controllerLoRaGW.runGWtoMQTTConnector, args=(
        #     GATEWAY_UDP_IP, GATEWAY_UDP_PORT, broker, broker_port))
        # p1.start()
        #
        #
        # # Start MQTT-to-MongoDB connector
        # p2 = Process(target=controllerMongoDB.bindMQTTtoDB, kwargs={
        #                     'broker':broker,
        #                     'port': broker_port,
        #                     'topic': "/sawedemo/firstresponder/bundledata/",
        #                     'mongoDBHost': MONGO_DB_IP,
        #                     'db_name': "SECON2022_DEMO",  'db_collection' : "dev_data"
        #                     }
        #              )
        #
        # p2.start()
        #
        # #DR adaptive Algorithm
        # adaptiveAlgoritm = AdaptiveAlgorithm(controllerMongoDB)
        # p4 = threading.Thread(target=adaptiveAlgoritm.RSSIAdaptationLoop)
        # p4.start()


        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)

        # Start View
        viewGui.app.run_server(host='0.0.0.0', port=8050, debug=False)

        # while True:
        #     print("1")
        #     time.sleep(1)


if __name__ == '__main__':
    MainApp().run()
