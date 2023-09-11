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

SERVER_ADDRESS = "localhost:23333"
CLIENT_ID = 1

# 中文注释和英文翻译
# Note that this example was contributed by an external user using Chinese comments.
# In all cases, the Chinese comment text is translated to English just below it.


# 一元模式(在一次调用中, 客户端只能向服务器传输一次请求数据, 服务器也只能返回一次响应)
# unary-unary(In a single call, the client can only send request once, and the server can
# only respond once.)
def send_log_message(stub):
    print("--------------Call SimpleMethod LOG ED--------------")
    request = demo_pb2.SendLogMessage(
        client_id=CLIENT_ID,
        message_data="called by Python client",
        key_agreement_log_message_node_id = 1,
        key_agreement_message_log = "ED log message #{}".format(random.randint(3, 99)),
        key_agreement_process_time = random.randint(3, 9),
    )
    response = stub.SimpleMethodsLogMessage(request)
    print(
        "resp from server(%d), the message=%s"
        % (response.server_id, response.response_data)
    )
    print("--------------Call SimpleMethod Over---------------")


    time.sleep(2)
    print("--------------Call SimpleMethod LOG GW--------------")
    request = demo_pb2.SendLogMessage(
        client_id=CLIENT_ID,
        message_data="called by Python client",
        key_agreement_log_message_node_id = 2,
        key_agreement_message_log = "GW log message #{}".format(random.randint(3, 99)),
        key_agreement_process_time = random.randint(3, 9),
    )
    response = stub.SimpleMethodsLogMessage(request)
    print(
        "resp from server(%d), the message=%s"
        % (response.server_id, response.response_data)
    )
    print("--------------Call SimpleMethod Over---------------")

    time.sleep(2)
    print("--------------Call SimpleMethod LOG ED--------------")
    request = demo_pb2.SendLogMessage(
        client_id=CLIENT_ID,
        message_data="called by Python client",
        key_agreement_log_message_node_id = 3,
        key_agreement_message_log = "DM log message #{}".format(random.randint(3, 99)),
        key_agreement_process_time = random.randint(3, 9),
    )
    response = stub.SimpleMethodsLogMessage(request)
    print(
        "resp from server(%d), the message=%s"
        % (response.server_id, response.response_data)
    )
    print("--------------Call SimpleMethod Over---------------")



# 客户端流模式（在一次调用中, 客户端可以多次向服务器传输数据, 但是服务器只能返回一次响应）
# stream-unary (In a single call, the client can transfer data to the server several times,
# but the server can only return a response once.)
def send_statistics(stub):
    print("--------------Call ClientStreamingMethod Begin--------------")

    # 创建一个生成器
    # create a generator
    def request_messages():
        for i in range(2):
            request = demo_pb2.SendStatistics(
                client_id=CLIENT_ID,
                message_data="called by Python client, message:%d" % i,
                gw_1_received_frame_num = random.randint(3, 9),
                gw_1_transmitted_frame_num = random.randint(3, 9),
                gw_2_received_frame_num = random.randint(3, 9),
                gw_2_transmitted_frame_num = random.randint(3, 9),
                ns_received_frame_frame_num = random.randint(3, 9),
                ns_transmitted_frame_frame_num = random.randint(3, 9),
                module_received_frame_frame_num = random.randint(3, 9),
                aggregation_function_result = random.randint(3, 9),
            )
            yield request
            print(i)
            time.sleep(3)

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
    with grpc.insecure_channel(SERVER_ADDRESS) as channel:
        stub = demo_pb2_grpc.GRPCDemoStub(channel)

        for ii in range(10):
          send_log_message(stub)
          time.sleep(3)
          send_statistics(stub)

        #
        # server_streaming_method(stub)
        #
        # bidirectional_streaming_method(stub)



if __name__ == "__main__":
    main()
