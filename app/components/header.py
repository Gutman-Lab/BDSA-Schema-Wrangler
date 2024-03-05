from dash import html, dcc, get_asset_url
import dash_bootstrap_components as dbc
import dash

header_style = {
    "padding-top": "0px",
    "margin-top": "-40px",
    "margin-bottom": "35px",
    "height": 50,
}

header = dbc.Container(
    dbc.Row(
        [
            dbc.Col(
                html.Img(src="assets/thumbnail_BDSA_logo_Cowboy.png", height="80px"),
                width="auto",
            ),
            dbc.Col(
                html.Div(
                    className="app-header text-center",
                    children=[
                        html.Div("BDSA Data Wrangler", className="app-header--title")
                    ],
                ),
                width=10,
            ),
            dbc.Col(html.Div()),
        ],
    ),
    fluid=True,
    style=header_style,
)


# header = html.Div(
#     children=[
#         dcc.Location(id="url", refresh=False),
#         html.A(
#             html.Img(
#                 src="assets/thumbnail_BDSA_logo_Cowboy.png",
#                 className="logo_img",
#             ),
#         ),
#         html.Div(id="picture", style={"float": "right"}),
#     ],
#     className="header",
#     style=header_style,
# )
