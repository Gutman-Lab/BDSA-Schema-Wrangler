import dash_mantine_components as dmc
import dash_ag_grid
from dash import html, Input, Output, State, callback

summary_table = dash_ag_grid.AgGrid(
    id="stats-summary-table",
    className="ag-theme-alpine color-fonts",
    columnDefs=[
        {"field": "Field"},
        {"field": "Validated"},
    ],
    dashGridOptions={
        "pagination": True,
        "paginationAutoPageSize": True,
    },
    rowData=[],
    style={"height": "50vh"},
)

stain_table = html.Div(
    children=[
        html.Div(
            children=[
                dmc.Switch(size="lg", checked=True, id="stains-switch"),
                html.Div(
                    "Unmapped Stains",
                    style={"marginLeft": "5px"},
                    id="stains-switch-label",
                ),
            ],
            style={"display": "flex"},
        ),
        dash_ag_grid.AgGrid(
            id="stats-stains-table",
            className="ag-theme-alpine color-fonts",
            columnDefs=[
                {"field": "Stain"},
                {"field": "Count"},
            ],
            dashGridOptions={
                "pagination": True,
                "paginationAutoPageSize": True,
            },
            rowData=[],
            # style={"height": "70vh"},
        ),
    ],
)

region_table = html.Div(
    children=[
        html.Div(
            children=[
                dmc.Switch(size="lg", checked=True, id="regions-switch"),
                html.Div(
                    "Unmapped Regions",
                    style={"marginLeft": "5px"},
                    id="regions-switch-label",
                ),
            ],
            style={"display": "flex"},
        ),
        dash_ag_grid.AgGrid(
            id="stats-regions-table",
            className="ag-theme-alpine color-fonts",
            columnDefs=[
                {"field": "Region"},
                {"field": "Count"},
            ],
            dashGridOptions={
                "pagination": True,
                "paginationAutoPageSize": True,
            },
            rowData=[],
            # style={"height": "70vh"},
        ),
    ],
)


stats_tab = html.Div(
    dmc.Tabs(
        [
            dmc.TabsList(
                [
                    dmc.Tab("Summary", value="stats-summary"),
                    dmc.Tab("Stains", value="stats-stains"),
                    dmc.Tab("Regions", value="stats-regions"),
                ],
                style={"backgroundColor": "#d9d9d6", "fontSize": "100px"},
            ),
            dmc.TabsPanel(
                summary_table,
                value="stats-summary",
            ),
            dmc.TabsPanel(
                stain_table,
                value="stats-stains",
            ),
            dmc.TabsPanel(
                region_table,
                value="stats-regions",
            ),
        ],
        orientation="horizontal",
        value="stats-summary",
        color="#007dba",
        inverted=True,
        variant="pills",
    ),
)


@callback(
    Output("regions-switch-label", "children"), Input("regions-switch", "checked")
)
def update_regions_switch_label(checked):
    return "Unmapped Regions" if checked else "Valid Regions"


@callback(Output("stains-switch-label", "children"), Input("stains-switch", "checked"))
def update_stains_switch_label(checked):
    return "Unmapped Stains" if checked else "Valid Stains"
