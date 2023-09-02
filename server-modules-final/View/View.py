# Import required libraries

import logging,sys
import time
import traceback
import collections

import datetime
from datetime import datetime, timedelta, date
from datetime import datetime as dttime

import dash_daq as daq
from plotly.subplots import make_subplots

# import pandas as pd

import sys
import dash
from dash import html
from dash import dcc
from dash import no_update
from dash.dependencies import Input, Output, State


# import numpy as np
import plotly.graph_objs as go
# from Controller.ControllerDB import ControllerMongoDB

# from Model.AppMessage import AppMessage, MessageType
# from Model.LoRaToA import LoRaToA
# from Model.AdaptiveAlgorithm import AdaptiveAlgorithm
# from scipy.signal import savgol_filter

logLevel=logging.INFO
logging.basicConfig(stream=sys.stdout, level=logLevel)

import plotly
import json

N_SEC=24


def audioEncode(inputAudio, type):
    outputAudio=[]
    return outputAudio


# get relative data folder
#PATH = pathlib.Path(__file__).parent
#DATA_PATH = PATH.joinpath("data").resolve()


class ViewGui:

    def __init__(self, controllerGRPC, controllerDB, loggingLevel=logging.INFO):

        self.logging = logging.getLogger(self.__class__.__name__)
        self.logging.setLevel(loggingLevel)

        self.lidar_offsets_ctrl=json.loads(json.dumps("[[]]"))
        self.lidar_lora = json.loads(json.dumps(""))

        self.text_lora = {}
        self.T_window = 60

        self.app = dash.Dash(__name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}])
        self.app.logger.setLevel(loggingLevel)

        logDevices = collections.deque(maxlen=20)
        logGateways = collections.deque(maxlen=20)
        logDistributed = collections.deque(maxlen=20)


        self.slider_legacy_device_num = 2
        self.slider_E2L_device_num = 2
        self.dropdown_process_function = "mean"
        self.dropdown_process_window = 40

        self.app.title = "MOBICOM 2023 DEMO"

        self.processingFunctions = ["mean", "max", "min", "std"]
        self.processingWindows = [10, 20, 30, 40, 50, 60]

        # Create app layout
        header = html.Div(
            [

                html.Div(
                    [
                        html.Img(
                            src=self.app.get_asset_url("Uniroma1.png"),
                            id="plotly-image-sapienza",
                            style={
                                "height": "80px",
                                "width": "auto",
                                "margin-bottom": "1px",
                            },
                        ),
                        html.Img(
                            src=self.app.get_asset_url("logo-unipa.png"),
                            id="plotly-image-unipa",
                            style={
                                "height": "80px",
                                "width": "auto",
                                "margin-bottom": "1px",
                            },
                        ),
                        html.Img(
                            src=self.app.get_asset_url("logo_unidata.png"),
                            id="plotly-image-unidata",
                            style={
                                "height": "80px",
                                "width": "auto",
                                "margin-bottom": "1px",
                            },
                        )
                    ],
                    className="one-third column",
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.H3(
                                    "Enabling Edge processing on LoRaWAN architecture",
                                    style={"margin-bottom": "0px"},
                                ),
                                html.H5("Stefano Milani, Ioannis Chatzigiannakis, Domenico Garlisi, Matteo Di Fraia, Patrizio Pisani", style={"margin-top": "0px"}
                                ),
                            ]
                        )
                    ],
                    className="one-half column",
                    id="title",
                ),

            ],
            id="header",
            className="row flex-display",
            style={"margin-bottom": "25px"},
        )

        content_pkt_stats = html.Div([
            # LORA EVENTS TIMING VISUALIZER
            dcc.Interval(
                id='interval-component',
                interval=1000,
                n_intervals=0
            ),
            # dcc.Interval(
            #     id='interval-component-HR',
            #     interval=30*1000,
            #     n_intervals=0
            # ),
            # dcc.Interval(
            #     id='interval-component-Lid',
            #     interval = 1000,
            #     n_intervals=0
            # ),
            html.Div([
                #FIRST SUB-ROW: POWER INTERFACE, regulate TX POWER GAIN

                #SECOND SUB-ROW: show current value of RSSI and DR
                # html.Div([
                #     html.Div("RSSI",className="pretty_container five columns"),
                #     html.Div("DR",className="pretty_container six columns")
                # ]),
                #THIRD SUB-ROW: show LIDAR data
                # LIDAR POLAR PLOT
                # SCENARIO CONFIGURATION
                html.Div(
                    [html.H6("SCENARIO CONFIGURATION", className="graph__title"),

                     html.Label('Select the legacy device number'),
                     dcc.Slider(0, 5, 1, value=self.slider_legacy_device_num, id='legacy-device-num'),
                     html.Div(id='slider-output-1'),

                     html.Label('Select the E2L device number'),
                     dcc.Slider(0, 5, 1, value=self.slider_E2L_device_num, id='E2L-device-num'),
                     html.Div(id='slider-output-2'),

                     html.Button('Update configuration', id='updateScenarioConfigurationButton', style={'text-align': 'center', 'vertical-align': 'middle', }),
                     html.Div(id='updateScenarioConfigurationDiv'),

                     # html.Div(id='output-container-button-app12', children='',
                              #  style={'width': '20%', 'hight':'40', 'backgroundColor':'#F7FBFE', 'marginLeft': 10, 'marginRight': 10, 'marginTop': 10, 'marginBottom': 10,
                              # 'border': 'thin lightgrey dashed', 'padding': '10px 10px 10px 10px', 'display': 'inline-block', 'vertical-align': 'top'}
                              # ),

                     ],
                    className="pretty_container seven columns",
                ),

                html.Div(
                    [
                     html.H6("STREAM PROCESSING CONFIGURATION", className="graph__title"),
                     # dcc.Graph(id='HR-graph', animate=False, style={"height":300}, config={'displayModeBar': False}),

                        html.Label('Select the aggregation function'),
                        dcc.Dropdown(
                        id='processing-function-dropdown',
                        options=[
                            {'label': '{}'.format(self.processingFunctions[index]),
                             'value': '{}'.format(self.processingFunctions[index])} for index in range(len(self.processingFunctions) - 1)
                        ],
                        value=self.processingFunctions[0]
                        ),

                        html.Label('Select the windows size'),
                        dcc.Dropdown(
                            id='processing-window-dropdown',
                            options=[
                                {'label': '{}'.format(self.processingWindows[index]),
                                 'value': '{}'.format(self.processingWindows[index])} for index in range(len(self.processingWindows) - 1)
                            ],
                            value=self.processingWindows[0]
                        ),

                        html.Button('Update processing configuration', id='updateProcessingConfigurationButton', style={'text-align': 'center', 'vertical-align': 'middle', }),
                        html.Div(id='updateProcessingConfigurationDiv'),

                    ],
                    className="pretty_container seven columns"
                ),
                # LOG MESSAGE CONSOLE
                html.Div(
                    [
                        html.Div([
                            html.H6("Devices key agreement log message", className="log_container_devices"),
                            html.Div(id="textarea-log-devices", children=[],
                                     style={"overflow": "scroll", 'height': 250, "background-color": "#f8f9fa"},
                                     )]
                            , className="pretty_container"),

                    ],
                    className="pretty_container seven columns",
                ),
                html.Div(
                    [
                        html.Div([
                            html.H6("Gateways key agreement log message", className="log_container_gateways"),
                            html.Div(id="textarea-log-gateways", children=[],
                                     style={"overflow": "scroll", 'height': 250, "background-color": "#f8f9fa"},
                                     )], className="pretty_container"),
                    ],
                    className="pretty_container seven columns",
                ),
                html.Div(
                    [
                        html.Div([
                            html.H6("Distributed module key agreement log message", className="log_container_gateways"),
                            html.Div(id="textarea-log-distributed", children=[],
                                     style={"overflow": "scroll", 'height': 250, "background-color": "#f8f9fa"},
                                     )], className="pretty_container"),
                    ],
                    className="pretty_container seven columns",
                ),

            ], className="four columns"),

                html.Div(
                    [
                        html.H6("LoRa Traffic", className="graph_title"),

                        dcc.Graph(id="lora-traffic-graph",animate=False,style={"height":650}, config={'displayModeBar': False}),

                        # dcc.Dropdown(
                        #     id='dropdown-scenario-spazio-radio',
                        #     options=[
                        #         {'label': 'CC00', 'value': 'CC00'},
                        #         {'label': 'PR00', 'value': 'PR00'},
                        #         {'label': 'Simul', 'value': 'Simul'},
                        #     ],
                        #     value='CC00'
                        # ),
                        # dcc.Dropdown(
                        #     id='dropdown-scenario-period',
                        #     options=[
                        #         {'label': 'Period 1 (2019-10-21)', 'value': '2019-10-21'},
                        #         {'label': 'Period 2 (2019-09-23)', 'value': '2019-09-23'},
                        #         {'label': 'Period 3 (2019-08-11)', 'value': '2019-08-12'},
                        #         {'label': 'Period 4 (2019-05-12)', 'value': '2019-05-13'},
                        #     ],
                        #     value='2019-10-21'
                        # ),
                        dcc.ConfirmDialog(id='confirm-dialog-app8', message='Please wait for complete!', ),

                        dcc.Store(id="session", storage_type="session"),
                        dcc.Dropdown(
                            id="dropdown-1",
                            options=[
                                {"label": "a", "value": "a"},
                                {"label": "b", "value": "b"},
                                {"label": "c", "value": "c"},
                            ],
                            placeholder="Choose a value",
                            value=None,
                        ),
                        dcc.Dropdown(
                            id="dropdown-2",
                            options=[
                                {"label": "d", "value": "d"},
                                {"label": "e", "value": "e"},
                                {"label": "f", "value": "f"},
                            ],
                            placeholder="Choose a value",
                            value=None,
                        ),
                        html.Div(id="textarea-1", children=[]),
                    ],
                    className="pretty_container five columns",
                ),
            ],
            #className="row flex-display",
        )
        self.app.layout = html.Div(
            [
                header,
                # dcc.Tabs(id="tabs-elements", value='tab-1-graph', children=[
                #     dcc.Tab(label='Device Interface', value='tab-2-graph'),
                #     dcc.Tab(label='Control Room', value='tab-1-graph'),
                #
                # ]),
                html.Div([content_pkt_stats]),
                #html.Div(id='tabs-container'),
                #content_row1,
                #content_row2,
            ],
            id="mainContainer",
            #style={"display": "flex", "flex-direction": "column"},
        )

        ########################
        #CALLBACKS
        ########################

        # @self.app.callback(
        #     [Output('confirm-dialog-app8', 'displayed'),
        #      Output('confirm-dialog-app8', 'message'),
        #      ],
        #     [Input('dropdown-scenario-spazio-radio', 'value'),
        #      Input('dropdown-scenario-period', 'value')])
        # def display_value_2_app12(selectedSpazioRadio, selectedScenario):
        #     global currentScenario
        #     global currentSpazioRadio
        #     print(selectedSpazioRadio)
        #     print(selectedScenario)
        #     currentScenario = selectedScenario
        #     currentSpazioRadio = selectedSpazioRadio
        #     messageDisplayString = 'Sent change spazio radio and period command'
        #     return True, messageDisplayString

        @self.app.callback(
            [Output('confirm-dialog-app8', 'displayed'), Output('confirm-dialog-app8', 'message')],
            [Input('legacy-device-num', 'value'), Input('E2L-device-num', 'value'),
             Input('processing-function-dropdown', 'value'), Input('processing-window-dropdown', 'value')])
        def update_output(legacyDeviceNum, e2lDeviceNum, processingFunction, processingWindow):

            controllerGRPC.legacy_device_num = legacyDeviceNum
            controllerGRPC.E2L_device_num = e2lDeviceNum
            controllerGRPC.process_function = processingFunction
            controllerGRPC.process_window = processingWindow

            messageDisplayString = 'Sent change command : ' + str(processingFunction)

            return True, messageDisplayString


        @self.app.callback(
            [Output("textarea-1", "children"), Output("session", "data"),
             Output('textarea-log-devices', 'children'),
             Output('textarea-log-gateways', 'children'),
             Output('textarea-log-distributed', 'children')],
            [Input('interval-component', 'n_intervals'), Input("dropdown-1", "value"), Input("dropdown-2", "value")],
            State("session", "data"),
            # prevent_initial_call=True,
        )
        def update_text_input(n, dd1, dd2, data):

            # print(dd1, dd2, data, file=sys.stderr)
            # if not data:
            #     print(dd1, dd2, data, file=sys.stderr)
            #     return no_update, {"dd1": None, "dd2": None}, "test1", "test2", "test3"
            # if dd1 and (dd1 != data["dd1"]):
            #     return [dd1], {"dd1": dd1, "dd2": data["dd2"]}, "test1", "test2", "test3"
            # if dd2 and (dd2 != data["dd2"]):
            #     return [dd2], {"dd1": data["dd1"], "dd2": dd2}, "test1", "test2", "test3"

            try:
                return_messaage_ed = controllerGRPC.devices_key_agreement_message_log
                return_messaage_gw = controllerGRPC.gw_key_agreement_message_log
                return_messaage_ds = controllerGRPC.module_key_agreement_message_log
                today = date.today()
                # today -= timedelta(days=3) #timedelta(days=6)
                datetime_last = datetime.strptime(today.strftime("%Y-%m-%d"), '%Y-%m-%d')
                print("return message : ",return_messaage_ds)
                if return_messaage_ed and return_messaage_gw and return_messaage_ds:

                    return_messaage_formatted = "[{}] {}".format(datetime_last, return_messaage_ed)
                    logDevices.append(return_messaage_formatted)
                    html_return_content_ed = []
                    for ii in range(len(logDevices)):
                        html_return_content_ed.append(html.Div(logDevices[ii], style={"font-weight": "bold"}))
                        # html_return_content.append(html.P("[{}] ".format("AUDIO MESSAGE"), style={"font-weight": "bold", "color":"red"}))
                        html_return_content_ed.append(html.Br())

                    return_messaage_formatted = "[{}] {}".format(datetime_last, return_messaage_gw)
                    logGateways.append(return_messaage_formatted)
                    html_return_content_gw = []
                    for ii in range(len(logGateways)):
                        html_return_content_gw.append(html.Div(logGateways[ii], style={"font-weight": "bold"}))
                        # html_return_content.append(html.P("[{}] ".format("AUDIO MESSAGE"), style={"font-weight": "bold", "color":"red"}))
                        html_return_content_gw.append(html.Br())

                    return_messaage_formatted = "[{}] {}".format(datetime_last, return_messaage_ds)
                    logDistributed.append(return_messaage_formatted)
                    html_return_content_ds = []
                    for ii in range(len(logDistributed)):
                        html_return_content_ds.append(html.Div(logDistributed[ii], style={"font-weight": "bold"}))
                        # html_return_content.append(html.P("[{}] ".format("AUDIO MESSAGE"), style={"font-weight": "bold", "color":"red"}))
                        html_return_content_ds.append(html.Br())

                    return no_update, data, html.Div(html_return_content_ed), html.Div(html_return_content_gw), html.Div(html_return_content_ds)
                else:
                    return no_update, data, "test1", "test2", "test3"

            except Exception as e:
                traceback.print_exc()
                pass


            return no_update, data, "test1", "test2", "test3"

        @self.app.callback(Output('lora-traffic-graph', 'figure'),
                           Input('interval-component', 'n_intervals'))
        def update_lora_traffic_graph_live(n):
            try:
                if True > 0:
                    if True:
                        ble_dev_list = list(["1", "2", "3"])
                        # Prepare figure
                        fig = make_subplots(
                            rows=2, cols=1,
                            shared_xaxes=True,
                            vertical_spacing=0.09,
                        )

                        ble_plot_colors = ["red", "green", "blue", "orange", "black"]
                        # print(list(controllerGRPC.legacy_gw_received_frame_num))
                        # print(list(controllerGRPC.E2L_gw_received_frame_num))

                        legacy_gw_received_frame_num_list = list(controllerGRPC.legacy_gw_received_frame_num)
                        legacy_gw_received_frame_unique_num_list = list(controllerGRPC.legacy_gw_received_frame_unique_num)
                        legacy_gw_transmitted_frame_num_list = list(controllerGRPC.legacy_gw_transmitted_frame_num)

                        timetsamp_list = list(range(len(legacy_gw_received_frame_num_list)))

                        fig.add_trace(go.Scatter(x=timetsamp_list, y=legacy_gw_received_frame_num_list,
                                                 mode='lines+markers', line=dict(color=ble_plot_colors[0]), name="received_frame"
                                                 ), row=1, col=1,
                                      )
                        fig.add_trace(go.Scatter(x=timetsamp_list, y=legacy_gw_received_frame_unique_num_list,
                                                 mode='lines+markers', line=dict(color=ble_plot_colors[1]), name="received_frame_unique"
                                                 ), row=1, col=1,
                                      )
                        fig.add_trace(go.Scatter(x=timetsamp_list, y=legacy_gw_received_frame_num_list,
                                                 mode='lines+markers', line=dict(color=ble_plot_colors[2]), name="transmitted_frame"
                                                 ), row=1, col=1,
                                      )

                        E2L_gw_received_frame_num_list = list(controllerGRPC.E2L_gw_received_frame_num)
                        E2L_gw_received_frame_unique_list = list(controllerGRPC.E2L_gw_received_frame_unique_num)
                        E2L_gw_transmitted_frame_num_list = list(controllerGRPC.E2L_gw_transmitted_frame_num)
                        fig.add_trace(go.Scatter(x=timetsamp_list, y=E2L_gw_received_frame_num_list,
                                                 mode='lines+markers', line=dict(color=ble_plot_colors[0]), name="received_frame"
                                                 ), row=2, col=1,
                                      )
                        fig.add_trace(go.Scatter(x=timetsamp_list, y=E2L_gw_received_frame_unique_list,
                                                 mode='lines+markers', line=dict(color=ble_plot_colors[1]), name="received_frame_unique"
                                                 ), row=2, col=1,
                                      )
                        fig.add_trace(go.Scatter(x=timetsamp_list, y=E2L_gw_transmitted_frame_num_list,
                                                 mode='lines+markers', line=dict(color=ble_plot_colors[2]), name="transmitted_frame"
                                                 ), row=2, col=1,
                                      )

                        fig.update_yaxes(row=1, col=1, title_text='Legacy GW Statistics')
                        fig.update_yaxes(row=2, col=1, title_text='Edge2Lora GW Statistics')
                        fig.update_layout( margin=dict(l=10, r=10, t=10, b=10), )
                        return fig

            except Exception as e:
                traceback.print_exc()
                pass

            # @self.app.callback( Output('textarea-log-devices', 'children'),
        #     Input('interval-component', 'n_intervals'),
        #     State('textarea-log-devices', 'children')
        # )
        # def update_text(n, div_children_ed):
        #
        #     try:
        #         return_messaage_ed = controllerGRPC.devices_key_agreement_message_log
        #         return_messaage_gw = controllerGRPC.gw_key_agreement_message_log
        #         return_messaage_ds = controllerGRPC.module_key_agreement_message_log
        #         today = date.today()
        #         # today -= timedelta(days=3) #timedelta(days=6)
        #         datetime_last = datetime.strptime(today.strftime("%Y-%m-%d"), '%Y-%m-%d')
        #         print("return message : ",return_messaage_ds)
        #         if return_messaage_ed and return_messaage_gw and return_messaage_ds:
        #
        #             return_messaage_formatted = "[{}] {}".format(datetime_last, return_messaage_ed)
        #             logDevices.append(return_messaage_formatted)
        #             html_return_content_ed = []
        #             for ii in range(len(logDevices)):
        #                 html_return_content_ed.append(html.Div(logDevices[ii], style={"font-weight": "bold"}))
        #                 # html_return_content.append(html.P("[{}] ".format("AUDIO MESSAGE"), style={"font-weight": "bold", "color":"red"}))
        #                 html_return_content_ed.append(html.Br())
        #
        #             return_messaage_formatted = "[{}] {}".format(datetime_last, return_messaage_gw)
        #             logGateways.append(return_messaage_formatted)
        #             html_return_content_gw = []
        #             for ii in range(len(logGateways)):
        #                 html_return_content_gw.append(html.Div(logGateways[ii], style={"font-weight": "bold"}))
        #                 # html_return_content.append(html.P("[{}] ".format("AUDIO MESSAGE"), style={"font-weight": "bold", "color":"red"}))
        #                 html_return_content_gw.append(html.Br())
        #
        #             return_messaage_formatted = "[{}] {}".format(datetime_last, return_messaage_ds)
        #             logDistributed.append(return_messaage_formatted)
        #             html_return_content_ds = []
        #             for ii in range(len(logDistributed)):
        #                 html_return_content_ds.append(html.Div(logDistributed[ii], style={"font-weight": "bold"}))
        #                 # html_return_content.append(html.P("[{}] ".format("AUDIO MESSAGE"), style={"font-weight": "bold", "color":"red"}))
        #                 html_return_content_ds.append(html.Br())
        #
        #             return html.Div(html_return_content_ed)
        #         else:
        #             return div_children_ed
        #
        #     except Exception as e:
        #         traceback.print_exc()
        #         pass


            # if not (len(return_message) == 0):
            #
            #     return json.dumps(return_message, default=str, indent=4, )
            """
            if not(len(return_message)==0):
                json_return_message = json.dumps(return_message, default=str, indent=4, )
                if not(textarea_value is None):
                    last_message = json.loads(textarea_value[len(textarea_value)-1])
                    if str(return_message["datetime"]) != str(last_message["datetime"]):
                        textarea_value.append(json_return_message)
                        return textarea_value[::-1]
                    else:
                        return textarea_value[::-1]

                else:
                    return [json_return_message]
            """

        """
        @self.app.callback(
            Output('lidar-graph-polar', 'figure'),
            [Input('interval-component-Lidar', 'n_intervals')]
        )

        def update_graph_polar(n):
            try:
                data_lidar_lora=[]
                if len(data_lidar_lora)!=0:
                    if len(data_lidar_lora)%2==0:
                        data_lidar_lora=LidarDataProcess(N_SEC).decompress_data(
                            np.reshape(data_lidar_lora, (-1, 2))
                        )
                        angles_deg = np.degrees([2 * i * np.pi / N_SEC for i in range(N_SEC)])
                        self.R_lidar_lora = list(data_lidar_lora)
                        self.Theta_lidar_lora = angles_deg
                        res = np.argwhere(np.array(self.R_lidar_lora) != 0)
                        idx = np.where(np.array(self.R_lidar_lora) != 0)
                        idx = list(idx[0])
                        self.R_lidar_lora = list(np.array(self.R_lidar_lora)[idx])
                        self.Theta_lidar_lora = list(np.array(self.Theta_lidar_lora)[idx])

                else:
                    self.R_lidar_lora = [0]
                    self.Theta_lidar_lora = [0]

            except Exception as e:
                traceback.print_exc()
                self.R_lidar_lora = [0]
                self.Theta_lidar_lora = [0]


            try:

                data_offsets_ctrl = [] #np.array(json.loads(controllerMQTT.lidar_offsets_ctrl))
                if data_offsets_ctrl.size!=0:
                    self.R_lidar = data_offsets_ctrl[:,1]
                    self.Theta_lidar= np.degrees(data_offsets_ctrl[:,0])
                else:
                    self.R_lidar = [0]
                    self.Theta_lidar = [0]
            except Exception as e:

                #print(traceback.format_exc())
                self.logging.warning(e)
                self.R_lidar = [0]
                self.Theta_lidar = [0]


            data_lidar = plotly.graph_objs.Scatterpolar(

                r=list(self.R_lidar),
                theta=list(self.Theta_lidar),
                mode='markers',

            )

            data_lidar_LoRa = plotly.graph_objs.Scatterpolar(
                r=list(self.R_lidar_lora),
                theta=list(self.Theta_lidar_lora),
                mode='markers',marker_symbol='diamond',
                marker = dict(
                size=15)
            )

            #return {'data': [data_lidar,data_lidar_LoRa],
            return {'data': [data_lidar_LoRa],
                    'layout': go.Layout(
                        xaxis=dict(range=[min(self.R_lidar_lora), max(self.R_lidar_lora)]),
                        yaxis=dict(range=[min(self.Theta_lidar_lora), max(self.Theta_lidar_lora)]),
                        margin=dict(l=10, r=10, t=10, b=10)
                    )
                    }
        """
        """
        @self.app.callback(Output('tabs-container', 'children'),
                      Input('tabs-elements', 'value'))
        def render_content(tab):
            if tab == 'tab-2-graph':
                return html.Div([content_pkt_stats])
                # return html.Div(
                #     [html.H6("BLE Heart Rate", className="graph__title"),
                #      dcc.Graph(id='HR-graph', animate=False),
                #      ],
                #     className="pretty_container twelve columns",
                # )
            elif tab == 'tab-1-graph':
                return html.Div([content_pkt_stats])
        """

        """
        @self.app.callback(Output('voice_lora_graph', 'figure'),
                      Input('interval-component', 'n_intervals'))
        def update_graph_live(n):
            tnow = datetime.now()
            #get data from DB
            try:

                df_start = pd.DataFrame(ControllerMongoDB().extractEventsDataFrame(T_window=self.T_window))
                #
                df = AdaptiveAlgorithm().scaleRSSI(df_start)


                try:
                    df['rssi_filter'] = df[["rssi"]].apply(savgol_filter, window_length=10, polyorder=1)
                except:
                    df['rssi_filter'] = df["rssi"]

                # FILTER ALIEN or WRONG MESSAGES
                if len(df)!=0:
                    df["MessageType"] = [str(AppMessage(d).getType()).split('.')[1] for d in df["data"]]
                    df = df[df["MessageType"] != "ERROR"]

                if len(df)!=0:
                    #df["MessageType"] = [str(AppMessage(d).getType()).split('.')[1] for d in df["data"]]
                    #df = df[df["MessageType"] != "ERROR"]

                    SF_curr = [int(datr.split("BW")[0].split("SF")[1]) for datr in df["datr"]]
                    N_CR_curr = [int(codr.split("/")[1]) for codr in df["codr"]]
                    df["ToA"] =[
                        LoRaToA().get_toa(n_size=(df["size"][i]), n_sf=SF_curr[i], n_cr=N_CR_curr[i])['t_packet']
                        for i in range(len(df["data"]))
                    ]
                    #self.logging.error((df[["ToA","MessageType"]]))

                    #Adapt RSSI for DEMO

                    t_off1 = [df.timestamp[i] + timedelta(milliseconds=1) for i in range(len(df))]
                    t_interpacket = [df.timestamp[i] for i in range(len(df))]
                    t_ToA = [df.timestamp[i] - timedelta(milliseconds=df["ToA"][i]) for i in range(len(df))]
                    t_off2 = [df.timestamp[i] - timedelta(milliseconds=df["ToA"][i]) - timedelta(milliseconds=1) for i in range(len(df))]
                    t_plot_packets = np.sort(np.concatenate([t_off1, t_interpacket, t_ToA,t_off2]))
                    vals=np.zeros(4*len(t_interpacket))
                    MIN_SENS = -134
                    for i in range(len(t_interpacket)):
                        vals[4 * i] = MIN_SENS
                        vals[4 * i + 1] = df["rssi"].iloc[i]
                        vals[4 * i + 2] = df["rssi"].iloc[i]
                        vals[4 * i + 3] = MIN_SENS
                    #vals=np.ones(len(tt))*(-140)
                    #vals[list(np.array([np.where(tt==t) for t in t_interpacket]).flatten())]=df["rssi"]
                    #vals[list(np.array([np.where(tt==t) for t in t_ToA]).flatten())]=df["rssi"]

                    #Prepare figure
                    fig = make_subplots(
                        rows=3, cols=1,
                        shared_xaxes=True,
                        vertical_spacing=0.09,
                    )

                    # fig.add_trace(go.Scatter(x=df['timestamp'], y=np.ones(len(df)),
                    #                          mode='markers', line=dict(color='blue'),name="Interarrival Packets"
                    #                          ), row=1, col=1,
                    #
                    #               )
                    #
                    # fig.add_trace(go.Scatter(x=t_ToA, y=np.ones(len(t_ToA)),
                    #                          mode='markers', line=dict(color='red'),name="Interarrival Packets ToA"
                    #                          ), row=1, col=1,
                    #
                    #               )
                    #
                    # fig.add_trace(go.Scatter(x=t_off1, y=np.zeros(len(t_off1)),
                    #                          mode='markers', line=dict(color='black'),name="t_off1"
                    #                          ), row=1, col=1,
                    #
                    #               )
                    #
                    # fig.add_trace(go.Scatter(x=t_off2, y=np.zeros(len(t_off2)),
                    #                          mode='markers', line=dict(color='grey'),name="t_off1"
                    #                          ), row=1, col=1,
                    #
                    #               )

                    fig.add_trace(go.Scatter(x=t_plot_packets, y=vals,
                                             mode='lines', line=dict(color='blue'),name="PACKETS"
                                             ), row=1, col=1,

                                  )
                    fig.update_yaxes(row=1, col=1, range=[MIN_SENS-2,-110],title_text='RSSI [dBm]')

                    fig.add_trace(go.Scatter(x=df['timestamp'], y=df['rssi_filter'],
                                             mode='lines+markers', line=dict(color='red'), name="RSSI FILT"
                                             ), row=1, col=1,

                                  )


                    #
                    # fig.add_trace(go.Scatter(x=df['timestamp'], y=df["rssi"],
                    #                          mode='lines+markers', line=dict(color='red'),name="RSSI"
                    #                          ), row=2, col=1,
                    #               )
                    #fig.update_yaxes(range=[-140, -105], row=2,col=1)


                    datr_list = ['SF12BW125','SF11BW125','SF10BW125', 'SF9BW125','SF8BW125','SF7BW125','SF7BW250']
                    #datr_list = ['SF10BW125', 'SF9BW125', 'SF8BW125', 'SF7BW125', 'SF7BW250']
                    #datr_list = ['DR2', 'DR3', 'DR4', 'DR5', 'DR6']
                    plot_dr = [datr_list.index(dd) for dd in df["datr"]]
                    fig.add_trace(go.Scatter(x=df['timestamp'], y=plot_dr,
                                             mode='markers+lines', line=dict(color='red'),name="Data Rate"
                                             ), row=2, col=1
                                  )

                    fig.update_yaxes(row=2,col=1,range=[-1,7], tickvals=[0,1,2,3,4,5,6] , ticktext = datr_list)

                    #fig.update_yaxes(row=2,col=1,range=[-1,5], tickvals=[0,1,2,3,4] , ticktext = datr_list)


                    message_list = ["TEXT","LIDAR","AUDIO","HR"]

                    plot_message_type = [message_list.index(dd) for dd in df["MessageType"]]
                    fig.add_trace(go.Scatter(x=df['timestamp'], y=plot_message_type,
                                             mode='markers', line=dict(color='green'), name="Message Type"
                                             ), row=3, col=1
                                  )
                    fig.update_yaxes(row=3, col=1, range=[-1, len(message_list)], tickvals=np.arange(len(message_list)), ticktext=message_list)
                    # fig.update_yaxes(
                    #     scaleanchor="x",
                    #     scaleratio=1,
                    # )
                    fig.update_xaxes(range=[tnow - timedelta(seconds=self.T_window), tnow])
                    #fig.update_layout(height=700)

                    fig.update_layout(margin = dict(l=10, r=10, t=10, b=10))
                    return fig
            except:
                traceback.print_exc()
                pass


        @self.app.callback(Output('knob-output-1', 'children'), Input('my-knob-1', 'value'))
        def update_output(value):

            #lower, upper = 0, 15
            #value_norm = int((lower + (upper - lower) * value)/100)
            #print('The knob value is {}.'.format(value_norm))
            #self.knob_rssi_value=value_norm
            self.knob_rssi_value = value
            #
            #Quick and dirty: change TX power by sending a control message to the Device
            #

            self.knob_dr_value = value
            AdaptiveAlgorithm().setDevRSSI(self.knob_rssi_value)
            return 'The knob value is {}.'.format(int(value))

        
        @self.app.callback(Output('knob-output-2', 'children'), Input('my-knob-2', 'value'))
        def update_output(value):

            #
            # Quick and dirty: change TX power by sending a control message to the Device
            #
            self.knob_dr_value=value
            AdaptiveAlgorithm().setDR(self.knob_dr_value)
            return 'The knob value is {}.'.format(int(value))
        """