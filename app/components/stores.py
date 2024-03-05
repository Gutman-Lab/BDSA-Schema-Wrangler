#  Keep all the Dash Core Components stores in one place.
from dash import dcc, html
from utils import get_files_with_size
from settings import LOCAL_FILESET_PATH


stores = html.Div(
    [
        dcc.Store("metadata-store", data=[]),
        dcc.Store(
            id="localFileSet_store", data=get_files_with_size(LOCAL_FILESET_PATH)
        ),
    ]
)
