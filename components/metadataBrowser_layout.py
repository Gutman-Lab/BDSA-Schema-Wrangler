from dash import html, dcc, callback, Input, Output
import pandas as pd
import os
import dash_ag_grid
import dash_bootstrap_components as dbc


metadata_store = dcc.Store(id="metadata_store", data=[])


## This will eventually need to be triggered when we add the upload feature
metadata_files = os.listdir("metadata")


## metadata File Set
csvFile_table = dash_ag_grid.AgGrid(
    id="csvFile_table",
    columnDefs=[
        {"field": "fileName", "headerName": "File Name"},
        {"field": "fileLength", "headerName": "Rows in File"},
    ],
    defaultColDef={
        "filter": "agSetColumnFilter",
        # "editable": True,
        # "flex": 1,
        "filterParams": {"debounceMs": 2500},
        "floatingFilter": True,
        "sortable": True,
        "resizable": True,
    },
    dashGridOptions={
        "rowSelection": "single",
    },
)


bdsaSchemaCols = [
    {"field": "fileName"},
    {"field": "caseID"},
    {"field": "stainID"},
    {"field": "regionName"},
    {"field": "blockID"},
]


bdsaSchema_table = dash_ag_grid.AgGrid(
    id="bdsaSchema_table",
    columnDefs=bdsaSchemaCols,
    dashGridOptions={
        "pagination": True,
        "paginationAutoPageSize": True,
        "rowSelection": "single",
    },
)

metadata_controls = html.Div(
    "Put Buttons here to do things like apply metadata map, show missing data, etc.., ignore certain words, etc..",
    "add something persistent to ignore files but have ability to unignore..mybe use sqlite.. TBD",
)

metadataBrowser_tab = dbc.Container(
    [
        dbc.Row(metadata_controls),
        dbc.Row([dbc.Col(csvFile_table, width=3), dbc.Col(bdsaSchema_table, width=9)]),
        metadata_store,
        dcc.Store(id="csvFileList_store", data=metadata_files),
    ],
    fluid=True,
)


@callback(Output("csvFile_table", "rowData"), [Input("csvFileList_store", "data")])
def update_bdsaMetadatafile(csvFileList):

    mdf = [
        {"fileName": file, "fileLength": len(pd.read_csv(f"metadata/{file}"))}
        for file in csvFileList
    ]
    return mdf


@callback(Output("metadata_store", "data"), [Input("csvFile_table", "selectedRows")])
def update_metadata_store(selectedRows):
    if selectedRows:
        selectedRow = selectedRows[0]
        selectedFile = selectedRow["fileName"]
        df = pd.read_csv(f"metadata/{selectedFile}")
        return df.to_dict("records")
    return []


@callback(Output("bdsaSchema_table", "rowData"), [Input("metadata_store", "data")])
def populate_bdsaSchema_table(metadata):
    if metadata:
        return metadata
    return []
