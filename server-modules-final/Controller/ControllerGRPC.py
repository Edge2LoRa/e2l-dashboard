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


    def SimpleMethodsJoinUpdateMessage(self, request, context):
        print("SimpleMethodsJoinUpdateMessage called by client(%d) the message: %s" % (request.client_id, request) )
        # print("SimpleMethod called by client(%d) the message:" % (request.client_id) )

        # print(request.key_agreement_log_message_node_id)
        # print(request.key_agreement_message_log)
        # print(request.key_agreement_process_time)

        if request.ed_id == 1:
            self.ed_1_gw_selection_confirmed = request.gw_id
            self.ed_1_gw_selection_updated = 1

        if request.ed_id == 2:
            self.ed_2_gw_selection_confirmed = request.gw_id
            self.ed_2_gw_selection_updated = 1

        if request.ed_id == 3:
            self.ed_3_gw_selection_confirmed = request.gw_id
            self.ed_3_gw_selection_updated = 1

        response = demo_pb2.ReplyLogMessage(
            server_id=SERVER_ID,
            response_data="Python server SimpleMethod Ok!!!!",
        )
        return response


    def SimpleMethodsLogMessage(self, request, context):
        print("SimpleMethodsLogMessage called by client(%d) the message: %s" % (request.client_id, request) )
        # print("SimpleMethod called by client(%d) the message:" % (request.client_id) )

        # print(request.key_agreement_log_message_node_id)
        # print(request.key_agreement_message_log)
        # print(request.key_agreement_process_time)

        if request.key_agreement_log_message_node_id == 1:
            self.controllerGRPC.devices_key_agreement_message_log = request.key_agreement_message_log
            self.controllerGRPC.devices_key_agreement_processing_time = request.key_agreement_process_time
            self.controllerGRPC.devices_key_agreement_message_log_updated = 1

        if request.key_agreement_log_message_node_id == 2:
            self.controllerGRPC.gw_key_agreement_message_log = request.key_agreement_message_log
            self.controllerGRPC.gw_key_agreement_processing_time = request.key_agreement_process_time
            self.controllerGRPC.gw_key_agreement_message_log_updated = 1

        if request.key_agreement_log_message_node_id == 3:
            self.controllerGRPC.module_key_agreement_message_log = request.key_agreement_message_log
            self.controllerGRPC.module_key_agreement_processing_time = request.key_agreement_process_time
            self.controllerGRPC.module_key_agreement_message_updated = 1

        response = demo_pb2.ReplyLogMessage(
            server_id=SERVER_ID,
            response_data="Python server SimpleMethod Ok!!!!",
        )
        return response

    # stream-unary (In a single call, the client can transfer data to the server several times,
    # but the server can only return a response once.)
    def ClientStreamingMethodStatistics(self, request_iterator, context):
        print("ClientStreamingMethod called by client...")
        print(request_iterator)

        for request in request_iterator:
            print(request)
            print("recv from client(%d), message= %s" % (request.client_id, request.message_data))

            print(request.gw_1_received_frame_num)
            print(request.gw_1_transmitted_frame_num)
            print(request.gw_2_received_frame_num)
            print(request.gw_2_transmitted_frame_num)
            print(request.ns_received_frame_frame_num)
            print(request.ns_transmitted_frame_frame_num)
            print(request.module_received_frame_frame_num)
            print(request.aggregation_function_result)

            print(self.controllerGRPC.gw_1_received_frame_num)
            self.controllerGRPC.gw_1_received_frame_num.append(request.gw_1_received_frame_num - self.controllerGRPC.gw_1_received_frame_num_last)
            self.controllerGRPC.gw_1_received_frame_num_last = request.gw_1_received_frame_num
            print(self.controllerGRPC.gw_1_received_frame_num)

            self.controllerGRPC.gw_1_transmitted_frame_num.append(request.gw_1_transmitted_frame_num - self.controllerGRPC.gw_1_transmitted_frame_last)
            self.controllerGRPC.gw_1_transmitted_frame_last = request.gw_1_transmitted_frame_num

            self.controllerGRPC.gw_2_received_frame_num.append(request.gw_2_received_frame_num - self.controllerGRPC.gw_2_received_frame_num_last)
            self.controllerGRPC.gw_2_received_frame_num_last = request.gw_2_received_frame_num

            self.controllerGRPC.gw_2_transmitted_frame_num.append(request.gw_2_transmitted_frame_num - self.controllerGRPC.gw_2_transmitted_frame_num_last)
            self.controllerGRPC.gw_2_transmitted_frame_num_last = request.gw_2_transmitted_frame_num

            self.controllerGRPC.ns_received_frame_frame_num.append(request.ns_received_frame_frame_num)
            self.controllerGRPC.ns_transmitted_frame_frame_num.append(request.ns_transmitted_frame_frame_num)

            self.controllerGRPC.module_received_frame_frame_num.append(request.module_received_frame_frame_num - self.controllerGRPC.module_received_frame_frame_num_last )
            self.controllerGRPC.module_received_frame_frame_num_last = request.module_received_frame_frame_num

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

        if self.controllerGRPC.start_key_agreement_process:
            self.controllerGRPC.start_key_agreement_process = 0

        return response

    # # unary-stream (In a single call, the client can only transmit data to the server at one time,
    # # but the server can return the response many times.)
    # def ServerStreamingMethod(self, request, context):
    #     print( "ServerStreamingMethod called by client(%d), message= %s" % (request.client_id, request.request_data) )
    #
    #     # create a generator
    #     def response_messages():
    #         for i in range(5):
    #             response = demo_pb2.Response(
    #                 server_id=SERVER_ID,
    #                 response_data="send by Python server, message=%d" % i,
    #             )
    #             yield response
    #
    #     return response_messages()
    #
    # # stream-stream (In a single call, both client and server can send and receive data
    # # to each other multiple times.)
    # def BidirectionalStreamingMethod(self, request_iterator, context):
    #     print("BidirectionalStreamingMethod called by client...")
    #
    #     # 开启一个子线程去接收数据
    #     # Open a sub thread to receive data
    #     def parse_request():
    #         for request in request_iterator:
    #             print(
    #                 "recv from client(%d), message= %s"
    #                 % (request.client_id, request.request_data)
    #             )
    #
    #     t = threading.Thread(target=parse_request)
    #     t.start()
    #
    #     for i in range(5):
    #         yield demo_pb2.Response(
    #             server_id=SERVER_ID,
    #             response_data="send by Python server, message= %d" % i,
    #         )
    #
    #     t.join()


