import datetime
from datetime import datetime, timedelta, date
import pandas as pd
import logging,sys
from enum import IntEnum

from concurrent import futures
import contextlib
import logging
import multiprocessing
import socket
import sys
import time
import collections

from concurrent import futures
import numpy as np
import grpc
import demo_pb2
import demo_pb2_grpc

import threading

type_data = pd.DataFrame(columns=['Datetime','Traffic Type','SF_BW','RSSI','PACKET RATE'])

SERVER_ID = 1

"python -m grpc_tools.protoc -I../../protos --python_out=. --pyi_out=. --grpc_python_out=. ../../protos/demo.proto"


class DemoServer(demo_pb2_grpc.GRPCDemoServicer):
    # unary-unary(In a single call, the client can only send request once, and the server can
    # only respond once.)

    def __init__(self, controllerGRPC):
        self.demoServerId = 0
        self.controllerGRPC = controllerGRPC

    def SimpleMethodGWInfo(self, request, context):
        # print("SimpleMethodGWInfo called with message: %s" % (request) )
        # update the informations in the gateway server
        self.controllerGRPC.gateways_list = request.gateway_list
        self.controllerGRPC.gateways_stats_dataframe = self.controllerGRPC.gateways_stats_dataframe.iloc[0:0]
        


        for gw in self.controllerGRPC.gateways_list:
            
            self.controllerGRPC.gateways_stats_dataframe = self.controllerGRPC.gateways_stats_dataframe._append({'Gateway ID': gw.gw_id, 'lat': gw.lat, 'lon': gw.lon, 'RX_frame': gw.rx_frame, 'TX_frame': gw.tx_frame, 'processed_frame':gw.processed_frame,'mem': gw.memory, 'cpu': gw.cpu, 'bandwidth_reduction': gw.bandwidth_reduction}, ignore_index=True)

        #print(self.controllerGRPC.gateways_stats_dataframe)
        response = demo_pb2.ReplyInfoGwList(
            server_id=SERVER_ID,
            response_data="Python server SimpleMethod Ok!!!!",
        )
        return response
    
    def SimpleMethodDevInfo(self, request, context):
        # print("SimpleMethodDevInfo called with message: %s" % (request) )
        # for dev in request.device_list:
        #     print(dev.dev_id)
        #     print(dev.lat)
        self.controllerGRPC.devices_list = request.device_list
        response = demo_pb2.ReplyInfoDevList(
            server_id=SERVER_ID,
            response_data="Python server SimpleMethod Ok!!!!",
        )
        return response
    

    def SimpleMethodsJoinUpdateMessage(self, request, context):
        print("SimpleMethodsJoinUpdateMessage called by client(%d) the message: %s" % (request.client_id, request) )
        # print("SimpleMethod called by client(%d) the message:" % (request.client_id) )

        if request.ed_id == 1:
            self.controllerGRPC.ed_1_gw_selection_confirmed = request.gw_id
            self.controllerGRPC.ed_1_gw_selection_updated = 1

        if request.ed_id == 2:
            self.controllerGRPC.ed_2_gw_selection_confirmed = request.gw_id
            self.controllerGRPC.ed_2_gw_selection_updated = 1

        if request.ed_id == 3:
            self.controllerGRPC.ed_3_gw_selection_confirmed = request.gw_id
            self.controllerGRPC.ed_3_gw_selection_updated = 1

        response = demo_pb2.ReplyLogMessage(
            server_id=SERVER_ID,
            response_data="Python server SimpleMethod Ok!!!!",
        )
        return response


    def SimpleMethodsLogMessage(self, request, context):
        # print("SimpleMethodsLogMessage called by client(%d) the message: %s" % (request.client_id, request) )
        print("SimpleMethodsLogMessage called by client(%d) the message:" % (request.client_id) )

        # print(request.key_agreement_log_message_node_id)
        # print(request.key_agreement_message_log)
        # print(request.key_agreement_process_time)
        now = date.today()
        # datetime_last = datetime.now().strftime("%H:%M:%S.%f")
        (dt, micro) = datetime.now().strftime('%H:%M:%S.%f').split('.')
        datetime_last = "%s.%03d" % (dt, int(micro) / 1000)
        return_messaage_formatted = "[{}] {}".format(datetime_last, request.key_agreement_message_log)

        if request.key_agreement_log_message_node_id == 1:
            self.controllerGRPC.key_agreement_message_log_gw1.append(return_messaage_formatted)
            # self.controllerGRPC.devices_key_agreement_message_log = request.key_agreement_message_log
            # self.controllerGRPC.devices_key_agreement_processing_time = request.key_agreement_process_time
            # self.controllerGRPC.gw1_key_agreement_message_log_updated = 1

        if request.key_agreement_log_message_node_id == 2:
            self.controllerGRPC.key_agreement_message_log_gw2.append(return_messaage_formatted)
            # self.controllerGRPC.gw_key_agreement_message_log = request.key_agreement_message_log
            # self.controllerGRPC.gw_key_agreement_processing_time = request.key_agreement_process_time
            # self.controllerGRPC.gw2_key_agreement_message_log_updated = 1

        if request.key_agreement_log_message_node_id == 3:
            self.controllerGRPC.key_agreement_message_log_ed.append(return_messaage_formatted)
            # self.controllerGRPC.module_key_agreement_message_log = request.key_agreement_message_log
            # self.controllerGRPC.module_key_agreement_processing_time = request.key_agreement_process_time
            # self.controllerGRPC.device_key_agreement_message_updated = 1

        response = demo_pb2.ReplyLogMessage(
            server_id=SERVER_ID,
            response_data="Python server SimpleMethod Ok!!!!",
        )
        return response

    # stream-unary (In a single call, the client can transfer data to the server several times,
    # but the server can only return a response once.)
    def ClientStreamingMethodStatistics(self, request_iterator, context):
        print("ClientStreamingMethod called by client...")

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
            self.controllerGRPC.gw_1_received_frame_num_sum = request.gw_1_received_frame_num
            print(self.controllerGRPC.gw_1_received_frame_num)

            self.controllerGRPC.gw_1_transmitted_frame_num.append(request.gw_1_transmitted_frame_num - self.controllerGRPC.gw_1_transmitted_frame_num_last)
            self.controllerGRPC.gw_1_transmitted_frame_num_last = request.gw_1_transmitted_frame_num
            self.controllerGRPC.gw_1_transmitted_frame_num_sum = request.gw_1_transmitted_frame_num

            self.controllerGRPC.gw_2_received_frame_num.append(request.gw_2_received_frame_num - self.controllerGRPC.gw_2_received_frame_num_last)
            self.controllerGRPC.gw_2_received_frame_num_last = request.gw_2_received_frame_num
            self.controllerGRPC.gw_2_received_frame_num_sum = request.gw_2_received_frame_num

            self.controllerGRPC.gw_2_transmitted_frame_num.append(request.gw_2_transmitted_frame_num - self.controllerGRPC.gw_2_transmitted_frame_num_last)
            self.controllerGRPC.gw_2_transmitted_frame_num_last = request.gw_2_transmitted_frame_num
            self.controllerGRPC.gw_2_transmitted_frame_num_sum = request.gw_2_transmitted_frame_num

            self.controllerGRPC.ns_received_frame_frame_num.append(request.ns_received_frame_frame_num)
            self.controllerGRPC.ns_transmitted_frame_frame_num.append(request.ns_transmitted_frame_frame_num)

            self.controllerGRPC.module_received_frame_frame_num.append(request.module_received_frame_frame_num - self.controllerGRPC.module_received_frame_frame_num_last )
            self.controllerGRPC.module_received_frame_frame_num_last = request.module_received_frame_frame_num
            self.controllerGRPC.module_received_frame_frame_num_sum = request.module_received_frame_frame_num

            print(np.array(self.controllerGRPC.module_received_frame_frame_num_sum))
            print(np.array(self.controllerGRPC.gw_1_received_frame_num_sum))
            dm_sum = np.sum(np.array(self.controllerGRPC.module_received_frame_frame_num_sum))
            gw_sum = np.sum(np.array(self.controllerGRPC.gw_1_received_frame_num_sum)) + np.sum(np.array(self.controllerGRPC.gw_2_received_frame_num_sum))
            print("test")
            print(dm_sum)
            print(gw_sum)
            if not gw_sum==0:
                self.controllerGRPC.reduction_frame_num.append(100-int(dm_sum/gw_sum*100))
            else:
                self.controllerGRPC.reduction_frame_num.append(0)
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
            scenario = self.controllerGRPC.scenario,
            assining_policy = self.controllerGRPC.assining_policy,
            refreshing_table_rate = self.controllerGRPC.refreshing_table_rate,

        )

        print("send response to statistics")
        print(self.controllerGRPC.ed_1_gw_selection)
        print(self.controllerGRPC.start_key_agreement_process)
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

        self.scenario = "Moving cluster"
        self.assining_policy = "Random"
        self.refreshing_table_rate = 1

        self.change_processing_configuraiton_old = 0
         
        self.change_processing_configuraiton = 0
        self.change_scenario_configuration = 0
        self.change_assignment_configuration = 0

        self.gw_1_received_frame_num_last = 0
        self.gw_1_transmitted_frame_num_last = 0
        self.gw_2_received_frame_num_last = 0
        self.gw_2_transmitted_frame_num_last = 0

        self.gw_1_received_frame_num_sum = 0
        self.gw_1_transmitted_frame_num_sum = 0
        self.gw_2_received_frame_num_sum = 0
        self.gw_2_transmitted_frame_num_sum = 0

        self.ns_received_frame_frame_num_last = 0
        self.ns_transmitted_frame_frame_num_last = 0
        self.module_received_frame_frame_num_last = 0
        self.module_received_frame_frame_num_sum = 0


        self.aggregation_function_result_last = 0
        self.gateway_color_dict = {}
        self.gateways_list = []
        for index, row in pd.read_csv("./gw-roma-50.csv").iterrows():
            
            self.gateways_list.append(demo_pb2.Gateway_info(gw_id=str(int(row['GW_ID'])),lat=row['lat'],lon=row['lon'],rx_frame=0,tx_frame=0,processed_frame=0,memory=0,cpu=0,bandwidth_reduction=0,coverage=row['coverage']))
            self.gateway_color_dict[int(row['GW_ID'])] = int(row['color'])
            
        


        self.devices_list = []

        self.gateways_stats_dataframe = pd.DataFrame(columns=['Gateway ID','lat','lon','RX_frame','TX_frame','processed_frame','mem','cpu','bandwidth_reduction'])


        self.gw_1_received_frame_num = collections.deque(maxlen=20)
        self.gw_1_transmitted_frame_num = collections.deque(maxlen=20)
        self.gw_2_received_frame_num = collections.deque(maxlen=20)
        self.gw_2_transmitted_frame_num = collections.deque(maxlen=20)
        self.ns_received_frame_frame_num = collections.deque(maxlen=20)
        self.ns_transmitted_frame_frame_num = collections.deque(maxlen=20)
        self.module_received_frame_frame_num = collections.deque(maxlen=20)
        self.reduction_frame_num = collections.deque(maxlen=20)
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

        # self.devices_key_agreement_message_log = "log ED"
        # self.devices_key_agreement_message_log_updated = 0
        # self.devices_key_agreement_processing_time = 0
        # self.gw_key_agreement_message_log = "log GW"
        # self.gw_key_agreement_message_log_updated = 0
        # self.gw_key_agreement_processing_time = 0
        # self.module_key_agreement_message_log = "log DM"
        # self.module_key_agreement_message_updated = 0
        # self.module_key_agreement_processing_time = 0

        self.key_agreement_message_log_gw1 = collections.deque(maxlen=50)
        self.key_agreement_message_log_gw2 = collections.deque(maxlen=50)
        self.key_agreement_message_log_ed = collections.deque(maxlen=50)

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

