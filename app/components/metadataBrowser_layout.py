from dash import html, callback, Input, Output, no_update, State, dcc, ctx
import pandas as pd
import dash_ag_grid
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from utils import get_csv_files
import json
from jsonschema import Draft7Validator
from collections import Counter
from components.summary_tables import stats_tab
import base64, io

# Grab the CSV file data - NOTE: this may switch to a upload button later.
csv_file_data = get_csv_files("metadata")


def _get_column_defs(cols):
    """Read the shim dictionary."""
    with open("schemaFiles/adrcNpSchema.json", "r") as fh:
        schema = json.load(fh)

    columnDefs = []

    for col in cols:
        if col in ["stainID", "regionName"]:
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
        elif col == "caseID":
            columnDefs.append(
                {
                    "field": col,
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
                }
            )
        else:
            columnDefs.append({"field": col})

    return columnDefs


# Tables.
metadata_table = dash_ag_grid.AgGrid(
    id="metadata-table",
    className="ag-theme-alpine color-fonts compact",
    columnDefs=[],  # _get_column_defs(),
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
            [
                dcc.Upload(
                    dbc.Button(
                        "Upload Metadata File (.csv or .xlsx)",
                        color="info",
                        className="me-1",
                        style={"fontWeight": "bold"},
                    ),
                    id="upload-data",
                    style={
                        "width": "auto",
                        "height": "auto",
                        "lineHeight": "auto",
                        "borderWidth": "1px",
                        # "borderStyle": "dashed",
                        # "borderRadius": "5px",
                        "textAlign": "center",
                        "margin-right": 5,
                        # "margin": "10px",
                    },
                    # multiple=True,  # could make this multiple files, for now the logic is for one.
                ),
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
                html.Div(
                    "Showing metadata for files for:",
                    style={"fontWeight": "bold"},
                ),
                dcc.RadioItems(
                    id="filter-radio",
                    options=[
                        {"label": "All CSV", "value": "all-rows"},
                        {"label": "Only in file system", "value": "filtered-rows"},
                    ],
                    value="filtered-rows",
                    inline=True,
                    style={"margin-left": 10},
                    labelStyle={"margin-right": 10},
                ),
            ],
            style={"display": "flex", "padding": "5px"},
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


@callback(
    Output("metadata-store", "data"),
    [
        Input("upload-data", "contents"),
        Input("upload-data", "filename"),
        Input("shim-dict-btn", "n_clicks"),
    ],
    State("metadata-store", "data"),
    prevent_initial_call=True,
)
def update_metadata_store(contents, filename, n_clicks, current_store):
    """Update the metadata store from selected CSV file."""
    context_id = ctx.triggered_id

    if n_clicks and context_id == "shim-dict-btn" and current_store:
        # Apply the shim dictionary to the entire store and reload!
        with open("shim-dictionary.json", "r") as fh:
            shim_dict = json.load(fh)

        df = pd.DataFrame(current_store).fillna("")

        for i, r in df.iterrows():
            for metadata_key, key_map in shim_dict.items():
                # Check if the row has this key.
                row_value = r.get(metadata_key, "")

                if row_value not in key_map:
                    for k, v in key_map.items():
                        if row_value in v:
                            df.loc[i, metadata_key] = k
                            break

        return df.to_dict("records")
    elif contents is not None:
        # There should be a single file.
        content_type, content_string = contents.split(",")
        decoded = base64.b64decode(content_string)
        df = pd.read_csv(io.StringIO(decoded.decode("utf-8")))

        return df.to_dict("records")

    return []


@callback(
    Output("metadata-table", "rowData"),
    Output("metadata-table", "columnDefs"),
    [Input("metadata-store", "data"), Input("filter-radio", "value")],
    State("localFileSet_store", "data"),
    prevent_initial_call=True,
)
def update_metadata_table(
    metadata_data: list[dict], showing: str, local_fileset_store: list[dict]
) -> list[dict]:
    """Update the metadata table when the metadata store changes or the toggle
    to show all or just the rows matching local file set.

    Args:
        metadata_data (list[dict]): The metadata as a list of dictionaries.
        showing (str): The value of the radio button.
        local_fileset_store (list[dict]): The local fileset store.

    Returns:
        list[dict]: The metadata as a list of dictionaries.

    """
    if metadata_data:
        # Return the metadata directly from store, or filter it by matching to local fileset.
        df = pd.DataFrame(metadata_data).fillna("")
        columnDefs = _get_column_defs(df.columns)

        if showing != "all-rows":
            local_fns = [file_data["fileName"] for file_data in local_fileset_store]

            df = df[df.fileName.isin(local_fns)]

            return df.to_dict("records"), columnDefs

        return metadata_data, columnDefs

    return [], []


@callback(
    Output("collapse", "is_open"),
    Input("stats-btn", "n_clicks"),
    State("collapse", "is_open"),
    prevent_initial_call=True,
)
def toggle_collapse(n_clicks: int, is_open: bool) -> bool:
    if n_clicks:
        return not is_open

    return is_open


@callback(
    [
        Output("stats-summary-table", "rowData"),
        Output("stats-stains-table", "rowData"),
        Output("stats-regions-table", "rowData"),
    ],
    [
        Input("metadata-table", "rowData"),
        Input("metadata-table", "cellValueChanged"),
        Input("stains-switch", "checked"),
        Input("regions-switch", "checked"),
    ],
    prevent_initial_call=True,
)
def get_metadata_stats(
    table_data: list[dict], _: dict, stain_check: bool, region_check: bool
):
    """Get the metadata stats to populate the summary tables.

    Args:
        table_data (list[dict]): The metadata table data.
        _ (dict): The cellValueChanged event data.
        stain_check (bool): The stain switch state.
        region_check (bool): The region switch state.

    Returns:

    """
    if len(table_data):
        # Read the schema.
        with open("schemaFiles/adrcNpSchema.json", "r") as fh:
            schema = json.load(fh)

        valid_regions = schema["properties"]["regionName"]["enum"]
        valid_stains = schema["properties"]["stainID"]["enum"]

        # Convert to dataframe for faster searching.
        table_data = pd.DataFrame(table_data).fillna("")

        if stain_check:
            # Get unmapped stains.
            df = table_data[~table_data.stainID.isin(valid_stains)]
        else:
            df = table_data[table_data.stainID.isin(valid_stains)]

        stains = Counter(df.stainID.tolist())

        if region_check:
            # Get unmapped regions.
            df = table_data[~table_data.regionName.isin(valid_regions)]
        else:
            df = table_data[table_data.regionName.isin(valid_regions)]

        regions = Counter(df.regionName.tolist())

        valid_files = len(
            table_data[
                (table_data.caseID != "")
                & (table_data.stainID.isin(valid_stains))
                & (table_data.regionName.isin(valid_regions))
            ]
        )
        case_valid_count = len(table_data[table_data.caseID != ""])
        stain_valid_count = len(table_data[table_data.stainID.isin(valid_stains)])
        region_valid_count = len(table_data[table_data.regionName.isin(valid_regions)])

        N = len(table_data)

        stats_df = pd.DataFrame(
            [
                ["Files", f"{valid_files} ({valid_files/N*100:.2f}%)"],
                ["caseID", f"{case_valid_count} ({case_valid_count/N*100:.2f}%)"],
                ["stainID", f"{stain_valid_count} ({stain_valid_count/N*100:.2f}%)"],
                [
                    "regionName",
                    f"{region_valid_count} ({region_valid_count/N*100:.2f}%)",
                ],
            ],
            columns=["Field", "Validated"],
        )

        # Populate the stain and region tables.
        stain_df = pd.DataFrame(stains.items(), columns=["Stain", "Count"])
        region_df = pd.DataFrame(regions.items(), columns=["Region", "Count"])

        return (
            stats_df.to_dict("records"),
            stain_df.to_dict("records"),
            region_df.to_dict("records"),
        )

    return [], [], []
