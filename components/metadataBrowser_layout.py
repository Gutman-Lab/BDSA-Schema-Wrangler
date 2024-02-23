from dash import html, callback, Input, Output, no_update, State
import pandas as pd
import dash_ag_grid
import dash_bootstrap_components as dbc
from pathlib import Path
import json
from collections import Counter
import dash_mantine_components as dmc
from utils import get_csv_files

# Grab the CSV file data - NOTE: this may switch to a upload button later.
csv_file_data = get_csv_files("metadata")

# Tables.
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
    style={"height": "75vh"},
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

csv_select_data = [
    {
        "value": dct["fileName"],
        "label": f"{dct['fileName']} (rows = {dct['fileLength']})",
    }
    for dct in csv_file_data
]

metadataBrowser_tab = html.Div(
    [
        dmc.Select(
            label="Select CSV File:",
            placeholder="No CSV files found.",
            id="csv-select",
            data=csv_select_data,
            value=csv_select_data[0]["value"] if len(csv_select_data) else "",
            style={"width": 200, "marginBottom": 10, "width": "auto"},
        ),
        html.Div(
            [
                dmc.Switch(
                    onLabel="In Fileset Only",
                    offLabel="       Show All",
                    size="lg",
                    checked=True,
                    id="filter-toggler",
                ),
                dbc.Button(
                    "Apply Schema",
                    id="apply-schema-btn",
                    color="primary",
                    className="mr-1",
                ),
            ],
            style={"display": "flex"},
        ),
        dbc.Spinner(metadata_table),
        # dbc.Spinner(stats_card),
    ],
)


@callback(
    Output("metadata-store", "data"),
    [Input("csv-select", "value")],
)
def update_metadata_store(value):
    """Update the metadata store from selected CSV file."""
    if value:
        return pd.read_csv(f"metadata/{value}").to_dict("records")

    return []


@callback(
    Output("metadata-table", "rowData"),
    [Input("metadata-store", "data"), Input("filter-toggler", "checked")],
    State("localFileSet_store", "data"),
    prevent_initial_call=True,
)
def update_metadata_table(metadata, filter, local_fileset_store):
    if metadata:
        if filter:
            # Only show rows for file in the dataset.
            from pprint import pprint

            local_fns = [file_data["fileName"] for file_data in local_fileset_store]

            df = pd.DataFrame(metadata)

            df = df[df.fileName.isin(local_fns)]

            return df.to_dict("records")

        return metadata

    return []


# @callback(
#     Output("metadata-stats", "children"),
#     Input("apply-schema-btn", "n_clicks"),
#     State("metadata-store", "data"),
# )
# def update_metadata_stats(n_clicks, metadata_store):
#     if n_clicks and metadata_store:
#         # Read the shim-dictionary.
#         with open("shim-dictionary.json", "r") as f:
#             shim_dict = json.load(f)

#         df = pd.DataFrame(metadata_store).fillna("")

#         # Do the mapping and return stats.
#         stats = {"validStains": [], "validRegions": []}

#         for _, r in df.iterrows():
#             # Check if stain and region name is valid.
#             stain = r["stainID"].capitalize()
#             region = r["regionName"].capitalize()

#             if stain in shim_dict["stainNames"]:
#                 stats["validStains"].append(stain)
#             else:
#                 # Attempt to remap!
#                 for s, values in shim_dict["stainNames"].items():
#                     for v in values:
#                         if v == stain:
#                             stats["validStains"].append(s)

#             if region in shim_dict["regionNames"]:
#                 stats["validRegions"].append(region)
#             else:
#                 # Attempt to remap!
#                 for s, values in shim_dict["regionNames"].items():
#                     for v in values:
#                         if v == region:
#                             stats["validRegions"].append(s)

#         # Report the stats.
#         regions = Counter(stats["validRegions"])
#         stains = Counter(stats["validStains"])

#         nl = html.Br()

#         t = "Valid Stains Found"
#         report = [f"Rows found in CSV: {len(df)}", nl, t, nl, "-" * len(t), nl]

#         for k, v in stains.items():
#             report.append(f"   {k} (n={v})")
#             report.append(nl)

#         t = "Valid Regions Found"
#         report.extend([nl, t, nl, "-" * len(t), nl])

#         for k, v in regions.items():
#             report.append(f"   {k} (n={v})")
#             report.append(nl)

#         return [html.P(report)]

#     return [html.P()]


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
