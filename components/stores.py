#  Keep all the Dash Core Components stores in one place.
from dash import dcc, html

stores = html.Div([dcc.Store("metadata-store", data=[])])
