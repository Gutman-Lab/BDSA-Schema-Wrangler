from dash import html, callback, Input, Output, no_update, State
import pandas as pd
import dash_ag_grid
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from utils import get_csv_files
import json
from jsonschema import Draft7Validator

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
    style={"height": "50vh"},
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
                )
            ],
            style={"display": "flex"},
        ),
        metadata_table,
    ],
)


@callback(
    Output("metadata-store", "data"),
    [Input("csv-select", "value")],
)
def update_metadata_store(fn: str) -> list[dict]:
    """Update the metadata store from selected CSV file.

    Args:
        fn (str): The filename of the selected CSV file.

    Returns:
        list[dict]: The metadata as a list of dictionaries.

    """
    if fn:
        return pd.read_csv(f"metadata/{fn}").fillna("").to_dict("records")

    return []


@callback(
    Output("metadata-table", "rowData"),
    [Input("metadata-store", "data"), Input("filter-toggler", "checked")],
    State("localFileSet_store", "data"),
    prevent_initial_call=True,
)
def update_metadata_table(
    metadata_data: list[dict], filter: bool, local_fileset_store: list[dict]
) -> list[dict]:
    """Update the metadata table when the metadata store changes or the toggle
    to show all or just the rows matching local file set.

    Args:
        metadata_data (list[dict]): The metadata as a list of dictionaries.
        filter (bool): The toggle to show all or just the rows matching local file set.
        local_fileset_store (list[dict]): The local fileset store.

    Returns:
        list[dict]: The metadata as a list of dictionaries.

    """
    if metadata_data:
        # Return the metadata directly from store, or filter it by matching to local fileset.
        if filter:
            local_fns = [file_data["fileName"] for file_data in local_fileset_store]

            df = pd.DataFrame(metadata_data).fillna("")

            df = df[df.fileName.isin(local_fns)]

            return df.to_dict("records")

        return metadata_data

    return []


@callback(
    Output("metadata-table", "columnDefs"),
    [Input("metadata-table", "rowData"), Input("metadata-table", "cellValueChanged")],
    prevent_initial_call=True,
)
def validate_metadata(table_data: list[dict], _: dict) -> list[dict]:
    """Apply JSON schema validation on the metadata table data, and appropiately
    color the table cells based on the validation results.

    Args:
        table_data (list[dict]): The metadata table data.
        _ (dict): The cellValueChanged event data.

    Returns:
        list[dict]: The column definitions with cell coloring based on validation results.

    """
    # Read the schema.
    with open("schemaFiles/adrcNpSchema.json", "r") as fh:
        schema = json.load(fh)

    validator = Draft7Validator(schema)

    columns = None
    indices = None

    if len(table_data):
        for i, row_data in enumerate(table_data):
            if columns is None:
                columns = list(row_data.keys())
                indices = {col: [] for col in columns}

            error_list = validator.iter_errors(row_data)

            invalid_cols = []

            for e in error_list:
                invalid_cols.append(*e.path)

            for col in invalid_cols:
                indices[col].append(i)

        columnDefs = []

        for col, indices in indices.items():
            indices = ",".join([str(i) for i in indices])
            columnDefs.append(
                {
                    "field": col,
                    "editable": True,
                    "cellStyle": {
                        "styleConditions": [
                            {
                                "condition": f"[{indices}].includes(params.rowIndex)",
                                "style": {"backgroundColor": "#FFB3B3"},
                            },
                        ],
                        "defaultStyle": {"backgroundColor": "#A7FF9D"},
                    },
                }
            )

        return columnDefs

    return []
