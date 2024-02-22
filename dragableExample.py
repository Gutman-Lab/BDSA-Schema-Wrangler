import random

import dash
from dash import html, ClientsideFunction, Output, Input
import dash_bootstrap_components as dbc

app = dash.Dash(__name__)

app.config.external_stylesheets = ["https://epsi95.github.io/dash-draggable-css-scipt/dragula.css"]
app.config.external_scripts = ["https://cdnjs.cloudflare.com/ajax/libs/dragula/3.7.2/dragula.min.js",
                               "https://epsi95.github.io/dash-draggable-css-scipt/script.js"]


def custom_style():
    return {
        'width': '100px',
        'height': '100px',
        'margin': '10px',
        'background-color': random.choice(['red', 'green', 'blue', 'yellow', 'black'])
    }


app.layout = html.Div([
    html.Div(style=custom_style()),
    html.Div(style=custom_style()),
    html.Div(style=custom_style()),
    html.Div(style=custom_style()),
],
    id='drag-container',
    style={'display': 'flex', 'flex-direction': 'column', 'align-items': 'center'}
)

app.clientside_callback(
    ClientsideFunction(namespace="clientside", function_name="make_draggable"),
    Output("drag-container", "data-drag"),
    Input("drag-container", "id")
)

if __name__ == "__main__":
    app.run_server(debug=True)
