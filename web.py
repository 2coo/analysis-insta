import json
from textwrap import dedent as d

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

# data loader
from codes.utils.data_loader import load_fb_data
import featuretools as ft
import pandas as pd

import dash_table


es = load_fb_data(data_dir="data")

adset_feature_matrix, feature_defs = ft.dfs(entityset=es,
                                       target_entity="adset",
                                       agg_primitives=["count", "sum", "mean"],
                                       max_depth=1)
adset_feature_matrix.rename(columns={"MEAN(report.duration)": "duration"}, inplace=True)
adset_feature_matrix.rename(columns={"MEAN(report.lost_days)": "lost_days"}, inplace=True)
targets = ['COUNT(beh)','COUNT(aud)', 'COUNT(demo)', 'COUNT(geo)', 'COUNT(int)']
for adset_id, row in adset_feature_matrix.iterrows():
    target_combination = []
    for target in targets:
        if row[target] > 0:
            target_combination.append(target.replace("COUNT(", "").replace(")",""))
    target_combination = sorted(target_combination)
    if not target_combination:
        target_combination = ["No target"]
    adset_feature_matrix.at[adset_id, "target_combination"] = "; ".join(target_combination)
df_adset = adset_feature_matrix.reset_index()[["account_id", "campaign_id", "adset_id", "campaign.objective", "target_combination", 'COUNT(report)', "duration", "lost_days", "SUM(report.imp)", "SUM(report.spend)", "COUNT(demo)", "COUNT(int)", "COUNT(beh)", "COUNT(geo)", "COUNT(aud)"]]
df_adset["adset_id"] = df_adset["adset_id"].apply(str)
df_adset["account_id"] = df_adset["account_id"].apply(str)
df_adset["campaign_id"] = df_adset["campaign_id"].apply(str)
df_adset.rename(columns={"campaign.objective": "objective", "COUNT(report)": "days", "SUM(report.imp)": "total_imp", "SUM(report.spend)": "total_spend"}, inplace=True)
df_report = es["report"].df.copy()
df_report["account_id"] = df_report["account_id"].apply(str)
df_report["campaign_id"] = df_report["campaign_id"].apply(str)
df_report["adset_id"] = df_report["adset_id"].apply(str)


# Colors for legend
colors = [
    "#001f3f",
    "#0074d9",
    "#3d9970",
    "#111111",
    "#01ff70",
    "#ffdc00",
    "#ff851B",
    "#ff4136",
    "#85144b",
    "#f012be",
    "#b10dc9",
    "#AAAAAA",
    "#111111",
]

# Assign color to legend
colormap = {}
for ind, formation_name in enumerate(df_adset["objective"].unique().tolist()):
    colormap[formation_name] = colors[ind]

app = dash.Dash(__name__)


styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}

app.layout = html.Div([
    html.Div(className="row", children=[
        html.Div(className="seven columns", children=[
                html.Div(className="row", children=[
                    html.Div(className="four columns", children=[
                        dcc.Dropdown(
                            id='color_column',
                            options=[
                                {'label': 'Objective', 'value': 'objective'},
                                {'label': 'Target combination', 'value': 'target_combination'}
                            ],
                            value='objective'
                        ),
                    ]),
                    html.Div(className="five columns", children=[
                        dcc.RadioItems(
                            id="axis_type",
                            options=[
                                {'label': 'Linear', 'value': 'linear'},
                                {'label': 'Log', 'value': 'log'},
                            ],
                            value='linear'
                        )
                    ])
                ]),
                html.Div(className="five columns", children=[

                ])
        ])
    ]),
    html.Div(className="row", children=[
        html.Div(className="seven columns", children=[
            dcc.Graph(
                id='adset',
                figure={
                    'data': [
                        {
                            'x': df_adset.query(f"objective == '{objective}'").total_spend,
                            'y': df_adset.query(f"objective == '{objective}'").total_imp,
                            'name': objective,
                            "text": df_adset.query(f"objective == '{objective}'").adset_id,
                            'mode': 'markers',
                            'marker': {'size': 12},
                            'customdata': [
                                {
                                    **dict_row,
                                    "report_values": df_report[df_report["adset_id"] == str(dict_row["adset_id"])].sort_values(by="date")[["date", "day", "imp", "spend", "frequency"]].to_dict("r")
                                }
                                for dict_row in df_adset.query(f"objective == '{objective}'").to_dict("r")
                            ],
                        } for objective in list(df_adset["objective"].unique())
                    ],
                    'layout': {
                        'clickmode': 'event+select'
                    }
                },
                style={'height': '700px'}
            )
        ]),
        html.Div(className="five columns", children=[
            dcc.Graph(id='imp-spend', style={'height': '450px'}),
            dcc.Graph(id='cpm'),
        ]),
    ]),
    html.Div(className='row', children=[
            dcc.Markdown(d("""
                    **Cliked adset detail**
                """)),
            html.Div([
                html.Pre(id='click-adset', style=styles['pre']),
            ], className='five columns', style={"overflowX": "auto", "height": "500px"}),
            html.Div(className="seven columns", children=[
                dash_table.DataTable(
                    id='table',
                    columns=[{"name": i, "id": i} for i in ["adset_id","date", "spend", "imp"]],
                    data=df_report[["adset_id","date", "spend", "imp"]].to_dict("rows"),
                )
            ], style={"overflowX": "auto", "height": "500px"})
    ]),
])

