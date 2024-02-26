from dash import html
import dash_bootstrap_components as dbc

header = dbc.Container(
    dbc.Row(
        [
            dbc.Col(
                html.Img(src="assets/BDSA logo.png", height="100px"),
                width="auto",
            ),
            dbc.Col(
                html.Div(
                    className="app-header",
                    children=[html.Div("Data Wrangler", className="app-header--title")],
                ),
            ),
            dbc.Col(html.Div()),
        ],
    ),
    fluid=True,
)
