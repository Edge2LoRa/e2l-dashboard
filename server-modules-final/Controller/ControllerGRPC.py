from datetime import datetime
import pandas as pd
import logging,sys
from enum import IntEnum

from concurrent import futures
import contextlib
import datetime
import logging
import multiprocessing
import socket
import sys
import time
import collections

from concurrent import futures

import grpc
import demo_pb2
import demo_pb2_grpc

import threading

type_data = pd.DataFrame(columns=['Datetime','Traffic Type','SF_BW','RSSI','PACKET RATE'])

SERVER_ID = 1

"python -m grpc_tools.protoc -I../../protos --python_out=. --pyi_out=. --grpc_python_out=. ../../protos/demo.proto"


class DemoServer(demo_pb2_grpc.GRPCDemoServicer):
    # 一元模式(在一次调用中, 客户端只能向服务器传输一次请求数据, 服务器也只能返回一次响应)
    # unary-unary(In a single call, the client can only send request once, and the server can
    # only respond once.)

    def __init__(self, controllerGRPC):
        self.demoServerId = 0
        self.controllerGRPC = controllerGRPC

    def SimpleMethod(self, request, context):
        print(
            "SimpleMethod called by client(%d) the message: %s"
            % (request.client_id, request.request_data)
        )

        self.controllerGRPC.legacy_gw_received_frame_num.append(request.legacy_gw_received_frame_num)
        self.controllerGRPC.legacy_gw_received_frame_unique_num.append(request.legacy_gw_received_frame_unique_num)
        self.controllerGRPC.legacy_gw_transmitted_frame_num.append(request.legacy_gw_transmitted_frame_num)
        self.controllerGRPC.E2L_gw_received_frame_num.append(request.E2L_gw_received_frame_num)
        self.controllerGRPC.E2L_gw_received_frame_unique_num.append(request.E2L_gw_received_frame_unique_num)
        self.controllerGRPC.E2L_gw_transmitted_frame_num.append(request.E2L_gw_transmitted_frame_num)
        self.controllerGRPC.module_received_frame_from_ns_num.append(request.module_received_frame_from_ns_num)
        self.controllerGRPC.module_received_frame_from_gw_num.append(request.module_received_frame_from_gw_num)
        self.controllerGRPC.key_agreement_process_time.append(request.key_agreement_process_time)
        self.controllerGRPC.aggregation_function_result.append(request.aggregation_function_result)

        self.controllerGRPC.devices_key_agreement_message_log = request.devices_key_agreement_message_log
        self.controllerGRPC.gw_key_agreement_message_log = request.gw_key_agreement_message_log
        self.controllerGRPC.module_key_agreement_message_log = request.module_key_agreement_message_log

        response = demo_pb2.Response(
            server_id=SERVER_ID,
            response_data="Python server SimpleMethod Ok!!!!",
            legacy_device_num = self.controllerGRPC.legacy_device_num,
            E2L_device_num = self.controllerGRPC.E2L_device_num,
            process_function = self.controllerGRPC.process_function,
            process_window = self.controllerGRPC.process_window,
        )
        return response

    # 客户端流模式（在一次调用中, 客户端可以多次向服务器传输数据, 但是服务器只能返回一次响应）
    # stream-unary (In a single call, the client can transfer data to the server several times,
    # but the server can only return a response once.)
    def ClientStreamingMethodStatistics(self, request_iterator, context):
        print("ClientStreamingMethod called by client...")

        for request in request_iterator:
            print(
                "recv from client(%d), message= %s"
                % (request.client_id, request.message_data)
            )

            self.controllerGRPC.gw_1_received_frame_num.append(request.gw_1_received_frame_num)
            self.controllerGRPC.gw_1_transmitted_frame_num.append(request.gw_1_transmitted_frame_num)
            self.controllerGRPC.gw_2_received_frame_num.append(request.gw_2_received_frame_num)
            self.controllerGRPC.gw_2_transmitted_frame_num.append(request.gw_2_transmitted_frame_num)
            self.controllerGRPC.ns_received_frame_frame_num.append(request.ns_received_frame_frame_num)
            self.controllerGRPC.ns_transmitted_frame_frame_num.append(request.ns_transmitted_frame_frame_num)
            self.controllerGRPC.module_received_frame_frame_num.append(request.module_received_frame_frame_num)
            self.controllerGRPC.aggregation_function_result.append(request.aggregation_function_result)

        response = demo_pb2.ReplyStatistics(
            server_id=SERVER_ID,
            response_data="Python server ClientStreamingMethod ok",
            ed_1_gw_selection = self.controllerGRPC.ed_1_gw_selection,
            ed_2_gw_selection = self.controllerGRPC.ed_2_gw_selection,
            ed_3_gw_selection = self.controllerGRPC.ed_3_gw_selection,
            start_key_agreement_process = self.controllerGRPC.start_key_agreement_process,
            process_function = self.controllerGRPC.process_function,
            process_window = self.controllerGRPC.process_window,
        )
        return response

    # 服务端流模式（在一次调用中, 客户端只能一次向服务器传输数据, 但是服务器可以多次返回响应）
    # unary-stream (In a single call, the client can only transmit data to the server at one time,
    # but the server can return the response many times.)
    def ServerStreamingMethod(self, request, context):
        print(
            "ServerStreamingMethod called by client(%d), message= %s"
            % (request.client_id, request.request_data)
        )

        # 创建一个生成器
        # create a generator
        def response_messages():
            for i in range(5):
                response = demo_pb2.Response(
                    server_id=SERVER_ID,
                    response_data="send by Python server, message=%d" % i,
                )
                yield response

        return response_messages()

    # 双向流模式 (在一次调用中, 客户端和服务器都可以向对方多次收发数据)
    # stream-stream (In a single call, both client and server can send and receive data
    # to each other multiple times.)
    def BidirectionalStreamingMethod(self, request_iterator, context):
        print("BidirectionalStreamingMethod called by client...")

        # 开启一个子线程去接收数据
        # Open a sub thread to receive data
        def parse_request():
            for request in request_iterator:
                print(
                    "recv from client(%d), message= %s"
                    % (request.client_id, request.request_data)
                )

        t = threading.Thread(target=parse_request)
        t.start()

        for i in range(5):
            yield demo_pb2.Response(
                server_id=SERVER_ID,
                response_data="send by Python server, message= %d" % i,
            )

        t.join()