class ControllerGRPC():
    bind_address = "0.0.0.0"
    port = "23333"

    def __init__(self, loggingLevel=logging.INFO):

        self.logging = logging.getLogger(self.__class__.__name__)
        self.logging.setLevel(loggingLevel)

        self.lora =[]
        self.text_lora = []

        self.client = None

        self.ed_1_gw_selection = 1
        self.ed_2_gw_selection = 1
        self.ed_3_gw_selection = 1

        self.start_key_agreement_process = 0
        self.start_key_agreement_process_old = 0

        self.process_function = "mean"
        self.process_window = 10

        self.change_processing_configuraiton = 0
        self.change_processing_configuraiton_old = 0

        self.gw_1_received_frame_num_last = 0
        self.gw_1_transmitted_frame_last = 0
        self.gw_2_received_frame_num_last = 0
        self.gw_2_transmitted_frame_num_last = 0
        self.ns_received_frame_frame_num_last = 0
        self.ns_transmitted_frame_frame_num_last = 0
        self.module_received_frame_frame_num_last = 0
        self.aggregation_function_result_last = 0


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

        self.devices_key_agreement_message_log = "log ED"
        self.devices_key_agreement_message_log_updated = 0
        self.devices_key_agreement_processing_time = 0
        self.gw_key_agreement_message_log = "log GW"
        self.gw_key_agreement_message_log_updated = 0
        self.gw_key_agreement_processing_time = 0
        self.module_key_agreement_message_log = "log DM"
        self.module_key_agreement_message_updated = 0
        self.module_key_agreement_processing_time = 0

        self.ed_1_gw_selection_confirmed = 0
        self.ed_2_gw_selection_confirmed = 0
        self.ed_3_gw_selection_confirmed = 0
        self.ed_1_gw_selection_updated = 0
        self.ed_2_gw_selection_updated = 0
        self.ed_3_gw_selection_updated = 0


    def runServerGRPC(self, bind_address=bind_address, port=port):
        server = grpc.server(futures.ThreadPoolExecutor())

        demo_pb2_grpc.add_GRPCDemoServicer_to_server(DemoServer(self), server)

        server.add_insecure_port(bind_address+":"+port)

        print("------------------start Python GRPC server : " + bind_address+":"+port)
        server.start()
        server.wait_for_termination()

