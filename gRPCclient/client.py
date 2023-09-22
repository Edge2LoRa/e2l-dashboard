# Copyright 2019 gRPC authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""The example of four ways of data transmission using gRPC in Python."""

import time

import grpc
import random

import demo_pb2
import demo_pb2_grpc

__all__ = [
    "send_log_message",
    "send_statistics",
    "server_streaming_method",
    "bidirectional_streaming_method",
]

SERVER_ADDRESS = "lab.tti.unipa.it:23333"
CLIENT_ID = 1

gw_1_received_frame_num_old = 0
gw_1_transmitted_frame_num_old = 0
gw_2_received_frame_num_old = 0
gw_2_transmitted_frame_num_old = 0
module_received_frame_frame_num_old = 0


# Note that this example was contributed by an external user using Chinese comments.
# In all cases, the Chinese comment text is translated to English just below it.

def send_join_update_message(stub):
  ed_id = [1, 3, 3, 3, 1, 3, 1, 3, 3, 3, 1, 3, 1, 3, 3, 3, 1, 3, 1]
  gw_id = [1, 1, 2, 1, 2, 2, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2]
  for ii in range(5):
    request = demo_pb2.SendJoinUpdateMessage(
      client_id=CLIENT_ID,
      message_data="called by Python client",
      ed_id=ed_id[ii],
      gw_id=gw_id[ii],
    )
    response = stub.SimpleMethodsJoinUpdateMessage(request)
    print(
      "resp from server(%d), the message=%s"
      % (response.server_id, response.response_data)
    )
    time.sleep(2)

  #
  # time.sleep(2)
  # print("--------------Call SimpleMethod LOG GW--------------")
  # request = demo_pb2.SendLogMessage(
  #     client_id=CLIENT_ID,
  #     message_data="called by Python client",
  #     key_agreement_log_message_node_id = 2,
  #     key_agreement_message_log = "GW log message #{}".format(random.randint(3, 99)),
  #     key_agreement_process_time = random.randint(3, 9),
  # )
  # response = stub.SimpleMethodsLogMessage(request)
  # print(
  #     "resp from server(%d), the message=%s"
  #     % (response.server_id, response.response_data)
  # )
  # print("--------------Call SimpleMethod Over---------------")
  #
  # time.sleep(2)
  # print("--------------Call SimpleMethod LOG ED--------------")
  # request = demo_pb2.SendLogMessage(
  #     client_id=CLIENT_ID,
  #     message_data="called by Python client",
  #     key_agreement_log_message_node_id = 3,
  #     key_agreement_message_log = "DM log message #{}".format(random.randint(3, 99)),
  #     key_agreement_process_time = random.randint(3, 9),
  # )
  # response = stub.SimpleMethodsLogMessage(request)
  # print(
  #     "resp from server(%d), the message=%s"
  #     % (response.server_id, response.response_data)
  # )
  # print("--------------Call SimpleMethod Over---------------")


# unary-unary(In a single call, the client can only send request once, and the server can
# only respond once.)
def send_log_message(stub):
    log_id = [1, 3, 3, 3, 1, 3, 1, 3, 3, 3, 1, 3, 1, 3, 3, 3, 1, 3, 1]
    log_message = ["Added GW info in DM active directory",
                   "Starting Edge Join", "Send EdgeJoinRequest", "Received EdgeAcceptRequest",
                   "Received Device 007599CB Public Info",
                   "Edge Join Completed",
                   "Edge Join Completed",
                   "Starting Edge Join", "Send EdgeJoinRequest",
                   "Received EdgeAcceptRequest", "Received Device 007599CB Public Info",
                   "Edge Join Completed", "Edge Join Completed",
                   "Starting Edge Join", "Send EdgeJoinRequest",
                   "Received EdgeAcceptRequest", "Received Device 00E7EB5A Public Info",
                   "Edge Join Completed", "Edge Join Completed"]
    for ii in range(5):
        request = demo_pb2.SendLogMessage(
            client_id=CLIENT_ID,
            message_data="called by Python client",
            key_agreement_log_message_node_id = log_id[ii],
            key_agreement_message_log = log_message[ii],
            key_agreement_process_time = random.randint(3, 9),
        )
        response = stub.SimpleMethodsLogMessage(request)
        print(
            "resp from server(%d), the message=%s"
            % (response.server_id, response.response_data)
        )
        time.sleep(2)

    #
    # time.sleep(2)
    # print("--------------Call SimpleMethod LOG GW--------------")
    # request = demo_pb2.SendLogMessage(
    #     client_id=CLIENT_ID,
    #     message_data="called by Python client",
    #     key_agreement_log_message_node_id = 2,
    #     key_agreement_message_log = "GW log message #{}".format(random.randint(3, 99)),
    #     key_agreement_process_time = random.randint(3, 9),
    # )
    # response = stub.SimpleMethodsLogMessage(request)
    # print(
    #     "resp from server(%d), the message=%s"
    #     % (response.server_id, response.response_data)
    # )
    # print("--------------Call SimpleMethod Over---------------")
    #
    # time.sleep(2)
    # print("--------------Call SimpleMethod LOG ED--------------")
    # request = demo_pb2.SendLogMessage(
    #     client_id=CLIENT_ID,
    #     message_data="called by Python client",
    #     key_agreement_log_message_node_id = 3,
    #     key_agreement_message_log = "DM log message #{}".format(random.randint(3, 99)),
    #     key_agreement_process_time = random.randint(3, 9),
    # )
    # response = stub.SimpleMethodsLogMessage(request)
    # print(
    #     "resp from server(%d), the message=%s"
    #     % (response.server_id, response.response_data)
    # )
    # print("--------------Call SimpleMethod Over---------------")



