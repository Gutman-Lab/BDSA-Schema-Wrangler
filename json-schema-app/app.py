# Main application for BDSA JSON Schema Viewer.
from dash import Dash, html, callback, Input, Output, dcc
from pathlib import Path
import json
import dash_renderjson


def load_schema():
    """Internal function to load the schema on app startup."""
    schema_path = Path("bdsa-schema.json")

    if schema_path.is_file():
        with open(schema_path, "r") as fh:
            schema = json.load(fh)
    else:
        schema = {}

    return schema


theme = {
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

app = Dash(__name__)

app.layout = html.Div(
    [
        html.H1(
            "BDSA JSON Schema Viewer",
            style={
                "backgroundColor": "lightblue",
                "color": "black",
                "padding": "10px",
                "margin": "0",
            },
        ),
        dcc.Store(id="schema-store", data=load_schema()),
        html.Div(id="viewer"),
    ],
    style={"margin": "0"},
)


@callback(
    Output("viewer", "children"),
    Input("schema-store", "data"),
)
def update_viewer(data: dict):
    # Update the JSON schema viewer.
    if data:
        return (
            html.Iframe(
                src="assets/bdsa-schema.html",
                width="100%",
                height="800px",
                style={"overflow": "scroll"},
            ),
        )
        return dash_renderjson.DashRenderjson(
            data=data,
            max_depth=-1,
            theme=theme,
            invert_theme=True,
        )

    return []


if __name__ == "__main__":
    app.run_server(debug=True, port=8050, host="0.0.0.0")
