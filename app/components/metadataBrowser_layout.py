from dash import html, callback, Input, Output, no_update, State, dcc
import pandas as pd
import dash_ag_grid
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from utils import get_csv_files
import json
from jsonschema import Draft7Validator
from collections import Counter
from components.summary_tables import stats_tab

# Grab the CSV file data - NOTE: this may switch to a upload button later.
csv_file_data = get_csv_files("metadata")


def _get_column_defs():
    """Read the shim dictionary."""
    with open("schemaFiles/adrcNpSchema.json", "r") as fh:
        schema = json.load(fh)

    columnDefs = [
        {"field": "fileName"},
        {
            "field": "caseID",
            "editable": True,
            "cellStyle": {
                "styleConditions": [
                    {
                        "condition": 'params.value != ""',
                        "style": {"backgroundColor": "#A7FF9D"},
                    },
                ],
                "defaultStyle": {"backgroundColor": "#FFB3B3"},
            },
        },
    ]

    for col in ["stainID", "regionName"]:

        values = schema["properties"][col]["enum"]

        values = [f'"{v}"' for v in values]

        columnDefs.append(
            {
                "field": col,
                "editable": True,
                "cellStyle": {
                    "styleConditions": [
                        {
                            "condition": f"[{','.join(values)}].includes(params.value)",
                            "style": {"backgroundColor": "#A7FF9D"},
                        },
                    ],
                    "defaultStyle": {"backgroundColor": "#FFB3B3"},
                },
            }
        )

    columnDefs.append({"field": "blockID"})

    return columnDefs


# Tables.
metadata_table = dash_ag_grid.AgGrid(
    id="metadata-table",
    className="ag-theme-alpine color-fonts compact",
    columnDefs=_get_column_defs(),
    dashGridOptions={
        "pagination": True,
        "paginationAutoPageSize": True,
        "rowSelection": "single",
    },
    rowData=[],
)

csv_select_data = [
    {
        "value": dct["fileName"],
        "label": f"{dct['fileName']} (rows = {dct['fileLength']})",
    }
    for dct in csv_file_data
]

metadataBrowser_tab = html.Div(
    [
        html.Div(
            children=[
                # html.Div(
                #     "Select CSV File:", style={"padding": "5x", "fontWeight": "bold"}
                # ),
                # dmc.Select(
                #     placeholder="No CSV files found.",
                #     id="csv-select",
                #     data=csv_select_data,
                #     value=csv_select_data[0]["value"] if len(csv_select_data) else "",
                #     style={"marginLeft": "5px", "marginRight": "5px", "width": "300px"},
                # ),
                dcc.Upload(
                    id="upload-data",
                    children=html.Div(
                        [
                            dbc.Button(
                                "Upload Metadata File (.csv or .xlsx)",
                                color="info",
                                className="me-1",
                            ),
                        ]
                    ),
                    style={
                        "width": "100%",
                        "height": "60px",
                        "lineHeight": "60px",
                        "borderWidth": "1px",
                        "borderStyle": "dashed",
                        "borderRadius": "5px",
                        "textAlign": "center",
                        "margin": "10px",
                    },
                    multiple=True,
                ),
            ],
            style={"display": "flex", "padding": "5px"},
        ),
        html.Div(
            [
                dbc.Button(
                    "Apply Shim Dictionary",
                    id="shim-dict-btn",
                    color="warning",
                    className="me-1",
                ),
                dbc.Button(
                    "Export CSV",
                    id="export-btn",
                    color="success",
                    className="me-1",
                ),
                dmc.Switch(
                    size="lg",
                    checked=True,
                    id="filter-toggler",
                    style={"marginRight": "5px"},
                ),
                html.Div(
                    "Showing metadata for files in local fileset.",
                    id="filter-label",
                    style={"fontWeight": "bold"},
                ),
            ],
            style={"display": "flex"},
        ),
        html.Div(
            children=[
                metadata_table,
                dbc.Collapse(
                    stats_tab, id="collapse", is_open=False, style={"width": "50%"}
                ),
                dbc.Button(
                    "Stats",
                    id="stats-btn",
                    color="primary",
                    className="me-1",
                    style={"height": "auto"},
                ),
            ],
            style={"display": "flex"},
        ),
    ],
)


# @callback(
#     Output("collapse", "is_open"),
#     Input("stats-btn", "n_clicks"),
#     State("collapse", "is_open"),
#     prevent_initial_call=True,
# )
# def toggle_collapse(n_clicks: int, is_open: bool) -> bool:
#     if n_clicks:
#         return not is_open

#     return is_open


# # NOTE: this callback will have issues when we add more CSVs.
# # NOTE: another issue with this callback, is that it applies the shim dictionary
# # to the entire data no matter if the toggle is showing only the rows in dataset
# @callback(
#     Output("metadata-store", "data"),
#     [Input("csv-select", "value"), Input("shim-dict-btn", "n_clicks")],
# )
# def update_metadata_store(fn: str, n_clicks: int) -> list[dict]:
#     """Update the metadata store from selected CSV file.

#     Args:
#         fn (str): The filename of the selected CSV file.
#         n_clicks (int): The number of times the button was clicked.

