from dash import html, callback, Input, Output, no_update, State
import pandas as pd
import dash_ag_grid
import dash_bootstrap_components as dbc
from pathlib import Path
import json
from collections import Counter
import numpy as np


# In future version, this file might be an upload instead of read from file.
# Get list of CSV files.
def _get_csv_files():
    csv_dir_path = Path("metadata")

    file_names = []

    for fp in csv_dir_path.glob("*.csv"):

        file_names.append({"fileName": fp.name, "fileLength": len(pd.read_csv(fp))})

    return file_names


# Tables.
csv_files_table = dash_ag_grid.AgGrid(
    id="csvs-table",
    columnDefs=[
        {"field": "fileName", "headerName": "File Name"},
        {"field": "fileLength", "headerName": "Rows in File"},
    ],
    defaultColDef={
        "filter": "agSetColumnFilter",
        "filterParams": {"debounceMs": 2500},
        "floatingFilter": True,
        "sortable": True,
        "resizable": True,
    },
    dashGridOptions={
        "rowSelection": "single",
    },
    columnSize="autoSize",
    rowData=_get_csv_files(),
)


metadata_table = dash_ag_grid.AgGrid(
    id="metadata-table",
    columnDefs=[
        {"field": "fileName"},
        {"field": "caseID"},
        {"field": "stainID"},
        {"field": "regionName"},
        {"field": "blockID"},
    ],
    dashGridOptions={
        "pagination": True,
        "paginationAutoPageSize": True,
        "rowSelection": "single",
    },
    rowData=[],
)

stats_card = dbc.Card(
    [
        dbc.CardHeader(
            "Metadata Statistics",
            style={"fontSize": "24px", "fontWeight": "bold"},
        ),
        dbc.CardBody([], id="metadata-stats"),
    ],
    style={"width": "18rem"},
)

metadataBrowser_tab = dbc.Container(
    [
        dbc.Row(
            [
                html.Div(
                    dbc.Button(
                        "Apply Schema",
                        id="apply-schema-btn",
                        color="primary",
                        className="mr-1",
                    ),
                )
            ]
        ),
        dbc.Row(
            [
                dbc.Col(csv_files_table, width=3),
                dbc.Col(dbc.Spinner(metadata_table), width=9),
            ]
        ),
        dbc.Spinner(stats_card),
    ],
    fluid=True,
)


@callback(
    Output("metadata-store", "data"),
    [Input("csvs-table", "selectedRows")],
    prevent_initial_call=True,
)
def update_metadata_store(row):
    """Update the metadata store from selected CSV file."""
    if row:
        return pd.read_csv(f'metadata/{row[0]["fileName"]}').to_dict("records")

    return []


@callback(
    Output("metadata-table", "rowData"),
    [Input("metadata-store", "data")],
    prevent_initial_call=True,
)
def update_metadata_table(metadata):
    if metadata:
        return metadata

    return []


@callback(
    Output("metadata-stats", "children"),
    Input("apply-schema-btn", "n_clicks"),
    State("metadata-store", "data"),
)
def update_metadata_stats(n_clicks, metadata_store):
    if n_clicks and metadata_store:
        # Read the shim-dictionary.
        with open("shim-dictionary.json", "r") as f:
            shim_dict = json.load(f)

        df = pd.DataFrame(metadata_store).fillna("")

        # Do the mapping and return stats.
        stats = {"validStains": [], "validRegions": []}

        for _, r in df.iterrows():
            # Check if stain and region name is valid.
            stain = r["stainID"].capitalize()
            region = r["regionName"].capitalize()

            if stain in shim_dict["stainNames"]:
                stats["validStains"].append(stain)
            else:
                # Attempt to remap!
                for s, values in shim_dict["stainNames"].items():
                    for v in values:
                        if v == stain:
                            stats["validStains"].append(s)

            if region in shim_dict["regionNames"]:
                stats["validRegions"].append(region)
            else:
                # Attempt to remap!
                for s, values in shim_dict["regionNames"].items():
                    for v in values:
                        if v == region:
                            stats["validRegions"].append(s)

        # Report the stats.
        regions = Counter(stats["validRegions"])
        stains = Counter(stats["validStains"])

        nl = html.Br()

        t = "Valid Stains Found"
        report = [f"Rows found in CSV: {len(df)}", nl, t, nl, "-" * len(t), nl]

        for k, v in stains.items():
            report.append(f"   {k} (n={v})")
            report.append(nl)

        t = "Valid Regions Found"
        report.extend([nl, t, nl, "-" * len(t), nl])

        for k, v in regions.items():
            report.append(f"   {k} (n={v})")
            report.append(nl)

        return [html.P(report)]

    return [html.P()]


# stats_card = dbc.Card(
#     [
#         dbc.CardHeader(
#             "Metadata Statistics",
#             style={"fontSize": "24px", "fontWeight": "bold"},
#         ),
#         dbc.CardBody([], id="metadata-stats"),
#     ],
#     style={"width": "18rem"},
# )
