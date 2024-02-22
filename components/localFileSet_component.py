import dash_ag_grid
from dash import Input, Output, State, dcc, callback, html
import dash_bootstrap_components as dbc
import os
from settings import LOCAL_FILESET_PATH

localFileSet_table = dash_ag_grid.AgGrid(
    id="localFileSet_table",
    columnDefs=[
        {"headerName": "File Name", "field": "fileName", "sortable": True},
        {"headerName": "File Path", "field": "filePath", "sortable": True},
        {"headerName": "File Size", "field": "fileSize", "sortable": True},
    ],
)


def get_files_with_size(root_directory):
    file_list = []
    for foldername, subfolders, filenames in os.walk(root_directory):
        for filename in filenames:
            full_path = os.path.join(foldername, filename)
            file_size = os.path.getsize(full_path)
            file_list.append(
                {"filePath": full_path, "fileSize": file_size, "fileName": filename}
            )
    return file_list


fileSet_store = dcc.Store(
    id="localFileSet_store", data=get_files_with_size(LOCAL_FILESET_PATH)
)


localFileSet_tab = dbc.Container(
    [
        dbc.Row([dbc.Col(localFileSet_table), dbc.Col(id="localFileSet_info")]),
        fileSet_store,
    ],
    fluid=True,
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
