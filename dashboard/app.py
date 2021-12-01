import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc

import plotly.express as px
import pandas as pd
import numpy as np
from scipy.stats import mode

import base64
import librosa
import joblib
import io

from helpers import extract_features, WINDOW_SIZE, BEST_MODEL, MUSIC_GENRES

external_stylesheets = [dbc.themes.BOOTSTRAP]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

styles = {
    'pre': {
        # 'border': 'thin lightgrey solid',
        # 'overflowX': 'scroll'
    }
}

app.layout = html.Div([
    html.Div(
        [dcc.Upload(
            id='upload-song',
            children=html.Div([
                'Arrastra o selecciona un archivo .wav'
            ]),
            className='border rounded-pill p-5 mt-5 mb-3 text-center dashed cursor-pointer c-white f-22-em',
        ),
            dcc.Loading(
                id="loading",
                children=[html.Div(id='output-data-upload', className='text-center m-4 c-white f-16-em')],
                type="circle",
                color='#415053'
            ),
        ],
        className='container d-flex flex-column vh-100 p-5'
    ),
])


def parse_contents(content, filename):
    content_type, content_string = content.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    return


@app.callback(Output('output-data-upload', 'children'),
              Input('upload-song', 'contents'),
              State('upload-song', 'filename'))
def update_output(content, filename):

    if filename is None:
        return dash.no_update

    if '.wav' in filename:
        content_type, content_string = content.split(',')
        decoded = base64.b64decode(content_string)

        signal, sample_rate = librosa.load(io.BytesIO(decoded))
        signal, _ = librosa.effects.trim(signal)  # Get rid of silence at the begining and end
        n_points = WINDOW_SIZE * sample_rate

        predictions = []
        for i in range(int(len(signal) / n_points)):
            window = signal[i * n_points:(i + 1) * n_points]
            if len(window):
                values = extract_features(window)
                model = joblib.load(BEST_MODEL)
                predictions.append(model.predict(np.array(values).reshape(1, -1))[0])

        return html.Div([
            f'El género de la canción que subiste es',
            html.Div(f'{MUSIC_GENRES[mode(predictions)[0][0]].upper()}', className='c-blue f-22-em')
        ])  # ToDo: Base decision on the prediction for all of the windows

    return html.Div('Debes subir un archivo .wav')


# app.layout = html.Div([
#     dcc.Graph(
#         id='basic-interactions',
#         figure=fig
#     ),
#
#     html.Div(className='row', children=[
#         html.Div([
#             dcc.Markdown("""
#                 **Hover Data**
#
#                 Mouse over values in the graph.
#             """),
#             html.Pre(id='hover-data', style=styles['pre'])
#         ], className='three columns'),
#
#         html.Div([
#             dcc.Markdown("""
#                 **Click Data**
#
#                 Click on points in the graph.
#             """),
#             html.Pre(id='click-data', style=styles['pre']),
#         ], className='three columns'),
#
#         html.Div([
#             dcc.Markdown("""
#                 **Selection Data**
#
#                 Choose the lasso or rectangle tool in the graph's menu
#                 bar and then select points in the graph.
#
#                 Note that if `layout.clickmode = 'event+select'`, selection data also
#                 accumulates (or un-accumulates) selected data if you hold down the shift
#                 button while clicking.
#             """),
#             html.Pre(id='selected-data', style=styles['pre']),
#         ], className='three columns'),
#
#         html.Div([
#             dcc.Markdown("""
#                 **Zoom and Relayout Data**
#
#                 Click and drag on the graph to zoom or click on the zoom
#                 buttons in the graph's menu bar.
#                 Clicking on legend items will also fire
#                 this event.
#             """),
#             html.Pre(id='relayout-data', style=styles['pre']),
#         ], className='three columns')
#     ])
# ])

#
# @app.callback(
#     Output('hover-data', 'children'),
#     Input('basic-interactions', 'hoverData'))
# def display_hover_data(hoverData):
#     return json.dumps(hoverData, indent=2)
#
#
# @app.callback(
#     Output('click-data', 'children'),
#     Input('basic-interactions', 'clickData'))
# def display_click_data(clickData):
#     return json.dumps(clickData, indent=2)
#
#
# @app.callback(
#     Output('selected-data', 'children'),
#     Input('basic-interactions', 'selectedData'))
# def display_selected_data(selectedData):
#     return json.dumps(selectedData, indent=2)
#
#
# @app.callback(
#     Output('relayout-data', 'children'),
#     Input('basic-interactions', 'relayoutData'))
# def display_relayout_data(relayoutData):
#     return json.dumps(relayoutData, indent=2)


if __name__ == '__main__':
    app.run_server(debug=True)
