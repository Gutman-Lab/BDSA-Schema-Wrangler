import dash_bootstrap_components as dbc
from dash import Dash, html, dcc
from components.localFileSet_component import localFileSet_tab
from components.metadataBrowser_layout import metadataBrowser_tab
from components.schemaBrowser import schema_browser

# Creating app and applying theme.
app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])


tabs_styles = {"height": "44px", "margin-bottom": "10px"}
tab_style = {
    "borderBottom": "1px solid #d6d6d6",
    "padding": "6px",
    "fontSize": "24px",
    "fontWeight": "bold",
}

tab_selected_style = {
    "borderTop": "1px solid #d6d6d6",
    "borderBottom": "1px solid #d6d6d6",
    "backgroundColor": "#119DFF",
    "color": "white",
    "fontSize": "24px",
    "padding": "6px",
    "fontWeight": "bold",
}


bdsa_header = html.Div(
    [
        html.H1("BDSA Data Wrangler", className="display-4"),
    ]
)

tab_list = dcc.Tabs(
    id="bdsa_tabs",
    value="bdsaSchema",
    children=[
        dcc.Tab(
            label="Local FileSet",
            value="localWSIfiles",
            style=tab_style,
            selected_style=tab_selected_style,
            children=[localFileSet_tab],
        ),
        dcc.Tab(
            label="Metadata Browser",
            value="metadataBrowser",
            style=tab_style,
            selected_style=tab_selected_style,
            children=[metadataBrowser_tab],
        ),
        dcc.Tab(
            children=[schema_browser],
            label="BDSA Schema",
            value="bdsaSchema",
            style=tab_style,
            selected_style=tab_selected_style,
        ),
        dcc.Tab(
            children=[html.Div("Mapping Data")],
            label="Mapper",
            value="mapper",
            style=tab_style,
            selected_style=tab_selected_style,
        ),
    ],
)


app.layout = dbc.Container(
    [bdsa_header, tab_list, html.Div(id="bdsa_tab_content")],
    fluid=True,
)

server = app.server

if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0")
