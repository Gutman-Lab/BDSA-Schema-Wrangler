import dash_ag_grid
from dash import Input, Output, callback, html
import dash_bootstrap_components as dbc

localFileSet_table = dash_ag_grid.AgGrid(
    id="localFileSet_table",
    columnDefs=[
        {"headerName": "File Name", "field": "fileName", "sortable": True},
        {"headerName": "File Path", "field": "filePath", "sortable": True},
        {"headerName": "File Size (KB)", "field": "fileSize", "sortable": True},
    ],
    style={"height": "80vh"},
    dashGridOptions={
        "pagination": True,
        "paginationAutoPageSize": True,
    },
)


localFileSet_tab = html.Div(
    [
        html.Div(
            "Number of images found: 0",
            id="localFileSet_info",
            style={"fontSize": "20px", "font-weight": "bold"},
        ),
        localFileSet_table,
    ],
)


@callback(
    Output("localFileSet_table", "rowData"), [Input("localFileSet_store", "data")]
)
def update_localFileSet_table(data):

    return data


@callback(
    Output("localFileSet_info", "children"), [Input("localFileSet_store", "data")]
)
def update_localFileSet_info(data):
    return f"Number of files: {len(data)}"
