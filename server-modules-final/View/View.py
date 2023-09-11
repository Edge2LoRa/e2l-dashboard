# Import required libraries

import logging,sys
# import time
import traceback
import collections

import datetime
from datetime import datetime, timedelta, date
# from datetime import datetime as dttime

# import dash_daq as daq
from plotly.subplots import make_subplots

# import pandas as pd

import sys
import dash
import dash_bootstrap_components as dbc
# import dash_html_components as html
from dash import html
from dash import dcc
from dash import no_update
import dash_daq as daq

from dash.dependencies import Input, Output, State
# import dash_cytoscape as cyto
import plotly.graph_objects as go
import networkx as nx


import numpy as np
import plotly.graph_objs as go
# from Controller.ControllerDB import ControllerMongoDB

# from Model.AppMessage import AppMessage, MessageType
# from Model.LoRaToA import LoRaToA
# from Model.AdaptiveAlgorithm import AdaptiveAlgorithm
# from scipy.signal import savgol_filter

logLevel=logging.INFO
logging.basicConfig(stream=sys.stdout, level=logLevel)

# import plotly
# import json

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

        # self.lidar_offsets_ctrl=json.loads(json.dumps("[[]]"))
        # self.lidar_lora = json.loads(json.dumps(""))

        self.text_lora = {}
        self.T_window = 60

        # self.app = dash.Dash(__name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}])
        self.app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])
        self.app.logger.setLevel(loggingLevel)

        logDevices = collections.deque(maxlen=20)
        logGateways = collections.deque(maxlen=20)
        logDistributed = collections.deque(maxlen=20)


        self.ed_1_gw_selection = 1
        self.ed_2_gw_selection = 1
        self.ed_3_gw_selection = 1
        self.dropdown_process_function = "mean"
        self.dropdown_process_window = 40

        self.app.title = "EDGE2LORA DEMO (MOBICOM 2023)"

        self.processingFunctions = ["mean", "max", "min", "std"]
        self.processingWindows = [10, 20, 30, 40, 50, 60]

        # self.G = nx.random_geometric_graph(8, 0.125)

        nodes = np.array(['ED_1', 'ED_2', 'E2D_1', 'E2D_2', 'E2D_3', 'E2L_GW_2', 'E2L_GW_1', 'NS', 'DS'])
        pos = np.array([[1, 5], [1, 4], [1, 3], [1, 2], [1, 1],
                        [3, 2], [3, 4],
                        [5,3],
                        [7,3]])
        edges = np.array([['ED_1', 'E2L_GW_1'], ['ED_2', 'E2L_GW_1'],
                          ['E2D_1', 'E2L_GW_1'], ['E2D_2', 'E2L_GW_1'], ['E2D_3', 'E2L_GW_1'],
                          ['ED_1', 'E2L_GW_2'], ['ED_2', 'E2L_GW_2'],
                          ['E2D_1', 'E2L_GW_2'], ['E2D_2', 'E2L_GW_2'], ['E2D_3', 'E2L_GW_2'],
                          ['E2L_GW_1', 'NS'], ['E2L_GW_2', 'NS'],
                          ['NS', 'DS'] ])
        self.G = nx.Graph()
        # print("1: ", self.G.nodes())
        # IG = InteractiveGraph(G) #>>>>> add this line in the next step
        self.G.add_nodes_from(nodes)
        # print("2: ", self.G.nodes())
        self.G.add_edges_from(edges)
        # print("3: ", self.G.nodes())

        nx.set_node_attributes(self.G, dict(zip(self.G.nodes(), pos.astype(float))), 'pos')
        # print("4: ", self.G.nodes())


        # Create app layout
        header = html.Div(
            [
                html.Div(
                    [
                        html.Img(
                            src=self.app.get_asset_url("Uniroma1.png"),
                            id="plotly-image-sapienza",
                            style={
                                "height": "80px",  "width": "auto", "margin-bottom": "1px", 'display': 'inline-block', 'text-align': 'center'
                            },
                        ),
                        html.Img(
                            src=self.app.get_asset_url("logo-unipa.png"),
                            id="plotly-image-unipa",
                            style={
                                "height": "80px", "width": "auto", "margin-bottom": "1px", 'display': 'inline-block', 'text-align': 'center'},
                        ),
                        html.Img(
                            src=self.app.get_asset_url("logo_unidata.png"),
                            id="plotly-image-unidata",
                            style={
                                "height": "80px", "width": "auto", "margin-bottom": "1px", 'display': 'inline-block', 'text-align': 'center'},
                        )
                    ],
                    className="one-third column",
                    style={
                        "height": "80px", "width": "auto", "margin-bottom": "1px", 'display': 'inline-block', 'text-align': 'center'
                    },
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
                    style={
                        "height": "80px", "width": "auto", "margin-bottom": "1px", 'display': 'inline-block', 'text-align': 'center'
                    },
                ),

            ],
            id="header",
            className="row flex-display",
            style={"margin-bottom": "25px"},
        )

        # content_pkt_stats = html.Div([
        #     # LORA EVENTS TIMING VISUALIZER
        #     dcc.Interval(
        #         id='interval-component',
        #         interval=1000000,
        #         n_intervals=0
        #     ),
        #     # dcc.Interval(
        #     #     id='interval-component-HR',
        #     #     interval=30*1000,
        #     #     n_intervals=0
        #     # ),
        #     # dcc.Interval(
        #     #     id='interval-component-Lid',
        #     #     interval = 1000,
        #     #     n_intervals=0
        #     # ),
        #     html.Div([
        #         #FIRST SUB-ROW: POWER INTERFACE, regulate TX POWER GAIN
        #
        #         #SECOND SUB-ROW: show current value of RSSI and DR
        #         # html.Div([
        #         #     html.Div("RSSI",className="pretty_container five columns"),
        #         #     html.Div("DR",className="pretty_container six columns")
        #         # ]),
        #         #THIRD SUB-ROW: show LIDAR data
        #         # LIDAR POLAR PLOT
        #         # SCENARIO CONFIGURATION
        #         html.Div(
        #             [html.H6("SCENARIO CONFIGURATION", className="graph__title"),
        #
        #              html.Label('Select the legacy device number'),
        #              dcc.Slider(0, 5, 1, value=self.slider_legacy_device_num, id='legacy-device-num'),
        #              html.Div(id='slider-output-1'),
        #
        #              html.Label('Select the E2L device number'),
        #              dcc.Slider(0, 5, 1, value=self.slider_E2L_device_num, id='E2L-device-num'),
        #              html.Div(id='slider-output-2'),
        #
        #              html.Button('Update configuration', id='updateScenarioConfigurationButton', style={'text-align': 'center', 'vertical-align': 'middle', }),
        #              html.Div(id='updateScenarioConfigurationDiv'),
        #
        #              # html.Div(id='output-container-button-app12', children='',
        #                       #  style={'width': '20%', 'hight':'40', 'backgroundColor':'#F7FBFE', 'marginLeft': 10, 'marginRight': 10, 'marginTop': 10, 'marginBottom': 10,
        #                       # 'border': 'thin lightgrey dashed', 'padding': '10px 10px 10px 10px', 'display': 'inline-block', 'vertical-align': 'top'}
        #                       # ),
        #
        #              ],
        #             className="pretty_container seven columns",
        #             style={'width': '20%', 'marginLeft': 2, 'marginRight': 2, 'marginTop': 2, 'marginBottom': 2, 'padding': '8px 8px 8px 8px',
        #                    'vertical-align': 'top', 'display': 'inline-block', 'text-align': 'center'}
        #         ),
        #
        #         # html.Div([
        #         #     dcc.Graph(id='devices-space-own-app12'),
        #         # ], id='devices-space-own-app12-div',
        #         #     style={'width': '45%', 'backgroundColor': '#FFFFFF', 'marginLeft': 10, 'marginRight': 10, 'marginTop': 10,
        #         #            'marginBottom': 10, 'border': 'thin lightgrey dashed', 'padding': '6px 0px 0px 8px',
        #         #            'vertical-align': 'top', 'display': 'inline-block', 'text-align': 'center'}),
        #         #
        #         # html.Div([
        #         #     dcc.Graph(id='devices-space-alien-app12'),
        #         # ], id='devices-space-alien-app12-div',
        #         #     style={'width': '45%', 'backgroundColor': '#FFFFFF', 'marginLeft': 10, 'marginRight': 10, 'marginTop': 10,
        #         #            'marginBottom': 10, 'border': 'thin lightgrey dashed', 'padding': '6px 0px 0px 8px',
        #         #            'vertical-align': 'top', 'display': 'inline-block', 'text-align': 'center'}),
        #
        #         html.Div(
        #             [
        #                  html.H6("STREAM PROCESSING CONFIGURATION", className="graph__title"),
        #                  # dcc.Graph(id='HR-graph', animate=False, style={"height":300}, config={'displayModeBar': False}),
        #
        #                 html.Label('Select the aggregation function'),
        #                 dcc.Dropdown(
        #                 id='processing-function-dropdown',
        #                 options=[
        #                     {'label': '{}'.format(self.processingFunctions[index]),
        #                      'value': '{}'.format(self.processingFunctions[index])} for index in range(len(self.processingFunctions) - 1)
        #                 ],
        #                 value=self.processingFunctions[0]
        #                 ),
        #
        #                 html.Label('Select the windows size'),
        #                 dcc.Dropdown(
        #                     id='processing-window-dropdown',
        #                     options=[
        #                         {'label': '{}'.format(self.processingWindows[index]),
        #                          'value': '{}'.format(self.processingWindows[index])} for index in range(len(self.processingWindows) - 1)
        #                     ],
        #                     value=self.processingWindows[0]
        #                 ),
        #
        #                 html.Button('Update configuration', id='updateProcessingConfigurationButton', style={'text-align': 'center', 'vertical-align': 'middle', }),
        #                 html.Div(id='updateProcessingConfigurationDiv'),
        #
        #             ],
        #             className="pretty_container two columns",
        #             style={'width': '16%', 'marginLeft': 2, 'marginRight': 2, 'marginTop': 2, 'marginBottom': 2, 'padding': '8px 8px 8px 8px',
        #                    'vertical-align': 'top', 'display': 'inline-block', 'text-align': 'center'}
        #         ),
        #     ], className="row flex-display",
        #         style={'marginLeft': 2, 'marginRight': 2, 'marginTop': 2, 'marginBottom': 2, 'padding': '8px 8px 8px 8px',
        #                "background-color": "#f8f9fa"}
        #
        #     ),

        #     # LOG MESSAGE CONSOLE
        #     html.Div(
        #         [
        #         html.Div(
        #             [
        #                 html.Div([
        #                     html.H6("Devices key agreement log message", className="log_container_devices"),
        #                     html.Div(id="textarea-log-devices", children=[],
        #                              style={"overflow": "scroll", 'height': 250, "background-color": "#f8f9fa"},
        #                              )]
        #                     , className="pretty_container"),
        #
        #             ],
        #             className="pretty_container two columns",
        #             style={'width': '20%', 'marginLeft': 2, 'marginRight': 2, 'marginTop': 2, 'marginBottom': 2, 'padding': '8px 8px 8px 8px',
        #                    'vertical-align': 'top', 'display': 'inline-block', 'text-align': 'center'}
        #         ),
        #         html.Div(
        #             [
        #                 html.Div([
        #                     html.H6("Gateways key agreement log message", className="log_container_gateways"),
        #                     html.Div(id="textarea-log-gateways", children=[],
        #                              style={"overflow": "scroll", 'height': 250, "background-color": "#f8f9fa"},
        #                              )], className="pretty_container"),
        #             ],
        #             className="pretty_container two columns",
        #             style={'width': '20%', 'marginLeft': 2, 'marginRight': 2, 'marginTop': 2, 'marginBottom': 2, 'padding': '8px 8px 8px 8px',
        #                    'vertical-align': 'top', 'display': 'inline-block', 'text-align': 'center'}
        #         ),
        #         html.Div(
        #             [
        #                 html.Div([
        #                     html.H6("Distributed key agreement log message", className="log_container_gateways"),
        #                     html.Div(id="textarea-log-distributed", children=[],
        #                              style={"overflow": "scroll", 'height': 250, "background-color": "#f8f9fa"},
        #                              )], className="pretty_container"),
        #             ],
        #             className="pretty_container two columns",
        #             style={'width': '20%', 'marginLeft': 2, 'marginRight': 2, 'marginTop': 2, 'marginBottom': 2, 'padding': '8px 8px 8px 8px',
        #                    'vertical-align': 'top', 'display': 'inline-block', 'text-align': 'center'}
        #         ),
        #
        #     ], className="row flex-display",
        #         style={'marginLeft': 2, 'marginRight': 2, 'marginTop': 2, 'marginBottom': 2, 'padding': '8px 8px 8px 8px',
        #                "background-color": "#f8f9fa"}
        #
        #     ), # className="row flex-display"), #className="twelve columns"),
        #
        #     html.Div( [
        #         html.Div([
        #             html.P("Lora network topology:"),
        #             # dcc.Graph(id="lora-network-topology", animate=False, style={"height": 650}, config={'displayModeBar': False}),
        #             dcc.Graph(id="lora-network-topology", animate=True),
        #         ], className="pretty_container five columns",
        #         ),
        #
        #         html.Div( [
        #             html.H6("LoRa Traffic", className="graph_title"),
        #             dcc.Graph(id="lora-traffic-graph", animate=True),
        #         ], className="pretty_container six columns",
        #         # style={'width': '20%', 'marginLeft': 2, 'marginRight': 2, 'marginTop': 2, 'marginBottom': 2, 'padding': '8px 8px 8px 8px',
        #         #        'vertical-align': 'top', 'display': 'inline-block', 'text-align': 'center'}
        #
        #         ),
        #
        #         ],
        #         className="pretty_container twelve columns",
        #     ),
        #
        #     html.Div( [
        #             # dcc.Dropdown(
        #             #     id='dropdown-scenario-spazio-radio',
        #             #     options=[
        #             #         {'label': 'CC00', 'value': 'CC00'},
        #             #         {'label': 'PR00', 'value': 'PR00'},
        #             #         {'label': 'Simul', 'value': 'Simul'},
        #             #     ],
        #             #     value='CC00'
        #             # ),
        #             # dcc.Dropdown(
        #             #     id='dropdown-scenario-period',
        #             #     options=[
        #             #         {'label': 'Period 1 (2019-10-21)', 'value': '2019-10-21'},
        #             #         {'label': 'Period 2 (2019-09-23)', 'value': '2019-09-23'},
        #             #         {'label': 'Period 3 (2019-08-11)', 'value': '2019-08-12'},
        #             #         {'label': 'Period 4 (2019-05-12)', 'value': '2019-05-13'},
        #             #     ],
        #             #     value='2019-10-21'
        #             # ),
        #
        #             dcc.ConfirmDialog(id='confirm-dialog-app8', message='Please wait for complete!', ),
        #             dcc.Store(id="session", storage_type="session"),
        #             dcc.Dropdown(
        #                 id="dropdown-1",
        #                 options=[
        #                     {"label": "a", "value": "a"},
        #                     {"label": "b", "value": "b"},
        #                     {"label": "c", "value": "c"},
        #                 ],
        #                 placeholder="Choose a value",
        #                 value=None,
        #             ),
        #             dcc.Dropdown(
        #                 id="dropdown-2",
        #                 options=[
        #                     {"label": "d", "value": "d"},
        #                     {"label": "e", "value": "e"},
        #                     {"label": "f", "value": "f"},
        #                 ],
        #                 placeholder="Choose a value",
        #                 value=None,
        #             ),
        #             html.Div(id="textarea-1", children=[]),
        #         ], className="pretty_container twelve columns",
        #     ),
        #
        # ], # className="row flex-display",
        # )

        sidebar = html.Div(
            [

                dbc.Row(
                    [
                        html.H6('Settings', style={'margin-top': '12px', 'margin-left': '24px'})
                    ],
                    style={"height": "5vh", 'margin': '8px'},
                    className='bg-primary text-white font-italic'
                ),

                dbc.Row(
                    [
                        html.Div([
                            html.P('SCENARIO CONFIGURATION', style={'margin-top': '18px', 'margin-bottom': '4px'}, className='font-weight-bold'),
                            # html.H6("SCENARIO CONFIGURATION", className="graph__title"),

                            html.Label('Edge2LoRa ED 1 GW selection'),
                            dcc.Slider(1, 2, 1, value=self.ed_1_gw_selection, id='ed-1-gw-selection'),
                            html.Div(id='slider-output-1'),

                            html.Div([
                                html.Div(id='boolean-slider-output-1')
                            ]),

                            html.Label('Edge2LoRa ED 2 GW selection'),
                            dcc.Slider(1, 2, 1, value=self.ed_2_gw_selection, id='ed-2-gw-selection'),
                            html.Div(id='slider-output-2'),
                            html.Div([
                                html.Div(id='boolean-slider-output-2')
                            ]),

                            html.Label('Edge2LoRa ED 3 GW selection'),
                            html.Div([
                                dcc.Slider(1, 2, 1, value=self.ed_3_gw_selection, id='ed-3-gw-selection'),
                                html.Div(id='boolean-slider-output-3')
                            ]),


                            html.Button('Update configuration', id='updateScenarioConfigurationButton',  n_clicks=0,
                                        style={'margin-top': '16px'},
                                        className='bg-dark text-white'),
                            # html.Div(id='updateScenarioConfigurationDiv'),
                            html.Hr(),

                            # html.Div(id='output-container-button-app12', children='',
                            #  style={'width': '20%', 'hight':'40', 'backgroundColor':'#F7FBFE', 'marginLeft': 10, 'marginRight': 10, 'marginTop': 10, 'marginBottom': 10,
                            # 'border': 'thin lightgrey dashed', 'padding': '10px 10px 10px 10px', 'display': 'inline-block', 'vertical-align': 'top'}
                            # ),

                            html.P('STREAM PROCESSING CONFIGURATION', style={'margin-top': '18px', 'margin-bottom': '4px'}, className='font-weight-bold'),
                            # html.H6("STREAM PROCESSING CONFIGURATION", className="graph__title"),

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

                            html.Button('Update configuration', id='updateProcessingConfigurationButton',  n_clicks=0,
                                        style={'margin-top': '16px'},
                                        className='bg-dark text-white'),
                            # html.Button('Update processing configuration', id='updateProcessingConfigurationButton', style={'text-align': 'center', 'vertical-align': 'middle', }),
                            # html.Div(id='updateProcessingConfigurationDiv'),
                            html.Hr()
                        ]
                        )
                    ],
                    style={'height': '50vh', 'margin': '8px'}),
            ]

        )
        content = html.Div(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Row(
                                    [
                                        html.H6('Network topology', style={'margin-top': '12px', 'margin-left': '24px'})
                                    ],
                                    style={'margin': '8px'},
                                    className='bg-primary text-white font-italic'
                                ),
                                dbc.Row(
                                    [
                                        # dcc.Graph(id="lora-network-topology", animate=False, style={"height": 650}, config={'displayModeBar': False}),
                                        dcc.Graph(id="lora-network-topology", animate=True),
                                    ],
                                ),
                            ]),
                        dbc.Col(
                            [
                                dbc.Row(
                                    [
                                        html.H6('Traffic', style={'margin-top': '12px', 'margin-left': '24px'})
                                    ],
                                    style={'margin': '8px'},
                                    className='bg-primary text-white font-italic'
                                ),
                                dbc.Row(
                                    [
                                        dcc.Graph(id="lora-traffic-graph", animate=True),
                                    ],
                                ),
                            ]),
                        # html.Div(id="textarea-1", children=[]),
                        dcc.Store(id="session", storage_type="session"),
                    ],
                    style={"height": "55vh"}
                ),

                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.H6("GW 1 log message", className="log_container_devices"),
                                html.Div(id="textarea-log-devices", children=[],
                                    style={"overflow": "scroll", 'height': 180, "background-color": "#f8f9fa"},
                                    ),
                            ]),
                        dbc.Col(
                            [
                                html.H6("GW 2 log message", className="log_container_gateways"),
                                html.Div(id="textarea-log-gateways", children=[],
                                     style={"overflow": "scroll", 'height': 180, "background-color": "#f8f9fa"},
                                     ),
                            ]),
                        dbc.Col(
                            [
                                html.H6("Edge2LoRa ED log message", className="log_container_gateways"),
                                html.Div(id="textarea-log-distributed", children=[],
                                     style={"overflow": "scroll", 'height': 180, "background-color": "#f8f9fa"},
                                     ),
                            ]),
                    ],
                    style={"height": "25vh"}),
            ]
        )

        self.app.layout = dbc.Container(
            [
                dcc.Interval( id='interval-component', interval=1000000, n_intervals=0 ),
                dbc.Row(
                    [
                        dbc.Col(header, width=0, className='bg-light'),
                    ],
                    style={"height": "10vh", }
                ),

                dbc.Row(
                    [
                        dbc.Col(sidebar, width=0, className='bg-light'),
                        dbc.Col(content, width=10, className='bg-white')
                    ],
                    style={"height": "90vh", 'margin': '18px'}
                ),
            ],
            fluid=True,
            className='bg-white',
            style = {'margin-top': '-10px', 'margin-left':'-5px'}
        )

        # self.app.layout = html.Div(
        #     [
        #         header,
        #         # dcc.Tabs(id="tabs-elements", value='tab-1-graph', children=[
        #         #     dcc.Tab(label='Device Interface', value='tab-2-graph'),
        #         #     dcc.Tab(label='Control Room', value='tab-1-graph'),
        #         #
        #         # ]),
        #         html.Div([content_pkt_stats]),
        #         #html.Div(id='tabs-container'),
        #     ],
        #     id="mainContainer",
        #     #style={"display": "flex", "flex-direction": "column"},
        # )
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
            [Output("session", "data"),
             Output('textarea-log-devices', 'children'),
             Output('textarea-log-gateways', 'children'),
             Output('textarea-log-distributed', 'children')],
            [Input('interval-component', 'n_intervals')],
            State("session", "data"),
            # prevent_initial_call=True,
        )
        def update_text_input(n, data):
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

                    return data, html.Div(html_return_content_ed), html.Div(html_return_content_gw), html.Div(html_return_content_ds)
                else:
                    return data, "test1", "test2", "test3"

            except Exception as e:
                traceback.print_exc()
                pass


            return data, "test1", "test2", "test3"


        @self.app.callback(Output('lora-network-topology', 'figure'),
                           Input('interval-component', 'n_intervals'))
        def update_lora_traffic_graph_live(n):
            try:
                ####NODE####
                node_x = []
                node_y = []
                for node in self.G.nodes():
                    x, y = self.G.nodes[node]['pos']
                    node_x.append(x)
                    node_y.append(y)


                ####EDGE####
                edge_x = []
                edge_y = []
                # print(self.G.edges())
                for edge in self.G.edges():
                    x0, y0 = self.G.nodes[edge[0]]['pos']
                    x1, y1 = self.G.nodes[edge[1]]['pos']
                    edge_x.append(x0)
                    edge_x.append(x1)
                    edge_x.append(None)
                    edge_y.append(y0)
                    edge_y.append(y1)
                    edge_y.append(None)

                # print(edge_x)
                # print(edge_y)


                edge_trace_E2LE = go.Scatter(
                    x=edge_x, y=edge_y,
                    name="Wireless link",
                    # line=dict(width=0.8, color='#888'), # hoverinfo='none', # mode='lines')
                    line=dict(color='firebrick', width=2, dash='dash')) # dash options include 'dash', 'dot', and 'dashdot'

                edge_trace_E2LO = go.Scatter(
                    x=edge_x, y=edge_y,
                    # name="Edge link",
                    # line=dict(width=0.8, color='#888'), # hoverinfo='none', # mode='lines')
                    line=dict(color='firebrick', width=2, dash='dash')) # dash options include 'dash', 'dot', and 'dashdot'

                edge_trace_CLOUD = go.Scatter(
                    x=edge_x, y=edge_y,
                    # name="Cloud",
                    # line=dict(width=0.8, color='#888'), # hoverinfo='none', # mode='lines')
                    line=dict(color='firebrick', width=2, dash='dash')) # dash options include 'dash', 'dot', and 'dashdot'

                node_trace_ED_legacy = go.Scatter(
                    x=node_x[:2], y=node_y[:2],
                    name='Legacy ED',
                    mode='markers',
                    hoverinfo='text',
                    marker=dict(
                        showscale=False,
                        # colorscale options
                        # 'Greys' | 'YlGnBu' | 'Greens' | 'YlOrRd' | 'Bluered' | 'RdBu' |
                        # 'Reds' | 'Blues' | 'Picnic' | 'Rainbow' | 'Portland' | 'Jet' |
                        # 'Hot' | 'Blackbody' | 'Earth' | 'Electric' | 'Viridis' |
                        colorscale='YlGnBu',
                        reversescale=True,
                        color='LightSkyBlue',
                        size=40,
                        colorbar=dict(
                            thickness=15,
                            title='Node Connections',
                            xanchor='left',
                            titleside='right'
                        ),
                        line=dict( color='MediumPurple', width=3, ),
                        symbol="circle",
                        ))

                node_trace_EDL = go.Scatter(
                    x=node_x[2:5], y=node_y[2:5],
                    mode='markers',
                    name='E2L ED',
                    hoverinfo='text',
                    marker=dict(
                        showscale=False,
                        # colorscale options
                        # 'Greys' | 'YlGnBu' | 'Greens' | 'YlOrRd' | 'Bluered' | 'RdBu' |
                        # 'Reds' | 'Blues' | 'Picnic' | 'Rainbow' | 'Portland' | 'Jet' |
                        # 'Hot' | 'Blackbody' | 'Earth' | 'Electric' | 'Viridis' |
                        colorscale='YlGnBu',
                        reversescale=False,
                        color='LightSkyBlue',
                        size=40,
                        colorbar=dict(
                            thickness=15,
                            title='Node Connections',
                            xanchor='left',
                            titleside='right'
                        ),
                        symbol="star",
                        line=dict( color='MediumPurple', width=3, ),
                    ))

                node_trace_GW = go.Scatter(
                    x=node_x[5:7], y=node_y[5:7],
                    mode='markers',
                    name='E2L GW',
                    hoverinfo='text',
                    marker=dict(
                        showscale=False,
                        # colorscale options
                        # 'Greys' | 'YlGnBu' | 'Greens' | 'YlOrRd' | 'Bluered' | 'RdBu' |
                        # 'Reds' | 'Blues' | 'Picnic' | 'Rainbow' | 'Portland' | 'Jet' |
                        # 'Hot' | 'Blackbody' | 'Earth' | 'Electric' | 'Viridis' |
                        colorscale='YlGnBu',
                        reversescale=True,
                        color='LightSkyBlue',
                        size=40,
                        colorbar=dict(
                            thickness=15,
                            title='Node Connections',
                            xanchor='left',
                            titleside='right'
                        ),
                        symbol="star-triangle-up",
                        line=dict(color='MediumPurple', width=3, ),
                    ))

                node_trace_NS = go.Scatter(
                    x=node_x[7:8], y=node_y[7:8],
                    mode='markers',
                    name='NS',
                    hoverinfo='text',
                    marker=dict(
                        showscale=False,
                        # colorscale options
                        # 'Greys' | 'YlGnBu' | 'Greens' | 'YlOrRd' | 'Bluered' | 'RdBu' |
                        # 'Reds' | 'Blues' | 'Picnic' | 'Rainbow' | 'Portland' | 'Jet' |
                        # 'Hot' | 'Blackbody' | 'Earth' | 'Electric' | 'Viridis' |
                        colorscale='YlGnBu',
                        reversescale=True,
                        color='LightSkyBlue',
                        size=40,
                        colorbar=dict(
                            thickness=15,
                            title='Node Connections',
                            xanchor='left',
                            titleside='right'
                        ),
                        symbol="square",
                        line=dict(color='MediumPurple', width=3, ),
                    ))

                node_trace_DS = go.Scatter(
                    x=node_x[8:9], y=node_y[8:9],
                    mode='markers',
                    name='DS',
                    hoverinfo='text',
                    marker=dict(
                        showscale=False,
                        # colorscale options
                        # 'Greys' | 'YlGnBu' | 'Greens' | 'YlOrRd' | 'Bluered' | 'RdBu' |
                        # 'Reds' | 'Blues' | 'Picnic' | 'Rainbow' | 'Portland' | 'Jet' |
                        # 'Hot' | 'Blackbody' | 'Earth' | 'Electric' | 'Viridis' |
                        colorscale='Viridis',
                        reversescale=False,
                        color='LightSkyBlue',
                        size=40,
                        colorbar=dict(
                            thickness=15,
                            title='Node Connections',
                            xanchor='left',
                            titleside='right'
                        ),
                        symbol="diamond",
                        line=dict(color='MediumPurple', width=3, ),
                    ))

                node_adjacencies = []
                node_text = []
                for node, adjacencies in enumerate(self.G.adjacency()):
                    # node_adjacencies.append(len(adjacencies[1]))
                    node_text.append('# of connections: ' + str(len(adjacencies[1])))

                # node_trace_EDL.marker.color = node_adjacencies
                node_trace_EDL.text = node_text

                fig = go.Figure(data=[edge_trace_E2LE, edge_trace_E2LO, edge_trace_CLOUD, node_trace_ED_legacy, node_trace_EDL, node_trace_GW, node_trace_NS, node_trace_DS],
                                layout=go.Layout(
                                    showlegend=True,
                                    hovermode='closest',
                                    margin=dict(b=20, l=5, r=5, t=40),
                                    xaxis=dict(showgrid=True, zeroline=False, showticklabels=False),
                                    yaxis=dict(showgrid=True, zeroline=False, showticklabels=False))
                                )

                fig.update_layout(
                    legend=dict( x=0.2, y=0.99, traceorder="normal", font=dict( family="sans-serif", size=12, color="blue" ), orientation='h',)
                    # legend=dict(yanchor="top", y=0.01, xanchor="left", x=0.01 )
                )

                return fig

            except Exception as e:
                traceback.print_exc()
            pass



        @self.app.callback(Output('lora-traffic-graph', 'figure'),
                           Input('interval-component', 'n_intervals'))
        def update_lora_traffic_graph_live(n):
            try:
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

                # self.controllerGRPC.gw_1_received_frame_num.append(request.gw_1_received_frame_num)
                # self.controllerGRPC.gw_1_transmitted_frame_num.append(request.gw_1_transmitted_frame_num)
                # self.controllerGRPC.gw_2_received_frame_num.append(request.gw_2_received_frame_num)
                # self.controllerGRPC.gw_2_transmitted_frame_num.append(request.gw_2_transmitted_frame_num)

                gw_1_received_frame_num = list(controllerGRPC.gw_1_received_frame_num)
                gw_1_transmitted_frame_num = list(controllerGRPC.gw_1_transmitted_frame_num)
                gw_2_received_frame_num = list(controllerGRPC.gw_2_received_frame_num)
                gw_2_transmitted_frame_num = list(controllerGRPC.gw_2_transmitted_frame_num)

                timetsamp_list = list(range(len(gw_1_received_frame_num)))

                fig.add_trace(go.Scatter(x=timetsamp_list, y=gw_1_received_frame_num,
                                         mode='lines+markers', line=dict(color=ble_plot_colors[0]), name="RX_GW1"
                                         ), row=1, col=1,
                              )
                fig.add_trace(go.Scatter(x=timetsamp_list, y=gw_1_transmitted_frame_num,
                                         mode='lines+markers', line=dict(color=ble_plot_colors[1]), name="TX_GW1"
                                         ), row=1, col=1,
                              )
                fig.add_trace(go.Scatter(x=timetsamp_list, y=gw_2_received_frame_num,
                                         mode='lines+markers', line=dict(color=ble_plot_colors[2]), name="RX_GW2"
                                         ), row=1, col=1,
                              )
                fig.add_trace(go.Scatter(x=timetsamp_list, y=gw_2_transmitted_frame_num,
                                         mode='lines+markers', line=dict(color=ble_plot_colors[3]), name="TX_GW2"
                                         ), row=1, col=1,
                              )

                # self.controllerGRPC.ns_received_frame_frame_num.append(request.ns_received_frame_frame_num)
                # self.controllerGRPC.ns_transmitted_frame_frame_num.append(request.ns_transmitted_frame_frame_num)
                # self.controllerGRPC.module_received_frame_frame_num.append(request.module_received_frame_frame_num)
                # self.controllerGRPC.aggregation_function_result.append(request.aggregation_function_result)

                ns_received_frame_frame_num = list(controllerGRPC.ns_received_frame_frame_num)
                ns_transmitted_frame_frame_num = list(controllerGRPC.ns_transmitted_frame_frame_num)
                module_received_frame_frame_num = list(controllerGRPC.module_received_frame_frame_num)
                fig.add_trace(go.Scatter(x=timetsamp_list, y=ns_received_frame_frame_num,
                                         mode='lines+markers', line=dict(color=ble_plot_colors[0]), name="RX_NS"
                                         ), row=2, col=1,
                              )
                fig.add_trace(go.Scatter(x=timetsamp_list, y=ns_transmitted_frame_frame_num,
                                         mode='lines+markers', line=dict(color=ble_plot_colors[1]), name="TX_NS"
                                         ), row=2, col=1,
                              )
                fig.add_trace(go.Scatter(x=timetsamp_list, y=module_received_frame_frame_num,
                                         mode='lines+markers', line=dict(color=ble_plot_colors[2]), name="RX_DM"
                                         ), row=2, col=1,
                              )

                fig.update_yaxes(row=1, col=1, title_text='GW 1/2 Statistics')
                fig.update_yaxes(row=2, col=1, title_text='NS/DM Statistics')
                fig.update_layout( margin=dict(l=10, r=10, t=10, b=10), )

                fig.update_layout(legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01 ))

                return fig

            except Exception as e:
                traceback.print_exc()
                pass

        @self.app.callback(
            Output('boolean-slider-output-1', 'children'),
            Input('ED1-boolean-switch', 'on')
        )
        def update_output(on):
            return f'The switch is {on}.'

        @self.app.callback(
            Output('boolean-slider-output-2', 'children'),
            Input('ED2-boolean-switch', 'on')
        )
        def update_output(on):
            return f'The switch is {on}.'

        @self.app.callback(
            Output('boolean-slider-output-3', 'children'),
            Input('ED3-boolean-switch', 'on')
        )
        def update_output(on):
            return f'The switch is {on}.'

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

        """
            cyto.Cytoscape(
                id='cytoscape',
                elements=[
                    {'data': {'id': 'ca', 'label': 'Canada'}},
                    {'data': {'id': 'on', 'label': 'Ontario'}},
                    {'data': {'id': 'qc', 'label': 'Quebec'}},
                    {'data': {'source': 'ca', 'target': 'on'}},
                    {'data': {'source': 'ca', 'target': 'qc'}}
                ],
                layout={'name': 'breadthfirst'},
                style={'width': '400px', 'height': '500px'}
            )
        """