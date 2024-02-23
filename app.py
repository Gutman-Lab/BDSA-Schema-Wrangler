import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash import Dash, html, dcc
from components.localFileSet_component import localFileSet_tab
from components.metadataBrowser_layout import metadataBrowser_tab
from components.schemaBrowser import schema_browser
from components import stores

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


tab_list = html.Div(
    dmc.Tabs(
        [
            dmc.TabsList(
                [
                    dmc.Tab("Local File Set", value="localWSIfiles"),
                    dmc.Tab("Metadata Browser", value="metadataBrowser"),
                    dmc.Tab("BDSA Schema", value="bdsaSchema"),
                    dmc.Tab("Mapper", value="mapper"),
                ],
            ),
            dmc.TabsPanel(
                localFileSet_tab,
                value="localWSIfiles",
            ),
            dmc.TabsPanel(
                metadataBrowser_tab,
                value="metadataBrowser",
            ),
            dmc.TabsPanel(
                schema_browser,
                value="bdsaSchema",
            ),
            dmc.TabsPanel(
                html.Div("Mapping Data"),
                value="mapper",
            ),
        ],
        orientation="horizontal",
        value="localWSIfiles",
        color="#6384c6",
        inverted=True,
        variant="pills",
    )
)


app.layout = dbc.Container(
    [stores, bdsa_header, tab_list],
    fluid=True,
)

server = app.server

if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0")
