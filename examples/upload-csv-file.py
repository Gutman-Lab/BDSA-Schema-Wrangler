# This example was generated by ChatGPT and should be clearly stated.
import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import pandas as pd
import base64
import io

# Initialize the Dash app
app = dash.Dash(__name__)

# Define the layout of the app
app.layout = html.Div(
    [
        dcc.Upload(
            id="upload-data",
            children=html.Div(["Drag and Drop or ", html.A("Select Files")]),
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
        html.Div(id="output-data-upload"),
    ]
)


# Define callback to parse uploaded CSV file and display data
@app.callback(
    Output("output-data-upload", "children"),
    [Input("upload-data", "contents"), Input("upload-data", "filename")],
)
def update_output(contents, filename):
    if contents is not None:
        # Parse CSV content
        content_type, content_string = contents[0].split(",")
        decoded = base64.b64decode(content_string)
        df = pd.read_csv(io.StringIO(decoded.decode("utf-8")))

        # Display data as a table
        return html.Div(
            [
                html.H5(filename),
                dash_table.DataTable(
                    data=df.to_dict("records"),
                    columns=[{"name": col, "id": col} for col in df.columns],
                ),
            ]
        )


# Run the Dash app
if __name__ == "__main__":
    app.run_server(debug=True)
