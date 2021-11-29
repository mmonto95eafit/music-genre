import json

import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output, State
import plotly.express as px
import pandas as pd
import base64

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}

app.layout = html.Div([
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        # Allow multiple files to be uploaded
        multiple=True
    ),
    html.Div(id='output-data-upload'),
])


def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')

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

    return html.Div([
        html.H5(filename),
        html.H6(datetime.datetime.fromtimestamp(date)),

        dash_table.DataTable(
            data=df.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in df.columns]
        ),

        html.Hr(),  # horizontal line

        # For debugging, display the raw contents provided by the web browser
        html.Div('Raw Content'),
        html.Pre(contents[0:200] + '...', style={
            'whiteSpace': 'pre-wrap',
            'wordBreak': 'break-all'
        })
    ])


@app.callback(Output('output-data-upload', 'children'),
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'),
              State('upload-data', 'last_modified'))
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children

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
