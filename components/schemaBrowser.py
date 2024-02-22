# When switching to using JSON schema, try this approach: https://github.com/coveooss/json-schema-for-humans
# Reference: https://github.com/ghandic/dash_renderjson
import dash_renderjson
from dash import html, callback, Input, Output, no_update
import dash_bootstrap_components as dbc
from pathlib import Path
import json

_theme = {
    "scheme": "monokai",
    "author": "wimer hazenberg (http://www.monokai.nl)",
    "base00": "#272822",
    "base01": "#383830",
    "base02": "#49483e",
    "base03": "#75715e",
    "base04": "#a59f85",
    "base05": "#f8f8f2",
    "base06": "#f5f4f1",
    "base07": "#f9f8f5",
    "base08": "#f92672",
    "base09": "#fd971f",
    "base0A": "#f4bf75",
    "base0B": "#a6e22e",
    "base0C": "#a1efe4",
    "base0D": "#66d9ef",
    "base0E": "#ae81ff",
    "base0F": "#cc6633",
}


schema_browser = html.Div(
    children=[
        dbc.Button(
            "Update Schema", id="update-schema-btn", color="success", className="me-1"
        ),
        dash_renderjson.DashRenderjson(
            id="bdsa-schema", data={}, max_depth=-1, theme=_theme, invert_theme=True
        ),
    ],
    style={"overflowY": "scroll", "height": "80vh"},
)


@callback(Output("bdsa-schema", "data"), Input("update-schema-btn", "n_clicks"))
def update_schema(n_clicks):
    schema_path = Path("shim-dictionary.json")

    if schema_path.is_file():
        with open(schema_path, "r") as fh:
            schema = json.load(fh)
        return schema

    return no_update