def create_lineplot(dff):
    axis_type = "linear"
    x_values = []
    y_values = []
    text = []
    if dff is not None:
        x_values = dff['spend'].cumsum()
        y_values = dff['imp'].cumsum()
        text = dff["date"]
    return {
        'data': [dict(
            x=x_values,
            y=y_values,
            text=text,
            mode='lines+markers'
        )],
        'layout': {
            'height': 450,
            'title': "Accumulated Spend vs Accumulated Impression",
            'yaxis': {'type': 'linear' if axis_type == 'linear' else 'log'},
            'xaxis': {'type': 'linear' if axis_type == 'linear' else 'log'}
        }
    }

def create_barplot(dff):
    x_values = []
    y_values = []
    if dff is not None:
        x_values = dff["date"]
        y_values = (dff['spend'].cumsum()/dff['imp'].cumsum()) * 1000
    return {
        'data': [dict(
            x=x_values,
            y=y_values,
            type='bar'
        )],
        'layout': {
            'height': 450,
            'title': "CPM"
        }
    }

@app.callback(
    Output('adset', 'figure'),
    [Input('color_column', 'value'),
    Input('axis_type', 'value')])
def display_adset(color_column, axis_type):
    figure = {
        'data': [
                    {
                        'x': df_adset.query(f"{color_column} == '{value}'").total_spend,
                        'y': df_adset.query(f"{color_column} == '{value}'").total_imp,
                        'name': value,
                        "text": df_adset.query(f"{color_column} == '{value}'").adset_id,
                        'mode': 'markers',
                        'marker': {'size': 12},
                        'customdata': [
                            {
                                **dict_row,
                                "report_values": df_report[df_report["adset_id"] == str(dict_row["adset_id"])].sort_values(by="date")[["date", "day", "imp", "spend", "frequency"]].to_dict("r")
                            }
                            for dict_row in df_adset.query(f"{color_column} == '{value}'").to_dict("r")
                        ],
                    } for value in list(df_adset[color_column].unique())
                ],
        'layout': {
                    'clickmode': 'event+select',
                    'yaxis': {'type': 'linear' if axis_type == 'linear' else 'log'},
                    'xaxis': {'type': 'linear' if axis_type == 'linear' else 'log'}
                }
        }
    return figure


@app.callback(
    Output('click-adset', 'children'),
    [Input('adset', 'clickData')])
def display_adset_details(clickData):
    details = clickData
    if clickData and "points" in clickData:
        details = clickData["points"][0]["customdata"]
        del details["report_values"]
    return json.dumps(details, indent=2)

@app.callback(
    dash.dependencies.Output('imp-spend', 'figure'),
    [Input('adset', 'clickData')])
def update_imp_spend(clickData):
    data = None
    if clickData:
        data = pd.DataFrame(clickData['points'][0]['customdata']["report_values"])
    return create_lineplot(data)


@app.callback(
    dash.dependencies.Output('cpm', 'figure'),
    [Input('adset', 'clickData')])
def update_cpm(clickData):
    data = None
    if clickData:
        data = pd.DataFrame(clickData['points'][0]['customdata']["report_values"])
    return create_barplot(data)


@app.callback(
    dash.dependencies.Output('table', 'data'),
    [Input('adset', 'clickData')])
def update_datatable(clickData):
    data = None
    df = df_report[["adset_id", "date", "spend", "imp"]]
    if clickData:
        adset_id = clickData['points'][0]['customdata']["adset_id"]
        df = df_report[df_report["adset_id"] == str(adset_id)].sort_values(by="date")[["adset_id", "date", "spend", "imp"]]
    return (df.to_dict("r"))

if __name__ == '__main__':
    app.run_server(debug=True)