#     Returns:
#         list[dict]: The metadata as a list of dictionaries.

#     """
#     if fn:
#         df = pd.read_csv(f"metadata/{fn}").fillna("")

#         if n_clicks:
#             # Apply shim dictionary.
#             with open("shim-dictionary.json", "r") as fh:
#                 shim_dict = json.load(fh)

#             for i, r in df.iterrows():
#                 for metadata_key, key_map in shim_dict.items():
#                     # Check if the row has this key.
#                     row_value = r.get(metadata_key, "")

#                     if row_value not in key_map:
#                         for k, v in key_map.items():
#                             if row_value in v:
#                                 df.loc[i, metadata_key] = k
#                                 break

#         return df.to_dict("records")

#     return []


# @callback(
#     Output("metadata-table", "rowData"),
#     [Input("metadata-store", "data"), Input("filter-toggler", "checked")],
#     State("localFileSet_store", "data"),
#     prevent_initial_call=True,
# )
# def update_metadata_table(
#     metadata_data: list[dict], filter: bool, local_fileset_store: list[dict]
# ) -> list[dict]:
#     """Update the metadata table when the metadata store changes or the toggle
#     to show all or just the rows matching local file set.

#     Args:
#         metadata_data (list[dict]): The metadata as a list of dictionaries.
#         filter (bool): The toggle to show all or just the rows matching local file set.
#         local_fileset_store (list[dict]): The local fileset store.

#     Returns:
#         list[dict]: The metadata as a list of dictionaries.

#     """
#     if metadata_data:
#         # Return the metadata directly from store, or filter it by matching to local fileset.
#         if filter:
#             local_fns = [file_data["fileName"] for file_data in local_fileset_store]

#             df = pd.DataFrame(metadata_data).fillna("")

#             df = df[df.fileName.isin(local_fns)]

#             return df.to_dict("records")

#         return metadata_data

#     return []


# @callback(
#     [
#         Output("stats-summary-table", "rowData"),
#         Output("stats-stains-table", "rowData"),
#         Output("stats-regions-table", "rowData"),
#     ],
#     [
#         Input("metadata-table", "rowData"),
#         Input("metadata-table", "cellValueChanged"),
#         Input("stains-switch", "checked"),
#         Input("regions-switch", "checked"),
#     ],
#     prevent_initial_call=True,
# )
# def get_metadata_stats(
#     table_data: list[dict], _: dict, stain_check: bool, region_check: bool
# ):
#     """Get the metadata stats to populate the summary tables.

#     Args:
#         table_data (list[dict]): The metadata table data.
#         _ (dict): The cellValueChanged event data.
#         stain_check (bool): The stain switch state.
#         region_check (bool): The region switch state.

#     Returns:

#     """
#     if len(table_data):
#         # Read the schema.
#         with open("schemaFiles/adrcNpSchema.json", "r") as fh:
#             schema = json.load(fh)

#         valid_regions = schema["properties"]["regionName"]["enum"]
#         valid_stains = schema["properties"]["stainID"]["enum"]

#         # Convert to dataframe for faster searching.
#         table_data = pd.DataFrame(table_data).fillna("")

#         if stain_check:
#             # Get unmapped stains.
#             df = table_data[~table_data.stainID.isin(valid_stains)]
#         else:
#             df = table_data[table_data.stainID.isin(valid_stains)]

#         stains = Counter(df.stainID.tolist())

#         if region_check:
#             # Get unmapped regions.
#             df = table_data[~table_data.regionName.isin(valid_regions)]
#         else:
#             df = table_data[table_data.regionName.isin(valid_regions)]

#         regions = Counter(df.regionName.tolist())

#         valid_files = len(
#             table_data[
#                 (table_data.caseID != "")
#                 & (table_data.stainID.isin(valid_stains))
#                 & (table_data.regionName.isin(valid_regions))
#             ]
#         )
#         case_valid_count = len(table_data[table_data.caseID != ""])
#         stain_valid_count = len(table_data[table_data.stainID.isin(valid_stains)])
#         region_valid_count = len(table_data[table_data.regionName.isin(valid_regions)])

#         N = len(table_data)

#         stats_df = pd.DataFrame(
#             [
#                 ["Files", f"{valid_files} ({valid_files/N*100:.2f}%)"],
#                 ["caseID", f"{case_valid_count} ({case_valid_count/N*100:.2f}%)"],
#                 ["stainID", f"{stain_valid_count} ({stain_valid_count/N*100:.2f}%)"],
#                 [
#                     "regionName",
#                     f"{region_valid_count} ({region_valid_count/N*100:.2f}%)",
#                 ],
#             ],
#             columns=["Field", "Validated"],
#         )

#         # Populate the stain and region tables.
#         stain_df = pd.DataFrame(stains.items(), columns=["Stain", "Count"])
#         region_df = pd.DataFrame(regions.items(), columns=["Region", "Count"])

#         return (
#             stats_df.to_dict("records"),
#             stain_df.to_dict("records"),
#             region_df.to_dict("records"),
#         )

#     return [], [], []
