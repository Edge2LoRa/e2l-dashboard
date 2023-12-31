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

        self.logDevices = collections.deque(maxlen=20)
        self.logGateways = collections.deque(maxlen=20)
        self.logDistributed = collections.deque(maxlen=20)

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

            ],
            id="header",
            className="row flex-display",
            style={"margin-bottom": "25px"},
        )

        sidebar = html.Div(
            [

                dbc.Row(
                    [
                    ],
                    style={"height": "1vh", 'margin': '0px'},
                    className='bg-white'
                ),

                dbc.Row(
                    [
                        html.H6('Settings', style={'margin-top': '12px', 'margin-left': '24px'})
                    ],
                    style={"height": "5vh", 'margin': '0px'},
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
                                # html.Div(id='boolean-slider-output-1')
                            ]),

                            html.Div([
                                html.Label('E2ED 2 GW selection'),
                                dcc.Slider(1, 2, 1, value=self.ed_2_gw_selection, id='ed-2-gw-selection'),
                                # html.Div(id='boolean-slider-output-2')
                            ]),

                            html.Div([
                                html.Label('E2ED 3 GW selection'),
                                dcc.Slider(1, 2, 1, value=self.ed_3_gw_selection, id='ed-3-gw-selection'),
                                # html.Div(id='boolean-slider-output-3')
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
                                value=self.processingWindows[0]
                            ),

                            html.Button('Update configuration', id='updateProcessingConfigurationButton',  n_clicks=0,
                                        style={'margin-top': '16px'},
                                        className='bg-dark text-white'),
                            # html.Button('Update processing configuration', id='updateProcessingConfigurationButton', style={'text-align': 'center', 'vertical-align': 'middle', }),
                            html.Div(id='updateProcessingConfigurationDiv'),
                            html.Hr(),

                            html.Label('AGGREGATION RESULT'),
                            dcc.Markdown(children="0", id='aggregation_result_id', style={'margin-top': '6px', 'text-align': 'center', 'vertical-align': 'middle'}, className='bg-white'),


                        ]
                        )
                    ],
                    style={'height': '50vh', 'margin': '16px'}),
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
                                        dcc.Graph(id="lora-network-topology", animate=False),
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
                                        dcc.Graph(id="lora-traffic-graph", animate=False),
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
                        dbc.Col(sidebar, width=0, className='bg-light'),
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

                print("test new line")
                print(n)
                print(edge_x)
                print(edge_y)

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
                    legend=dict( x=0.4, y=0.99, traceorder="normal", font=dict( family="sans-serif", size=12, color="blue" )) #, orientation='h',)
                    # legend=dict(yanchor="top", y=0.01, xanchor="left", x=0.01 )
                )

                return fig

            except Exception as e:
                traceback.print_exc()
            pass


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
                                         mode='lines+markers', line=dict(color=ble_plot_colors[0]), name="RX_GW1"
                                         ), row=1, col=1,
                              )
                fig.add_trace(go.Scatter(x=timetsamp_list, y=gw_1_transmitted_frame_num,
                                         mode='lines+markers', line=dict(color=ble_plot_colors[0]),  name="TX_GW1",
                                         marker=dict(symbol="triangle-up", size=12),
                                         ), row=1, col=1,
                              )
                fig.add_trace(go.Scatter(x=timetsamp_list, y=gw_2_received_frame_num,
                                         mode='lines+markers', line=dict(color=ble_plot_colors[1]), name="RX_GW2"
                                         ), row=1, col=1,
                              )
                fig.add_trace(go.Scatter(x=timetsamp_list, y=gw_2_transmitted_frame_num,
                                         mode='lines+markers', line=dict(color=ble_plot_colors[1]), name="TX_GW2",
                                        marker = dict(symbol="triangle-up", size=12),
                                        ), row=1, col=1,
                              )
                fig.add_trace(go.Scatter(x=timetsamp_list, y=module_received_frame_frame_num,
                                         mode='lines+markers', line=dict(color=ble_plot_colors[2], dash = 'dash'), name="RX_DM"
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

                stream_reduction = np.array(controllerGRPC.module_received_frame_frame_num) / (np.array(gw_1_transmitted_frame_num) + np.array(gw_2_transmitted_frame_num)) * 100

                fig.add_trace(go.Scatter(x=timetsamp_list, y=stream_reduction,
                                         mode='lines+markers', line=dict(color=ble_plot_colors[3], dash = 'dot',), name="Stream redcution"
                                         ), row=2, col=1,
                              )


                fig.update_yaxes(row=1, col=1, title_text='Number of Frames', range=[-0.3, 6])
                fig.update_yaxes(row=2, col=1, title_text='Stream Frame Reduction [%]', range=[0, 100])
                fig.update_layout( margin=dict(l=10, r=10, t=10, b=10), )

                fig.update_layout(legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01 ))
                # print("end update")
                return fig, str(controllerGRPC.aggregation_function_result[-1])


            except Exception as e:
                traceback.print_exc()
                pass

        # @self.app.callback(
        #     Output('boolean-slider-output-1', 'children'),
        #     Input('ed-1-gw-selection', 'value')
        # )
        # def update_output(selection):
        #     controllerGRPC.ed_1_gw_selection=selection
        #     return f'The slider is {selection}.'
        #
        # @self.app.callback(
        #     Output('boolean-slider-output-2', 'children'),
        #     Input('ed-2-gw-selection', 'value')
        # )
        # def update_output(selection):
        #     controllerGRPC.ed_2_gw_selection=selection
        #     return f'The slider is {selection}.'
        #
        # @self.app.callback(
        #     Output('boolean-slider-output-3', 'children'),
        #     Input('ed-3-gw-selection', 'value')
        # )
        # def update_output(selection):
        #     controllerGRPC.ed_3_gw_selection=selection
        #     return f'The slider is {selection}.'

        @self.app.callback(
            #Output('updateScenarioConfigurationDiv', 'children'),
            Input('updateScenarioConfigurationButton', 'n_clicks'),
            prevent_initial_call=True
        )
        def update_output(n_clicks):
            controllerGRPC.start_key_agreement_process = 1
            return #'the button has been clicked {} times'.format(n_clicks)

        @self.app.callback(
            #Output('updateProcessingConfigurationDiv', 'children'),
            [Input('updateProcessingConfigurationButton', 'n_clicks'),
             Input('processing-function-dropdown', 'value'), Input('processing-window-dropdown', 'value')],
            prevent_initial_call=True
        )
        def update_output(n_clicks,processingFunction, processingWindow):
            controllerGRPC.change_processing_configuraiton = 1
            controllerGRPC.process_function = processingFunction
            controllerGRPC.process_window = int(processingWindow)
            return #'the button has been clicked {} times'.format(n_clicks)

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
                now = date.today()
                # today -= timedelta(days=3) #timedelta(days=6)
                # datetime_last = datetime.strptime(now.strftime("%H:%M:%S"), '%H:%M:%S')
                datetime_last = datetime.now().strftime("%H:%M:%S")
                if controllerGRPC.devices_key_agreement_message_log_updated:
                    controllerGRPC.devices_key_agreement_message_log_updated = 0
                    return_messaage_ed = controllerGRPC.devices_key_agreement_message_log
                    return_messaage_formatted = "[{}] {}".format(datetime_last, return_messaage_ed)
                    self.logDevices.append(return_messaage_formatted)
                    print("test logdevices")
                    print(self.logDevices)

                html_return_content_ed = []
                for ii in range(len(self.logDevices)):
                    html_return_content_ed.append(html.Div(self.logDevices[ii], style={"font-weight": "bold"}))
                    # html_return_content.append(html.P("[{}] ".format("AUDIO MESSAGE"), style={"font-weight": "bold", "color":"red"}))
                    # html_return_content_ed.append(html.Br())

                if controllerGRPC.gw_key_agreement_message_log_updated:
                    controllerGRPC.gw_key_agreement_message_log_updated = 0
                    return_messaage_gw = controllerGRPC.gw_key_agreement_message_log
                    return_messaage_formatted = "[{}] {}".format(datetime_last, return_messaage_gw)
                    self.logGateways.append(return_messaage_formatted)

                html_return_content_gw = []
                for ii in range(len(self.logGateways)):
                    html_return_content_gw.append(html.Div(self.logGateways[ii], style={"font-weight": "bold"}))
                    # html_return_content.append(html.P("[{}] ".format("AUDIO MESSAGE"), style={"font-weight": "bold", "color":"red"}))
                    # html_return_content_gw.append(html.Br())

                if controllerGRPC.module_key_agreement_message_updated:
                    controllerGRPC.module_key_agreement_message_updated = 0
                    return_messaage_ds = controllerGRPC.module_key_agreement_message_log
                    return_messaage_formatted = "[{}] {}".format(datetime_last, return_messaage_ds)
                    self.logDistributed.append(return_messaage_formatted)

                html_return_content_ds = []
                for ii in range(len(self.logDistributed)):
                    html_return_content_ds.append(html.Div(self.logDistributed[ii], style={"font-weight": "bold"}))
                    # html_return_content.append(html.P("[{}] ".format("AUDIO MESSAGE"), style={"font-weight": "bold", "color":"red"}))
                    # html_return_content_ds.append(html.Br())

                return data, html.Div(html_return_content_ed), html.Div(html_return_content_gw), html.Div(html_return_content_ds)

            except Exception as e:
                traceback.print_exc()
                pass

            return data, "test1", "test2", "test3"
