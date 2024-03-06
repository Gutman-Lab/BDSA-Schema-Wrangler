from dash import html, callback, Output, Input, State, dcc
import dash_bootstrap_components as dbc
from utils import deidentify_image
from pathlib import Path


export_tab = html.Div(
    [
        dbc.Input(value="de-id-images", id="deid-output-dir"),
        dbc.Button("De-identify", id="deid-button", color="primary", className="mr-1"),
        html.Div(
            [
                html.Div("Deidentification Progress:", style={"margin-right": "10px"}),
                dbc.Progress(id="deid-progress", value=0, style={"width": "50%"}),
            ],
            style={"display": "flex", "align-items": "center"},
        ),
        html.Div(id="deid-status"),
    ]
)


@callback(
    output=Output("deid-status", "children"),
    inputs=[
        Input("deid-button", "n_clicks"),
        State("deid-output-dir", "value"),
        State("localFileSet_store", "data"),
    ],
    background=True,
    progress=[Output("deid-progress", "value"), Output("deid-progress", "label")],
    prevent_initial_call=True,
)
def update_output(set_progress, n_clicks: bool, save_dir: str, file_store: list[dict]):
    if n_clicks and save_dir:
        save_dir = Path(save_dir)
        save_dir.mkdir(exist_ok=True)

        # De-identify the images.
        total = len(file_store)

        for i, file_data in enumerate(file_store):
            fp = Path(file_data["filePath"])

            save_fp = save_dir.joinpath(fp.name).with_suffix(".png")

            deidentify_image(str(fp), str(save_fp))

            progress = int(((i + 1) / total) * 100)
            set_progress((progress, f"{progress}%"))

            # print(i)
            # set_progress((str(i), str(total)))
            # dbc.Progress(
            #     value=progress,
            #     max=100,
            #     label=f"{progress:.0f}%",
            #     style={"width": "50%"},
            # )
            # )

        return "De-identification complete."
    return ""
