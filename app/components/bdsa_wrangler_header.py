from dash import html, dcc
import dash


wrangler_header = html.Div(
    children=[
        dcc.Location(id="url", refresh=False),
        html.A(
            html.Img(
                src=dash.get_asset_url("logo.png"),
                className="logo_img",
            ),
        ),
        html.Div(id="picture", style={"float": "right"}),
    ],
    className="header",
    style={
        "padding-top": "0px",
        "margin-top": "0px",
        "margin-bottom": "0px",
        "height": 50,
    },
)