class ControllerGRPC():
    bind_address = "0.0.0.0"
    port = "50051"
    E2L_IP = "10.8.9.27"
    E2L_PORT = "1680"


    def __init__(self, loggingLevel=logging.INFO):

        self.logging = logging.getLogger(self.__class__.__name__)
        self.logging.setLevel(loggingLevel)

        self.lora =[]
        self.text_lora = []

        self.client = None

        self.ed_1_gw_selection = 1
        self.ed_2_gw_selection = 1
        self.ed_3_gw_selection = 1
        self.process_function="mean"
        self.process_window=10
        self.start_key_agreement_process = 0

        self.gw_1_received_frame_num = collections.deque(maxlen=20)
        self.gw_1_transmitted_frame_num = collections.deque(maxlen=20)
        self.gw_2_received_frame_num = collections.deque(maxlen=20)
        self.gw_2_transmitted_frame_num = collections.deque(maxlen=20)
        self.ns_received_frame_frame_num = collections.deque(maxlen=20)
        self.ns_transmitted_frame_frame_num = collections.deque(maxlen=20)
        self.module_received_frame_frame_num = collections.deque(maxlen=20)
        self.aggregation_function_result = collections.deque(maxlen=20)

        self.gw_1_received_frame_num.append(0)
        self.gw_1_transmitted_frame_num.append(0)
        self.gw_2_received_frame_num.append(0)
        self.gw_2_transmitted_frame_num.append(0)
        self.ns_received_frame_frame_num.append(0)
        self.ns_transmitted_frame_frame_num.append(0)
        self.module_received_frame_frame_num.append(0)
        self.aggregation_function_result.append(0)

        self.gw_1_received_frame_num.append(1)
        self.gw_1_transmitted_frame_num.append(1)
        self.gw_2_received_frame_num.append(1)
        self.gw_2_transmitted_frame_num.append(1)
        self.ns_received_frame_frame_num.append(1)
        self.ns_transmitted_frame_frame_num.append(1)
        self.module_received_frame_frame_num.append(1)
        self.aggregation_function_result.append(1)

        self.devices_key_agreement_message_log = "log1"
        self.gw_key_agreement_message_log = "log2"
        self.module_key_agreement_message_log = "log3"

    """
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

        """

    def runServerGRPC(self, bind_address=bind_address, port=port):
        server = grpc.server(futures.ThreadPoolExecutor())

        demo_pb2_grpc.add_GRPCDemoServicer_to_server(DemoServer(self), server)

        server.add_insecure_port(bind_address+":"+port)

        print("------------------start Python GRPC server : " + bind_address+":"+port)
        server.start()
        server.wait_for_termination()

