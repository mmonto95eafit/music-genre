import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc

import numpy as np
from scipy.stats import mode

import base64
import librosa
import joblib
import io
import os

from helpers import extract_features, WINDOW_SIZE, BEST_MODEL, MUSIC_GENRES


external_stylesheets = [dbc.themes.BOOTSTRAP]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

scaler = joblib.load('../data/models/knn_937_scaler.joblib')

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
                values = scaler.transform(np.array(extract_features(window)).reshape(1, -1))
                model = joblib.load(BEST_MODEL)
                predictions.append(model.predict(values)[0])

        return html.Div([
            f'El género de la canción que subiste es',
            html.Div(f'{MUSIC_GENRES[mode(predictions)[0][0]].upper()}', className='c-blue f-22-em')
        ])  # ToDo: Base decision on the prediction for all of the windows

    return html.Div('Debes subir un archivo .wav')


if __name__ == '__main__':
    if os.environ.get('ENV') == 'development':
        app.run_server(debug=True)
    else:
        app.run_server(host='0.0.0.0', port=80)
