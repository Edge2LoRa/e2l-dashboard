from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class Request(_message.Message):
    __slots__ = ["client_id", "request_data", "legacy_gw_received_frame_num", "legacy_gw_received_frame_unique_num", "legacy_gw_transmitted_frame_num", "E2L_gw_received_frame_num", "E2L_gw_received_frame_unique_num", "E2L_gw_transmitted_frame_num", "module_received_frame_from_ns_num", "module_received_frame_from_gw_num", "devices_key_agreement_message_log", "gw_key_agreement_message_log", "module_key_agreement_message_log", "key_agreement_process_time", "aggregation_function_result"]
    CLIENT_ID_FIELD_NUMBER: _ClassVar[int]
    REQUEST_DATA_FIELD_NUMBER: _ClassVar[int]
    LEGACY_GW_RECEIVED_FRAME_NUM_FIELD_NUMBER: _ClassVar[int]
    LEGACY_GW_RECEIVED_FRAME_UNIQUE_NUM_FIELD_NUMBER: _ClassVar[int]
    LEGACY_GW_TRANSMITTED_FRAME_NUM_FIELD_NUMBER: _ClassVar[int]
    E2L_GW_RECEIVED_FRAME_NUM_FIELD_NUMBER: _ClassVar[int]
    E2L_GW_RECEIVED_FRAME_UNIQUE_NUM_FIELD_NUMBER: _ClassVar[int]
    E2L_GW_TRANSMITTED_FRAME_NUM_FIELD_NUMBER: _ClassVar[int]
    MODULE_RECEIVED_FRAME_FROM_NS_NUM_FIELD_NUMBER: _ClassVar[int]
    MODULE_RECEIVED_FRAME_FROM_GW_NUM_FIELD_NUMBER: _ClassVar[int]
    DEVICES_KEY_AGREEMENT_MESSAGE_LOG_FIELD_NUMBER: _ClassVar[int]
    GW_KEY_AGREEMENT_MESSAGE_LOG_FIELD_NUMBER: _ClassVar[int]
    MODULE_KEY_AGREEMENT_MESSAGE_LOG_FIELD_NUMBER: _ClassVar[int]
    KEY_AGREEMENT_PROCESS_TIME_FIELD_NUMBER: _ClassVar[int]
    AGGREGATION_FUNCTION_RESULT_FIELD_NUMBER: _ClassVar[int]
    client_id: int
    request_data: str
    legacy_gw_received_frame_num: int
    legacy_gw_received_frame_unique_num: int
    legacy_gw_transmitted_frame_num: int
    E2L_gw_received_frame_num: int
    E2L_gw_received_frame_unique_num: int
    E2L_gw_transmitted_frame_num: int
    module_received_frame_from_ns_num: int
    module_received_frame_from_gw_num: int
    devices_key_agreement_message_log: str
    gw_key_agreement_message_log: str
    module_key_agreement_message_log: str
    key_agreement_process_time: int
    aggregation_function_result: int
    def __init__(self, client_id: _Optional[int] = ..., request_data: _Optional[str] = ..., legacy_gw_received_frame_num: _Optional[int] = ..., legacy_gw_received_frame_unique_num: _Optional[int] = ..., legacy_gw_transmitted_frame_num: _Optional[int] = ..., E2L_gw_received_frame_num: _Optional[int] = ..., E2L_gw_received_frame_unique_num: _Optional[int] = ..., E2L_gw_transmitted_frame_num: _Optional[int] = ..., module_received_frame_from_ns_num: _Optional[int] = ..., module_received_frame_from_gw_num: _Optional[int] = ..., devices_key_agreement_message_log: _Optional[str] = ..., gw_key_agreement_message_log: _Optional[str] = ..., module_key_agreement_message_log: _Optional[str] = ..., key_agreement_process_time: _Optional[int] = ..., aggregation_function_result: _Optional[int] = ...) -> None: ...

class Response(_message.Message):
    __slots__ = ["server_id", "response_data", "legacy_device_num", "E2L_device_num", "process_function", "process_window"]
    SERVER_ID_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_DATA_FIELD_NUMBER: _ClassVar[int]
    LEGACY_DEVICE_NUM_FIELD_NUMBER: _ClassVar[int]
    E2L_DEVICE_NUM_FIELD_NUMBER: _ClassVar[int]
    PROCESS_FUNCTION_FIELD_NUMBER: _ClassVar[int]
    PROCESS_WINDOW_FIELD_NUMBER: _ClassVar[int]
    server_id: int
    response_data: str
    legacy_device_num: int
    E2L_device_num: int
    process_function: str
    process_window: int
    def __init__(self, server_id: _Optional[int] = ..., response_data: _Optional[str] = ..., legacy_device_num: _Optional[int] = ..., E2L_device_num: _Optional[int] = ..., process_function: _Optional[str] = ..., process_window: _Optional[int] = ...) -> None: ...