# 客户端流模式（在一次调用中, 客户端可以多次向服务器传输数据, 但是服务器只能返回一次响应）
# stream-unary (In a single call, the client can transfer data to the server several times,
# but the server can only return a response once.)

def send_statistics(stub):
    print("--------------Call ClientStreamingMethod Begin--------------")

    # 创建一个生成器
    # create a generator
    def request_messages():
        for i in range(1):
            request = demo_pb2.SendStatistics(
                client_id=CLIENT_ID,
                message_data="called by Python client, message:%d" % i,
                gw_1_received_frame_num = gw_1_received_frame_num_old,
                gw_1_transmitted_frame_num = gw_1_transmitted_frame_num_old,
                gw_2_received_frame_num = gw_2_received_frame_num_old,
                gw_2_transmitted_frame_num = gw_2_transmitted_frame_num_old,
                ns_received_frame_frame_num = 0,
                ns_transmitted_frame_frame_num = 0,
                module_received_frame_frame_num = module_received_frame_frame_num_old,
                aggregation_function_result = random.randint(3, 9),
            )
            yield request
            print(i)
            time.sleep(1)

    response = stub.ClientStreamingMethodStatistics(request_messages())
    print(
        "resp from server(%d), the message=%s"
        % (response.server_id, response)
    )
    # print(response.ed_1_gw_selection)
    # print(response.ed_1_gw_selection)
    # print(response.ed_2_gw_selection)
    print(response.start_key_agreement_process)
    # print(response.process_window)
    # print(response.process_window)
    # print(response.change_processing_configuraiton)


    print("--------------Call ClientStreamingMethod Over---------------")


# 服务端流模式（在一次调用中, 客户端只能一次向服务器传输数据, 但是服务器可以多次返回响应）
# unary-stream (In a single call, the client can only transmit data to the server at one time,
# but the server can return the response many times.)
def server_streaming_method(stub):
    print("--------------Call ServerStreamingMethod Begin--------------")
    request = demo_pb2.Request(
        client_id=CLIENT_ID, request_data="called by Python client"
    )
    response_iterator = stub.ServerStreamingMethod(request)
    for response in response_iterator:
        print(
            "recv from server(%d), message=%s"
            % (response.server_id, response.response_data)
        )

    print("--------------Call ServerStreamingMethod Over---------------")


# 双向流模式 (在一次调用中, 客户端和服务器都可以向对方多次收发数据)
# stream-stream (In a single call, both client and server can send and receive data
# to each other multiple times.)
def bidirectional_streaming_method(stub):
    print(
        "--------------Call BidirectionalStreamingMethod Begin---------------"
    )

    # 创建一个生成器
    # create a generator
    def request_messages():
        for i in range(5):
            request = demo_pb2.Request(
                client_id=CLIENT_ID,
                request_data="called by Python client, message: %d" % i,
            )
            yield request
            time.sleep(1)

    response_iterator = stub.BidirectionalStreamingMethod(request_messages())
    for response in response_iterator:
        print(
            "recv from server(%d), message=%s"
            % (response.server_id, response.response_data)
        )

    print("--------------Call BidirectionalStreamingMethod Over---------------")



def main():
    global gw_1_received_frame_num_old
    global gw_1_transmitted_frame_num_old
    global gw_2_received_frame_num_old
    global gw_2_transmitted_frame_num_old
    global module_received_frame_frame_num_old

    with grpc.insecure_channel(SERVER_ADDRESS) as channel:
        stub = demo_pb2_grpc.GRPCDemoStub(channel)

        for ii in range(100):
          send_join_update_message(stub)
          time.sleep(3)

          # send_log_message(stub)
          # time.sleep(3)
          #
          # gw_1_received_frame_num_old += random.randint(3, 9)
          # gw_1_transmitted_frame_num_old += random.randint(3, 9)
          # gw_2_received_frame_num_old += random.randint(3, 9)
          # gw_2_transmitted_frame_num_old += random.randint(3, 9)
          # module_received_frame_frame_num_old += random.randint(3, 9)
          #
          # send_statistics(stub)

        #
        # server_streaming_method(stub)
        #
        # bidirectional_streaming_method(stub)



if __name__ == "__main__":
    main()
