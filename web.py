import json
from textwrap import dedent as d

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

# data loader
from utils.data_loaders import load_instagram_data

# Instagram data
es = load_instagram_data(data_dir="Data")

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}

app.layout = html.Div([
    dcc.Graph(
        id='account',
        figure={
            'data': [
                {
                    'x': es["ad_account"].df["age"],
                    'y': es["ad_account"].df["amount_spent"],
                    #'name': row["id"],
                    # "text": row["id"],
                    'mode': 'markers',
                    'marker': {'size': 12},
                    'customdata': es["ad_account"].df.to_dict("r"),
                }
            ],
            'layout': {
                'clickmode': 'event+select'
            }
        }
    ),
    html.Div(className='row', children=[
        html.Div([
            dcc.Markdown(d("""
                **Click Data**

                Click on points in the graph.
            """)),
            html.Pre(id='click-adv', style=styles['pre']),
        ], className='three columns'),
    ]),
    dcc.Graph(
        id='basic-interactions',
        figure={
            'data': [
                {
                    'x': [1, 2, 3, 4],
                    'y': [4, 1, 3, 5],
                    'text': ['a', 'b', 'c', 'd'],
                    'customdata': ['c.a', 'c.b', 'c.c', 'c.d'],
                    'name': 'Trace 1',
                    'mode': 'markers',
                    'marker': {'size': 12}
                },
                {
                    'x': [1, 2, 3, 4],
                    'y': [9, 4, 1, 4],
                    'text': ['w', 'x', 'y', 'z'],
                    'customdata': ['c.w', 'c.x', 'c.y', 'c.z'],
                    'name': 'Trace 2',
                    'mode': 'markers',
                    'marker': {'size': 12}
                }
            ],
            'layout': {
                'clickmode': 'event+select'
            }
        }
    ),

    html.Div(className='row', children=[
        

        html.Div([
            dcc.Markdown(d("""
                **Click Data**

                Click on points in the graph.
            """)),
            html.Pre(id='click-data', style=styles['pre']),
        ], className='three columns'),

        html.Div([
            dcc.Markdown(d("""
                **Selection Data**

                Choose the lasso or rectangle tool in the graph's menu
                bar and then select points in the graph.

                Note that if `layout.clickmode = 'event+select'`, selection data also 
                accumulates (or un-accumulates) selected data if you hold down the shift
                button while clicking.
            """)),
            html.Pre(id='selected-data', style=styles['pre']),
        ], className='three columns'),
    ])
])
@app.callback(
    Output('click-adv', 'children'),
    [Input('account', 'clickData')])
def display_adv_data(clickData):
    details = clickData
    if clickData and "points" in clickData:
        details = clickData["points"][0]["customdata"]
    return json.dumps(details, indent=2)

@app.callback(
    Output('click-data', 'children'),
    [Input('basic-interactions', 'clickData')])
def display_click_data(clickData):
    return json.dumps(clickData, indent=2)


@app.callback(
    Output('selected-data', 'children'),
    [Input('basic-interactions', 'selectedData')])
def display_selected_data(selectedData):
    return json.dumps(selectedData, indent=2)


if __name__ == '__main__':
    app.run_server(debug=True)