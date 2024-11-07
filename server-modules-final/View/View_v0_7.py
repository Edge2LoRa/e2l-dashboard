# Import required libraries

import logging,sys
# import time
import traceback
import collections
import folium

import datetime
import random

from datetime import datetime, timedelta, date
# from datetime import datetime as dttime
import dash_leaflet as dl
# import dash_daq as daq
from plotly.subplots import make_subplots
import plotly.express as px
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
        self.app._favicon = (self.app.get_asset_url("favicon.ico"))

        self.logDevices = collections.deque(maxlen=20)
        self.logGateways = collections.deque(maxlen=20)
        self.logDistributed = collections.deque(maxlen=20)

        self.ed_1_gw_selection = 1
        self.ed_2_gw_selection = 1
        self.ed_3_gw_selection = 1
        self.dropdown_process_function = "mean"
        self.dropdown_process_window = 2

        self.app.title = "EDGE2LORA DEMO (MOBICOM 2023)"

        self.processingFunctions = ["mean", "max", "min", "std"]
        self.processingWindows = [1, 2, 4, 8, 10, 20]

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
                          ['NS', 'DS'],
                          ['E2L_GW_1', 'DS'], ['E2L_GW_2', 'DS']
                          ])
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
                                html.H5("Stefano Milani, Domenico Garlisi, Matteo Di Fraia, Patrizio Pisani, Ioannis Chatzigiannakis", style={"margin-top": "0px"}
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
                html.Div(
                    [
                        html.Img(
                            src=self.app.get_asset_url("edge2lora-icon-trasparent.png"),
                            id="plotly-image-edge2lora",
                            style={
                                "height": "90px", "width": "auto", "margin-bottom": "1px", 'display': 'inline-block', 'text-align': 'center'
                            },
                        ),
                        html.Img(
                            src=self.app.get_asset_url("qr-code-edge2lora.png"),
                            id="plotly-image-qrcode",
                            style={
                                "height": "90px", "width": "auto", "margin-bottom": "1px", 'display': 'inline-block', 'text-align': 'center'},
                        ),
                    ],
                    className="one-third column",
                    style={
                        "height": "80px", "width": "auto", "margin-bottom": "1px", 'display': 'inline-block', 'text-align': 'center'
                    },
                ),

            ],
            id="header",
            className="row flex-display",
            style={"margin-bottom": "25px"},
        )

        sidebar = html.Div(
            [
                dbc.Row( [ ],
                    style={"height": "1vh", 'margin-left': '-8px'},
                    className='bg-white'
                ),

                dbc.Row(
                    [
                        html.H6('Settings', style={'margin-top': '12px', 'margin-left': '12px'})
                    ],
                    style={"height": "5vh",  'margin-left': '-8px'},
                    className='bg-primary text-white font-italic'
                ),

                dbc.Row(
                    [
                        html.Div([
                            html.P('SCENARIO CONFIGURATION', style={'margin-top': '18px', 'margin-bottom': '4px'}, className='font-weight-bold'),
                            # html.H6("SCENARIO CONFIGURATION", className="graph__title"),

                            html.Div([
                                html.Label('E2ED 1 GW selection'),
                                dcc.Slider(1, 2, 1, value=self.ed_1_gw_selection, id='ed-1-gw-selection'),
                            ]),

                            html.Div([
                                html.Label('E2ED 2 GW selection'),
                                dcc.Slider(1, 2, 1, value=self.ed_2_gw_selection, id='ed-2-gw-selection'),
                            ]),

                            html.Div([
                                html.Label('E2ED 3 GW selection'),
                                dcc.Slider(1, 2, 1, value=self.ed_3_gw_selection, id='ed-3-gw-selection'),
                            ]),


                            html.Button('Update configuration', id='updateScenarioConfigurationButton',  n_clicks=0,
                                        style={'margin-top': '16px'},
                                        className='bg-dark text-white'),
                            html.Div(id='updateScenarioConfigurationDiv'),
                            html.Hr(),

                            # html.Div(id='output-container-button-app12', children='',
                            #  style={'width': '20%', 'hight':'40', 'backgroundColor':'#F7FBFE', 'marginLeft': 10, 'marginRight': 10, 'marginTop': 10, 'marginBottom': 10,
                            # 'border': 'thin lightgrey dashed', 'padding': '10px 10px 10px 10px', 'display': 'inline-block', 'vertical-align': 'top'}
                            # ),

                            html.P('STREAM PROCESSING CONFIGURATION', style={'margin-top': '18px', 'margin-bottom': '4px'}, className='font-weight-bold'),

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
                                value=self.processingWindows[1]
                            ),

                            html.Button('Update configuration', id='updateProcessingConfigurationButton',  n_clicks=0,
                                        style={'margin-top': '16px'},
                                        className='bg-dark text-white'),
                            # html.Button('Update processing configuration', id='updateProcessingConfigurationButton', style={'text-align': 'center', 'vertical-align': 'middle', }),
                            html.Div(id='updateProcessingConfigurationDiv'),
                            html.Hr(),

                            html.Label('AGGREGATION RESULT'),
                            dcc.Markdown(children="0", id='aggregation_result_id', style={'margin-top': '6px', 'text-align': 'center', 'vertical-align': 'middle'},
                                         className='bg-white'),

                            html.Div(id='boolean-slider-output-1', style={ 'text-align': 'center', 'vertical-align': 'middle'}, className='bg-light text-light font-italic'),
                            html.Div(id='boolean-slider-output-2', style={ 'text-align': 'center', 'vertical-align': 'middle'}, className='bg-light text-light font-italic'),
                            html.Div(id='boolean-slider-output-3', style={ 'text-align': 'center', 'vertical-align': 'middle'}, className='bg-light text-light font-italic'),

                        ]
                        )
                    ],
                    style = {'height': '40vh', 'margin': '0px'}),
            ],
            style = {'margin': '0px'},
        )
        content = html.Div(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                # dbc.Row([],
                                #         style={"height": "1vh", 'margin-left': '0px'},
                                #         className='bg-white'
                                #         ),
                                dbc.Row(
                                    [
                                        html.H6('Network topology', style={'margin-top': '12px', 'margin-left': '12px'})
                                    ],
                                    style={"height": "5vh", 'margin': '8px', 'margin-top': '10px'},
                                    className='bg-primary text-white font-italic'
                                ),
                                dbc.Row(
                                    [
                                        # dcc.Graph(id="lora-network-topology", animate=False, style={"height": 650}, config={'displayModeBar': False}),
                                        # dcc.Graph(id="lora-network-topology", animate=False),
                                        #html.Iframe(id='lora-network-topology', srcDoc=open('rome.html', 'r').read(), width='100%', height='400px'),
                                        dl.Map([dl.TileLayer(),dl.LayerGroup(id='nodes-marker-layer'),dl.LayerGroup(id='gateway-marker-layer')], center=[41.90,12.49], zoom=10, style={'height': '45vh', 'margin-left':'20px', 'margin-right':'20px','width':'97%'}),
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
                                # dbc.Row([],
                                #         style={"height": "1vh", 'margin-left': '0px'},
                                #         className='bg-white'
                                #         ),
                                dbc.Row(
                                    [
                                        html.H6('Gateways transmission and reception of frames', style={'margin-top': '12px', 'margin-left': '12px'})
                                    ],
                                    style={"height": "5vh",  'margin': '8px', 'margin-top': '10px'},
                                    className='bg-primary text-white font-italic'
                                ),
                                dbc.Row(
                                    [
                                        dcc.Graph(id="gateways-statistics", animate=False,style={'height': '20vh'}),

                                        #dcc.Graph(id="lora-traffic-graph", animate=False)
                                    ],
                                    
                                ),
                            ]),
                    ],
                    style={"height": "25vh"}),
        
                

                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Row(
                                    [
                                        html.H6('Gateways Load informations', style={'margin-top': '12px', 'margin-left': '12px'})
                                    ],
                                    style={"height": "5vh",  'margin': '8px', 'margin-top': '10px'},
                                    className='bg-primary text-white font-italic'
                                ),
                                dbc.Row(
                                    [
                                        dcc.Graph(id="gateways-loads", animate=False,style={'height': '20vh'}),

                                    ],
                                    
                                ),
                            ]),
                    ],
                    style={"height": "25vh"}),
            ]
        )

        # self.app.layout = dbc.Container(
        #     [
        #         dcc.Interval( id='interval-component', interval=3000, n_intervals=0 ),
        #         dbc.Row(
        #             [
        #                 dbc.Col(header, width=0, className='bg-light'),
        #             ],
        #             style={"height": "10vh", }
        #         ),
        #
        #         dbc.Row(
        #             [
        #                 dbc.Col(sidebar, width=0, className='bg-light'),
        #                 dbc.Col(content, width=10, className='bg-white')
        #             ],
        #             style={"height": "90vh", 'margin': '18px'}
        #         ),
        #     ],
        #     fluid=True,
        #     className='bg-white',
        #     style = {'margin-top': '-10px', 'margin-left':'-5px'}
        # )

        self.app.layout = html.Div(
            [
                dcc.Interval( id='interval-component', interval=1000, n_intervals=0 ),
                dbc.Row(
                    [
                        dbc.Col(header, width=0, className='bg-light'),
                    ],
                    style={"height": "10vh", }
                ),

                dbc.Row(
                    [
                        dbc.Col(sidebar, width=0, className='bg-light', style={'margin': '0px'} ),
                        dbc.Col(content, width=10, className='bg-white')
                    ],
                    style={"height": "90vh", 'margin': '18px'}
                ),
            ],
            id="mainContainer",
            style={"display": "flex", "flex-direction": "column", 'background-color': '#FFFFFF'},
        )

        # self.app.layout = html.Div([],
        #                       style={'background-color': '#000000',
        #                              'background-size': '100%',
        #                              'position': 'fixed',
        #                              'width': '100%',
        #                              'height': '100%'
        #                              })

        ########################
        #CALLBACKS
        ########################

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


        @self.app.callback(Output('lora-network-topology', 'figure'),
                           Input('interval-component', 'n_intervals'))
        def update_lora_topology_graph_live(n):
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

                edge_trace_E2LE = go.Scatter(
                    x=edge_x[:12], y=edge_y[:12],
                    name="Wireless link",
                    # line=dict(width=0.8, color='#888'), # hoverinfo='none', # mode='lines')
                    line=dict(color='darkgrey', width=2, dash='dash')) # dash options include 'dash', 'dot', and 'dashdot'

                # print("view")
                # print(controllerGRPC.ed_1_gw_selection_confirmed)

                if controllerGRPC.ed_1_gw_selection_confirmed==2:
                    colorEdgeEd_1_gw_1 = 'darkblue'
                    colorEdgeEd_1_gw_2 = 'darkgrey'
                    width_gw1 = 3
                    width_gw2 = 0
                elif controllerGRPC.ed_1_gw_selection_confirmed==1:
                    colorEdgeEd_1_gw_1 = 'darkgrey'
                    colorEdgeEd_1_gw_2 = 'darkblue'
                    width_gw1 = 0
                    width_gw2 = 3
                else:
                    colorEdgeEd_1_gw_1 = 'darkgrey'
                    colorEdgeEd_1_gw_2 = 'darkgrey'
                    width_gw1 = 0
                    width_gw2 = 0
                edge_trace_E2E1_GW1 = go.Scatter(
                    x=edge_x[12:15], y=edge_y[12:15],
                    # name="Wireless link",
                    # line=dict(width=0.8, color='#888'), # hoverinfo='none', # mode='lines')
                    line=dict(color=colorEdgeEd_1_gw_1, width=2, dash='dash')) # dash options include 'dash', 'dot', and 'dashdot'
                edge_trace_E2E1_GW2 = go.Scatter(
                    x=edge_x[15:18], y=edge_y[15:18],
                    # name="Wireless link",
                    # line=dict(width=0.8, color='#888'), # hoverinfo='none', # mode='lines')
                    line=dict(color=colorEdgeEd_1_gw_2, width=2, dash='dash')) # dash options include 'dash', 'dot', and 'dashdot'
                edge_trace_GW1_EDGE = go.Scatter(
                    x=edge_x[39:42], y=edge_y[39:42],
                    # name="Cloud",
                    # line=dict(width=0.8, color='#888'), # hoverinfo='none', # mode='lines')
                    line=dict(color=colorEdgeEd_1_gw_1, width=width_gw1)) # dash options include 'dash', 'dot', and 'dashdot'
                edge_trace_GW2_EDGE = go.Scatter(
                    x=edge_x[33:36], y=edge_y[33:36],
                    # name="Cloud",
                    # line=dict(width=0.8, color='#888'), # hoverinfo='none', # mode='lines')
                    line=dict(color=colorEdgeEd_1_gw_2, width=width_gw2))  # dash options include 'dash', 'dot', and 'dashdot'

                # if controllerGRPC.ed_2_gw_selection_confirmed==1:
                #     colorEdgeEd_2_gw_1 = 'darkcyan'
                #     colorEdgeEd_2_gw_2 = 'darkgrey'
                # elif controllerGRPC.ed_2_gw_selection_confirmed==2:
                #     colorEdgeEd_2_gw_1 = 'darkgrey'
                #     colorEdgeEd_2_gw_2 = 'darkcyan'
                # else:
                if True:
                    colorEdgeEd_2_gw_1 = 'darkgrey'
                    colorEdgeEd_2_gw_2 = 'darkgrey'
                edge_trace_E2E2_GW1 = go.Scatter(
                    x=edge_x[18:21], y=edge_y[18:21],
                    # name="Wireless link",
                    # line=dict(width=0.8, color='#888'), # hoverinfo='none', # mode='lines')
                    line=dict(color=colorEdgeEd_2_gw_1, width=2, dash='dash')) # dash options include 'dash', 'dot', and 'dashdot'
                edge_trace_E2E2_GW2 = go.Scatter(
                    x=edge_x[21:24], y=edge_y[21:24],
                    # name="Wireless link",
                    # line=dict(width=0.8, color='#888'), # hoverinfo='none', # mode='lines')
                    line=dict(color=colorEdgeEd_2_gw_2, width=2, dash='dash')) # dash options include 'dash', 'dot', and 'dashdot'



                # if controllerGRPC.ed_3_gw_selection_confirmed==1:
                #     colorEdgeEd_3_gw_1 = 'darkgreen'
                #     colorEdgeEd_3_gw_2 = 'darkgrey'
                # elif controllerGRPC.ed_3_gw_selection_confirmed==2:
                #     colorEdgeEd_3_gw_1 = 'darkgrey'
                #     colorEdgeEd_3_gw_2 = 'darkgreen'
                # else:
                if True:
                    colorEdgeEd_3_gw_1 = 'darkgrey'
                    colorEdgeEd_3_gw_2 = 'darkgrey'
                edge_trace_E2E3_GW1 = go.Scatter(
                    x=edge_x[24:27], y=edge_y[24:27],
                    # name="Wireless link",
                    # line=dict(width=0.8, color='#888'), # hoverinfo='none', # mode='lines')
                    line=dict(color=colorEdgeEd_3_gw_1, width=2, dash='dash')) # dash options include 'dash', 'dot', and 'dashdot'
                edge_trace_E2E3_GW2 = go.Scatter(
                    x=edge_x[27:30], y=edge_y[27:30],
                    # name="Wireless link",
                    # line=dict(width=0.8, color='#888'), # hoverinfo='none', # mode='lines')
                    line=dict(color=colorEdgeEd_3_gw_2, width=2, dash='dash')) # dash options include 'dash', 'dot', and 'dashdot'

                # edge_trace_E2LO = go.Scatter(
                #     x=edge_x, y=edge_y,
                #     # name="Edge link",
                #     # line=dict(width=0.8, color='#888'), # hoverinfo='none', # mode='lines')
                #     line=dict(color='firebrick', width=2, dash='dash')) # dash options include 'dash', 'dot', and 'dashdot'
                #

                edge_trace_GW2_NS = go.Scatter(
                    x=edge_x[30:33], y=edge_y[30:33],
                    # name="Cloud",
                    # line=dict(width=0.8, color='#888'), # hoverinfo='none', # mode='lines')
                    line=dict(color='darkgray', width=2))  # dash options include 'dash', 'dot', and 'dashdot'

                edge_trace_GW1_NS = go.Scatter(
                    x=edge_x[36:39], y=edge_y[36:39],
                    # name="Cloud",
                    # line=dict(width=0.8, color='#888'), # hoverinfo='none', # mode='lines')
                    line=dict(color='darkgrey', width=2)) # dash options include 'dash', 'dot', and 'dashdot'

                edge_trace_NS_DS = go.Scatter(
                    x=edge_x[42:45], y=edge_y[42:45],
                    # name="Cloud",
                    # line=dict(width=0.8, color='#888'), # hoverinfo='none', # mode='lines')
                    line=dict(color='darkgrey', width=2)) # dash options include 'dash', 'dot', and 'dashdot'

                node_trace_ED_legacy = go.Scatter(
                    x=node_x[:2], y=node_y[:2],
                    name='Legacy ED',
                    mode='markers',
                    # hoverinfo='text',
                    marker=dict(
                        showscale=False,
                        # colorscale options
                        # 'Greys' | 'YlGnBu' | 'Greens' | 'YlOrRd' | 'Bluered' | 'RdBu' |
                        # 'Reds' | 'Blues' | 'Picnic' | 'Rainbow' | 'Portland' | 'Jet' |
                        # 'Hot' | 'Blackbody' | 'Earth' | 'Electric' | 'Viridis' |
                        colorscale='YlGnBu',
                        reversescale=True,
                        color='#FFFFD9',
                        size=40,
                        colorbar=dict(
                            thickness=15,
                            title='Node Connections',
                            xanchor='left',
                            titleside='right'
                        ),
                        line=dict( color='#434746', width=2, ),
                        symbol="circle",
                        ))

                node_trace_EDL = go.Scatter(
                    x=node_x[2:5], y=node_y[2:5],
                    mode='markers',
                    name='E2L ED',
                    # hoverinfo='text',
                    marker=dict(
                        showscale=False,
                        # colorscale options
                        # 'Greys' | 'YlGnBu' | 'Greens' | 'YlOrRd' | 'Bluered' | 'RdBu' |
                        # 'Reds' | 'Blues' | 'Picnic' | 'Rainbow' | 'Portland' | 'Jet' |
                        # 'Hot' | 'Blackbody' | 'Earth' | 'Electric' | 'Viridis' |
                        colorscale='YlGnBu',
                        reversescale=False,
                        color='#96D7BA',
                        size=40,
                        colorbar=dict(
                            thickness=15,
                            title='Node Connections',
                            xanchor='left',
                            titleside='right'
                        ),
                        symbol="star",
                        line=dict( color='#434746', width=2, ),
                    ))

                node_trace_GW_1 = go.Scatter(
                    x=node_x[5:6], y=node_y[5:6],
                    mode='markers+text',
                    name='E2L GW 1',
                    hoverinfo='text',
                    text="{},{}".format(controllerGRPC.gw_1_received_frame_num_sum, controllerGRPC.gw_1_transmitted_frame_num_sum),
                    textposition="top right",
                    textfont=dict(size=30, color='red'),
                    marker=dict(
                        showscale=False,
                        # colorscale options
                        # 'Greys' | 'YlGnBu' | 'Greens' | 'YlOrRd' | 'Bluered' | 'RdBu' |
                        # 'Reds' | 'Blues' | 'Picnic' | 'Rainbow' | 'Portland' | 'Jet' |
                        # 'Hot' | 'Blackbody' | 'Earth' | 'Electric' | 'Viridis' |
                        colorscale='YlGnBu',
                        reversescale=True,
                        color='red',
                        size=40,
                        colorbar=dict(
                            thickness=15,
                            title='Node Connections',
                            xanchor='left',
                            titleside='right'
                        ),
                        symbol="triangle-up",
                        line=dict(color="#434746", width=0, ),
                    ))


                node_trace_GW_2 = go.Scatter(
                    x=node_x[6:7], y=node_y[6:7],
                    mode='markers+text',
                    name='E2L GW 2',
                    hoverinfo='text',
                    text="{},{}".format(controllerGRPC.gw_2_received_frame_num_sum, controllerGRPC.gw_2_transmitted_frame_num_sum),
                    textposition="top right",
                    textfont=dict(size=30, color='blue'),
                    marker=dict(
                        showscale=False,
                        # colorscale options
                        # 'Greys' | 'YlGnBu' | 'Greens' | 'YlOrRd' | 'Bluered' | 'RdBu' |
                        # 'Reds' | 'Blues' | 'Picnic' | 'Rainbow' | 'Portland' | 'Jet' |
                        # 'Hot' | 'Blackbody' | 'Earth' | 'Electric' | 'Viridis' |
                        colorscale='YlGnBu',
                        reversescale=True,
                        color='blue',
                        size=40,
                        colorbar=dict(
                            thickness=15,
                            title='Node Connections',
                            xanchor='left',
                            titleside='right'
                        ),
                        symbol="triangle-up",
                        # line=dict(color='MediumPurple', width=3, ),
                    ))



                node_trace_NS = go.Scatter(
                    x=node_x[7:8], y=node_y[7:8],
                    mode='markers+text',
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
                        color='#071D57',
                        size=40,
                        # colorbar=dict(
                        #     thickness=15,
                        #     title='Node Connections',
                        #     xanchor='left',
                        #     titleside='right'
                        # ),
                        symbol="square",
                        line=dict(color='#434746', width=0, ),
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
                        color='#207FB7',
                        size=40,
                        colorbar=dict(
                            thickness=15,
                            title='Node Connections',
                            xanchor='left',
                            titleside='right'
                        ),
                        symbol="diamond",
                        line=dict(color='#434746', width=0, ),
                    ))

                # node_adjacencies = []
                # node_text = []
                # for node, adjacencies in enumerate(self.G.adjacency()):
                #     # node_adjacencies.append(len(adjacencies[1]))
                #     node_text.append('# of connections: ' + str(len(adjacencies[1])))
                #
                # # node_trace_EDL.marker.color = node_adjacencies
                # node_trace_EDL.text = node_text

                fig = go.Figure(data=[edge_trace_E2LE,
                                      edge_trace_E2E1_GW1, edge_trace_E2E1_GW2,
                                      edge_trace_E2E2_GW1, edge_trace_E2E2_GW2,
                                      edge_trace_E2E3_GW1, edge_trace_E2E3_GW2,
                                      edge_trace_GW1_EDGE,
                                      edge_trace_GW2_EDGE,
                                      edge_trace_GW1_NS,
                                      edge_trace_GW2_NS,
                                      edge_trace_NS_DS,
                                      node_trace_ED_legacy, node_trace_EDL,
                                      node_trace_GW_1, node_trace_GW_2,
                                      node_trace_NS, node_trace_DS,
                                      ],
                                layout=go.Layout(
                                    showlegend=True,
                                    hovermode='closest',
                                    margin=dict(b=20, l=5, r=5, t=40),
                                    xaxis=dict(showgrid=True, zeroline=False, showticklabels=False),
                                    yaxis=dict(showgrid=True, zeroline=False, showticklabels=False))
                                )

                fig.update_layout(
                    legend=dict( x=0.4, y=0.99, traceorder="normal", font=dict( family="sans-serif", size=12, color="blue" ), orientation='h',)
                    # legend=dict(yanchor="top", y=0.01, xanchor="left", x=0.01 )
                )

                fig['data'][0]['showlegend'] = False
                fig['data'][1]['showlegend'] = False
                fig['data'][2]['showlegend'] = False
                fig['data'][3]['showlegend'] = False
                fig['data'][4]['showlegend'] = False
                fig['data'][5]['showlegend'] = False
                fig['data'][6]['showlegend'] = False
                fig['data'][7]['showlegend'] = False
                fig['data'][8]['showlegend'] = False
                fig['data'][9]['showlegend'] = False
                fig['data'][10]['showlegend'] = False
                fig['data'][11]['showlegend'] = False

                fig.update_layout( margin=dict(l=10, r=10, t=10, b=10), )


                return fig

            except Exception as e:
                traceback.print_exc()
            pass



        @self.app.callback([Output('nodes-marker-layer','children'), Output('gateway-marker-layer','children')],                           
                           [Input('interval-component', 'n_intervals')])
        
        def update_markers_map(n):
            
            nodes_markers = [dl.Marker(position=[device.lat,device.lon]) for device in controllerGRPC.devices_list]

            return nodes_markers,[]
        

        @self.app.callback(Output('gateways-loads', 'figure'),
                           Input('interval-component', 'n_intervals'))
        
        def update_gateways_loads(n):
            memory_trace = go.Bar(
                x = controllerGRPC.gateways_stats_dataframe['Gateway ID'],
                y = controllerGRPC.gateways_stats_dataframe['mem'],
                name = 'Memory',
                marker=dict(color='purple')
            )

            cpu_trace = go.Bar(
                x=controllerGRPC.gateways_stats_dataframe['Gateway ID'],
                y=controllerGRPC.gateways_stats_dataframe['cpu'],
                name='CPU',
                marker=dict(color='orange')
            )

            
            fig = go.Figure(data =[memory_trace, cpu_trace])
            

            fig.update_layout(margin=dict(t=10, b=10), showlegend=True)
            fig.update_xaxes(showticklabels=True)

            return fig



        @self.app.callback(Output('gateways-statistics', 'figure'),
                           Input('interval-component', 'n_intervals'))
        
        def update_gateways_statistics(n):
            # i have to make a plotly figure composed by a bar plot with a varying number of bars
            # the number of bars is equal to the number of gateways
            # each bar has a height equal to the number of received frames

            # fig = go.bar(controllerGRPC.gateways_stats_dataframe, x='Gateway ID', y='mem', title='Gateways statistics')
            # fig.update_layout( margin=dict(l=10, r=10, t=10, b=10), )

            bar_trace_rx = go.Bar(
                x=controllerGRPC.gateways_stats_dataframe['Gateway ID'],
                y=controllerGRPC.gateways_stats_dataframe['RX_frame'],
                name = 'RX_frame'
            )

            bar_trace_tx = go.Bar(
                x=controllerGRPC.gateways_stats_dataframe['Gateway ID'],
                y=controllerGRPC.gateways_stats_dataframe['TX_frame'],
                name = 'TX_frame'
            )

            fig = go.Figure(data =[bar_trace_rx, bar_trace_tx])



            fig.update_layout(margin=dict(t=10, b=10), showlegend=True)
            fig.update_xaxes(showticklabels=True)

            return fig

           


            

        @self.app.callback([Output('lora-traffic-graph', 'figure'), Output('aggregation_result_id', 'children')],
                           [Input('interval-component', 'n_intervals')])
        def update_lora_traffic_graph_live(n):

            # print("Update graph : ", controllerGRPC.gw_1_received_frame_num)

            try:
                # Prepare figure
                fig = make_subplots(
                    rows=2, cols=1,
                    shared_xaxes=True,
                    vertical_spacing=0.09,
                )

                ble_plot_colors = ["red", "blue", "black", "green", "orange"]
                # print(list(controllerGRPC.legacy_gw_received_frame_num))
                # print(list(controllerGRPC.E2L_gw_received_frame_num))

                gw_1_received_frame_num = list(controllerGRPC.gw_1_received_frame_num)
                gw_1_transmitted_frame_num = list(controllerGRPC.gw_1_transmitted_frame_num)
                gw_2_received_frame_num = list(controllerGRPC.gw_2_received_frame_num)
                gw_2_transmitted_frame_num = list(controllerGRPC.gw_2_transmitted_frame_num)
                module_received_frame_frame_num = list(controllerGRPC.module_received_frame_frame_num)

                timetsamp_list = list(range(len(gw_1_received_frame_num)))

                fig.add_trace(go.Scatter(x=timetsamp_list, y=gw_1_received_frame_num,
                                        mode='lines+markers', line=dict(color=ble_plot_colors[0], dash = 'dash'), name="RX_GW1",
                                        marker = dict(symbol="circle-open", size=12),
                                        ), row=1, col=1,
                              )
                fig.add_trace(go.Scatter(x=timetsamp_list, y=gw_1_transmitted_frame_num,
                                         mode='lines+markers', line=dict(color=ble_plot_colors[0], dash = 'dash'),  name="TX_GW1",
                                         marker=dict(symbol="triangle-up", size=12),
                                         ), row=1, col=1,
                              )
                fig.add_trace(go.Scatter(x=timetsamp_list, y=gw_2_received_frame_num,
                                         mode='lines+markers', line=dict(color=ble_plot_colors[1], dash = 'dash'), name="RX_GW2",
                                         marker = dict(symbol="circle-open", size=12),
                                        ), row=1, col=1,
                              )
                fig.add_trace(go.Scatter(x=timetsamp_list, y=gw_2_transmitted_frame_num,
                                         mode='lines+markers', line=dict(color=ble_plot_colors[1], dash = 'dash'), name="TX_GW2",
                                         marker = dict(symbol="triangle-up", size=12),
                                        ), row=1, col=1,
                              )
                fig.add_trace(go.Scatter(x=timetsamp_list, y=module_received_frame_frame_num,
                                         mode='lines+markers', line=dict(color=ble_plot_colors[2]), name="RX_DM",
                                         marker = dict(symbol="circle", size=12),
                                        ), row=1, col=1,
                              )

                # ns_received_frame_frame_num = list(controllerGRPC.ns_received_frame_frame_num)
                # ns_transmitted_frame_frame_num = list(controllerGRPC.ns_transmitted_frame_frame_num)
                #
                # fig.add_trace(go.Scatter(x=timetsamp_list, y=ns_received_frame_frame_num,
                #                          mode='lines+markers', line=dict(color=ble_plot_colors[0]), name="RX_NS"
                #                          ), row=2, col=1,
                #               )
                # fig.add_trace(go.Scatter(x=timetsamp_list, y=ns_transmitted_frame_frame_num,
                #                          mode='lines+markers', line=dict(color=ble_plot_colors[1]), name="TX_NS"
                #                          ), row=2, col=1,
                #               )

                stream_reduction = list(controllerGRPC.reduction_frame_num)
                fig.add_trace(go.Scatter(x=timetsamp_list, y=stream_reduction,
                                         mode='lines+markers', line=dict(color=ble_plot_colors[3], dash='dot', ), name="Stream redcution"
                                         ), row=2, col=1,
                              )

                fig.update_yaxes(row=1, col=1, title_text='Number of Frames', range=[-0.3, 6])
                fig.update_yaxes(row=2, col=1, title_text='Stream Frame Reduction [%]', range=[0, 100])
                fig.update_layout( margin=dict(l=10, r=10, t=10, b=10), )

                fig.update_layout(legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01 ))
                # print("end update")
                return fig, str(controllerGRPC.aggregation_function_result[-1])

            except Exception as e:
                print("exception triggered")
                traceback.print_exc()
                pass

        @self.app.callback(
            Output('boolean-slider-output-1', 'children'),
            Input('ed-1-gw-selection', 'value')
        )
        def update_output_ed1(selection):
            controllerGRPC.ed_1_gw_selection=selection
            # return f'The slider is {selection}.'
            return f''

        @self.app.callback(
            Output('boolean-slider-output-2', 'children'),
            Input('ed-2-gw-selection', 'value')
        )
        def update_output_ed2(selection):
            controllerGRPC.ed_2_gw_selection=selection
            # return f'The slider is {selection}.'
            return f''

        @self.app.callback(
            Output('boolean-slider-output-3', 'children'),
            Input('ed-3-gw-selection', 'value')
        )
        def update_output_ed3(selection):
            controllerGRPC.ed_3_gw_selection=selection
            # return f'The slider is {selection}.'
            return f''

        @self.app.callback(
            Output('updateScenarioConfigurationDiv', 'children'),
            Input('updateScenarioConfigurationButton', 'n_clicks'),
            prevent_initial_call=True
        )
        def update_output(n_clicks):
            controllerGRPC.start_key_agreement_process = 1
            # return 'the button has been clicked {} times'.format(n_clicks)
            return ''

        @self.app.callback(
            Output('updateProcessingConfigurationDiv', 'children'),
            [Input('updateProcessingConfigurationButton', 'n_clicks'),
             Input('processing-function-dropdown', 'value'), Input('processing-window-dropdown', 'value')],
            prevent_initial_call=True
        )
        def update_output(n_clicks,processingFunction, processingWindow):
            controllerGRPC.change_processing_configuraiton = 1
            controllerGRPC.process_function = processingFunction
            controllerGRPC.process_window = int(processingWindow)
            # return 'the button has been clicked {} times'.format(n_clicks)
            return ''

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
            try:
                if True: #controllerGRPC.gw1_key_agreement_message_log_updated or \
                        #controllerGRPC.gw2_key_agreement_message_log_updated or controllerGRPC.device_key_agreement_message_updated:

                    # controllerGRPC.gw1_key_agreement_message_log_updated = 0
                    # controllerGRPC.gw2_key_agreement_message_log_updated = 0
                    # controllerGRPC.device_key_agreement_message_updated = 0

                    html_return_content_gw1 = []
                    for ii in range(len(controllerGRPC.key_agreement_message_log_gw1)-1,0,-1):
                        html_return_content_gw1.append(html.Div(controllerGRPC.key_agreement_message_log_gw1[ii], style={"font-weight": "bold"}))

                    html_return_content_gw2 = []
                    for ii in range(len(controllerGRPC.key_agreement_message_log_gw2)-1,0,-1):
                        html_return_content_gw2.append(html.Div(controllerGRPC.key_agreement_message_log_gw2[ii], style={"font-weight": "bold"}))
                        # html_return_content.append(html.P("[{}] ".format("AUDIO MESSAGE"), style={"font-weight": "bold", "color":"red"}))
                        # html_return_content_gw.append(html.Br())

                    html_return_content_device = []
                    for ii in range(len(controllerGRPC.key_agreement_message_log_ed)-1,0,-1):
                        html_return_content_device.append(html.Div(controllerGRPC.key_agreement_message_log_ed[ii], style={"font-weight": "bold"}))

                return data, html.Div(html_return_content_gw1), html.Div(html_return_content_gw2), html.Div(html_return_content_device)

            except Exception as e:
                traceback.print_exc()
                pass

            return data, "test1", "test2", "test3"
