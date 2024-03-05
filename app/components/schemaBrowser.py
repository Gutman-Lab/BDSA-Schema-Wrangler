# When switching to using JSON schema, try this approach: https://github.com/coveooss/json-schema-for-humans
# Reference: https://github.com/ghandic/dash_renderjson
import dash_renderjson
from dash import html, callback, Input, Output, no_update
import dash_bootstrap_components as dbc
from pathlib import Path
import json
import dash_mantine_components as dmc

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
    [
        dmc.Switch(id="toggle-schema", label="JSON Schema", checked=True),
        html.Div(
            id="schema-component",
            style={"overflowY": "scroll", "height": "70vh"},
        ),
    ]
)

schema_path = Path("shim-dictionary.json")

if schema_path.is_file():
    with open(schema_path, "r") as fh:
        schema = json.load(fh)


@callback(
    [
        Output("schema-component", "children"),
        Output("toggle-schema", "label"),
    ],
    Input("toggle-schema", "checked"),
)
def toggle_schema_view(checked: bool) -> tuple[html.Div, str]:
    """Toggle the schema view.

    Args:
        checked (bool): Whether the switch is checked.

    Returns:
        tuple[html.Div, str]: The schema view and the switch label.

    """
    if checked:
        return (
            html.Iframe(
                src="assets/schema_doc.html",
                width="100%",
                height="800px",
                style={"overflow": "scroll"},
            ),
            "JSON Schema",
        )
    else:
        return (
            dash_renderjson.DashRenderjson(
                id="bdsa-schema",
                data=schema,
                max_depth=-1,
                theme=_theme,
                invert_theme=True,
            ),
            "Shim Dictionary",
        )
