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

        self.gateway_icon = {
                'iconUrl': self.app.get_asset_url("gateway-icon.png"),
                'iconSize': [70,70],
            }

        self.nodes_icons = []
        for i in range(1,8):
            self.nodes_icons.append({
                'iconUrl': self.app.get_asset_url(f"markers/marker_{i}.png"),
                'iconSize': [48,48]
            })
    


        self.gateways_markers = [dl.Marker(position=[gateway.lat,gateway.lon],icon=self.gateway_icon, id=gateway.gw_id ,children=dl.Popup(content=f"This gateways has id: {gateway.gw_id}",autoClose=True,children=dl.Circle(center=[gateway.lat,gateway.lon],color="blue",radius=gateway.coverage*1000))) for gateway in controllerGRPC.gateways_list]
        self.nodes_markers = []
        self.coverage_circles_markers = []
        

        self.logDevices = collections.deque(maxlen=20)
        self.logGateways = collections.deque(maxlen=20)
        self.logDistributed = collections.deque(maxlen=20)

        self.ed_1_gw_selection = 1
        self.ed_2_gw_selection = 1
        self.ed_3_gw_selection = 1
        self.dropdown_process_function = "mean"
        self.dropdown_process_window = 2

        self.app.title = "EDGE2LORA DEMO (MOBICOM 2023)"

        self.processingFunctions = ["Mean and Variance", "Hampel Filter"]
        self.scenarios = ["Moving cluster", "Taxi simulation"]
        self.assigning_policy = ["Random","Nearest","Balanced"]
        self.update_table_rate = 1
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

                            html.Label('Select the scenario to use'),
                            dcc.Dropdown(
                                id='scenario-selection-dropdown',
                                options=[
                                    {'label': '{}'.format(self.scenarios[index]),
                                     'value': '{}'.format(self.scenarios[index])} for index in range(len(self.scenarios))
                                ],
                                value=self.scenarios[0]
                            ),
                            html.Div(id='updateScenarioConfigurationDiv'),
                            
                            # html.Div([
                            #     html.Label('E2ED 1 GW selection'),
                            #     dcc.Slider(1, 2, 1, value=self.ed_1_gw_selection, id='ed-1-gw-selection'),
                            # ]),

                            # html.Div([
                            #     html.Label('E2ED 2 GW selection'),
                            #     dcc.Slider(1, 2, 1, value=self.ed_2_gw_selection, id='ed-2-gw-selection'),
                            # ]),

                            # html.Div([
                            #     html.Label('E2ED 3 GW selection'),
                            #     dcc.Slider(1, 2, 1, value=self.ed_3_gw_selection, id='ed-3-gw-selection'),
                            # ]),
                            html.Hr(),
                            html.P('ASSIGNMENT CONFIGURATION', style={'margin-top': '18px', 'margin-bottom': '4px'}, className='font-weight-bold'),

                            html.Label('Select the policy to use'),
                            dcc.Dropdown(
                                id='policy-selection-dropdown',
                                options=[
                                    {'label': '{}'.format(self.assigning_policy[index]),
                                     'value': '{}'.format(self.assigning_policy[index])} for index in range(len(self.assigning_policy))
                                ],
                                value=self.assigning_policy[0]
                            ),
                            dcc.Input(id="UpdateTableRate", type="number", placeholder="Update Table Rate", value=self.update_table_rate, min=1, max=1000, step=1),
                            html.Div(id='updatePolicyConfigurationDiv'),
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
                                     'value': '{}'.format(self.processingFunctions[index])} for index in range(len(self.processingFunctions))
                                ],
                                value=self.processingFunctions[0]
                            ),

                            html.Label('Select the windows size'),
                            dcc.Dropdown(
                                id='processing-window-dropdown',
                                options=[
                                    {'label': '{}'.format(self.processingWindows[index]),
                                     'value': '{}'.format(self.processingWindows[index])} for index in range(len(self.processingWindows))
                                ],
                                value=self.processingWindows[0]
                            ),

                            html.Button('Update configuration', id='updateProcessingConfigurationButton',  n_clicks=0,
                                        style={'margin-top': '16px'},
                                        className='bg-dark text-white'),
                            # html.Button('Update processing configuration', id='updateProcessingConfigurationButton', style={'text-align': 'center', 'vertical-align': 'middle', }),
                            html.Div(id='updateProcessingConfigurationDiv'),
                            

                            # html.Label('AGGREGATION RESULT'),
                            # dcc.Markdown(children="0", id='aggregation_result_id', style={'margin-top': '6px', 'text-align': 'center', 'vertical-align': 'middle'},
                            #              className='bg-white'),

                            # html.Div(id='boolean-slider-output-1', style={ 'text-align': 'center', 'vertical-align': 'middle'}, className='bg-light text-light font-italic'),
                            # html.Div(id='boolean-slider-output-2', style={ 'text-align': 'center', 'vertical-align': 'middle'}, className='bg-light text-light font-italic'),
                            # html.Div(id='boolean-slider-output-3', style={ 'text-align': 'center', 'vertical-align': 'middle'}, className='bg-light text-light font-italic'),

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
                                        dl.Map([
                                            dl.TileLayer(),
                                            dl.LayersControl([
                                                dl.Overlay(
                                                    dl.LayerGroup(id='nodes-marker-layer', children=self.nodes_markers), 
                                                    name='Nodes', checked=True
                                                ),
                                                dl.Overlay(
                                                    dl.LayerGroup(id='gateway-marker-layer', children=self.gateways_markers), 
                                                    name='Gateways', checked=True
                                                ),
                                            ])],
                                            center=[41.90,12.49], zoom=10, style={'height': '45vh', 'margin-left':'20px', 'margin-right':'20px','width':'97%'}),
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



        @self.app.callback([Output('nodes-marker-layer','children'), Output('gateway-marker-layer','children')],                           
                           [Input('interval-component', 'n_intervals')])
        
        def update_markers_map(n):
            self.nodes_markers = [dl.Marker(position=[device.lat,device.lon], icon=self.nodes_icons[controllerGRPC.gateway_color_dict[device.assigned_gw]]) for device in controllerGRPC.devices_list]
            self.gateways_markers = [dl.Marker(position=[gateway.lat,gateway.lon],icon=self.gateway_icon, id=gateway.gw_id ,children=dl.Popup(content=f"This gateways has id: {gateway.gw_id}",autoClose=True,children=dl.Circle(center=[gateway.lat,gateway.lon],color="blue",radius=gateway.coverage*1000))) for gateway in controllerGRPC.gateways_list]

            return self.nodes_markers, self.gateways_markers
                

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
        

        # @self.app.callback(
        #     Output('coverage-circles', 'children'),
        #     [Input(marker.id, "n_clicks") for marker in self.gateways_markers]
        # )
        # def update_covering_circles(*args):
            
        #     if dash.callback_context.triggered[0]['value'] != None:
        #         removed = False
        #         marker_id = dash.callback_context.triggered[0]["prop_id"].split(".")[0]
                
                
        #         for dev in controllerGRPC.gateways_list:
                    
                            
        #             if dev.gw_id == marker_id:
                        
        #                 for circle in self.coverage_circles_markers:
        #                     if circle.id == f"circle_{marker_id}":
        #                         self.coverage_circles_markers.remove(circle)
        #                         removed = True
        #                         break

        #                 if not removed:
        #                     self.coverage_circles_markers.append(dl.Circle(center=[dev.lat, dev.lon], radius=dev.coverage*1000,id=f"circle_{marker_id}", color='blue', fill=True, fillOpacity=0.3))
        #                     break
                                   
        #     return self.coverage_circles_markers
        


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
            bar_trace_processed = go.Bar(
                x = controllerGRPC.gateways_stats_dataframe['Gateway ID'],
                y = controllerGRPC.gateways_stats_dataframe['processed_frame'],
                name = 'Processed_frame',
                marker=dict(color='green')
            )

            fig = go.Figure(data =[bar_trace_rx, bar_trace_tx, bar_trace_processed])



            fig.update_layout(margin=dict(t=10, b=10), showlegend=True)
            fig.update_xaxes(showticklabels=True)

            return fig


        # @self.app.callback(
        #     Output('updateScenarioConfigurationDiv', 'children'),
        #     Input('updateScenarioConfigurationButton', 'n_clicks'),
        #     prevent_initial_call=True
        # )
        # def update_output(n_clicks):
        #     controllerGRPC.start_key_agreement_process = 1
        #     # return 'the button has been clicked {} times'.format(n_clicks)
        #     return ''

        @self.app.callback(
            Output('updateProcessingConfigurationDiv', 'children'),
            [Input('updateProcessingConfigurationButton', 'n_clicks'),
             Input('processing-function-dropdown', 'value'), Input('processing-window-dropdown', 'value')],
            prevent_initial_call=True
        )
        def update_output(n_clicks,processingFunction, processingWindow):
            controllerGRPC.change_processing_configuraiton = 1
            controllerGRPC.process_function = processingFunction
            if processingWindow is not None :
                controllerGRPC.process_window = int(processingWindow)
            else: 
                controllerGRPC.process_window = 10
            # return 'the button has been clicked {} times'.format(n_clicks)
            return ''

        @self.app.callback(
                Output('updateScenarioConfigurationDiv', 'children'),
                [Input('scenario-selection-dropdown', 'value')],
                 prevent_initial_call=True
        )
        def update_scenario_configuration(scenario):
            controllerGRPC.scenario = scenario
            return ''
        
        @self.app.callback(
            Output('updatePolicyConfigurationDiv', 'children'),
            [Input('policy-selection-dropdown', 'value'),Input('UpdateTableRate', 'value')],
             prevent_initial_call=True
        )
        def update_policy_configuration(policy,rate):
            controllerGRPC.assining_policy = policy
            controllerGRPC.refreshing_table_rate = rate
            return ''
