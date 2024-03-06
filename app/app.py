import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash import Dash, html, DiskcacheManager
import diskcache

from components.localFileSet_component import localFileSet_tab
from components.metadataBrowser_layout import metadataBrowser_tab
from components.schemaBrowser import schema_browser
from components.export_tab import export_tab
from components import stores, header

# Run using cache as background callbacks.
cache = diskcache.Cache("./cache")
background_callback_manager = DiskcacheManager(cache)

# Creating app and applying theme.
app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    assets_folder="assets",
    background_callback_manager=background_callback_manager,
)

tab_list = html.Div(
    dmc.Tabs(
        [
            dmc.TabsList(
                [
                    dmc.Tab("Local File Set", value="localWSIfiles"),
                    dmc.Tab("Metadata Browser", value="metadataBrowser"),
                    dmc.Tab("Export", value="export-tab"),
                    dmc.Tab("BDSA Schema", value="bdsaSchema"),
                    # dmc.Tab("Mapper", value="mapper"),
                ],
                style={"backgroundColor": "#d9d9d6", "fontSize": "100px"},
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
                export_tab,
                value="export-tab",
            ),
            dmc.TabsPanel(
                schema_browser,
                value="bdsaSchema",
            ),
            # dmc.TabsPanel(html.Div("Mapping Data"), value="mapper"),
        ],
        orientation="horizontal",
        value="export-tab",
        color="#007dba",
        inverted=True,
        variant="pills",
    ),
)


app.layout = dbc.Container(
    [stores, header, tab_list],
    fluid=True,
)

if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0")
