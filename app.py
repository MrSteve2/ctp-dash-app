import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from plotly.subplots import make_subplots

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}


def get_CTP_and_Census_data():
    URL = 'https://covidtracking.com/api/states/daily'
    CTP_df = pd.read_json(URL, dtype={'date': 'int64'})
    CTP_df['date_val'] = pd.to_datetime(CTP_df['date'], format='%Y%m%d')
    CTP_df.sort_values(['state', 'date'], inplace=True)

    for item in ['deathIncrease', 'positiveIncrease', 'totalTestResultsIncrease', 'hospitalizedIncrease', 'hospitalizedCurrently']:
        CTP_df[item + '_7day'] = CTP_df.groupby(
            'state')[item].rolling(7).mean().reset_index(0, drop=True)

    census_pop = pd.read_csv('https://data.cdc.gov/api/views/b2jx-uyck/rows.csv',
                             names=['pop_year', 'state', 'state_name', 'TopicType', 'TopicDesc', 'DataSource', 'Data_Value_Type', 'Population', 'Gender', 'Age',
                                    'GeoLocation', 'Source_File_USCB', 'Data_Pulled', 'LocationID', 'TopicTypeId', 'TopicId', 'MeasureId', 'StratificationID1',
                                    'StratificationID2', 'SubMeasureID', 'DisplayOrder'],
                             usecols=['pop_year', 'state', 'state_name',
                                      'Population', 'Gender', 'Age', 'GeoLocation'],
                             skiprows=1)
    max_year = census_pop.pop_year.max()
    census_pop_latest = census_pop[(census_pop.Gender == 'Total') &
                                   (census_pop.Age == 'Total') &
                                   (census_pop.pop_year == max_year)]

    df = pd.merge(CTP_df, census_pop_latest[[
        'pop_year', 'state', 'state_name', 'Population', 'GeoLocation']], on='state', how='outer')
    cols_to_per_million = ['positive', 'negative', 'pending',
                           'hospitalizedCurrently', 'hospitalizedCumulative', 'inIcuCurrently',
                           'inIcuCumulative', 'onVentilatorCurrently', 'onVentilatorCumulative',
                           'death', 'hospitalized',
                           'totalTestsViral', 'positiveTestsViral', 'negativeTestsViral',
                           'positiveCasesViral', 'positiveIncrease', 'negativeIncrease',
                           'totalTestResults', 'totalTestResultsIncrease',
                           'deathIncrease', 'hospitalizedIncrease',
                           'totalTestResultsIncrease_7day', 'positiveIncrease_7day',
                           'deathIncrease_7day', 'hospitalizedIncrease_7day', 'hospitalizedCurrently_7day']
    for col in cols_to_per_million:
        df[col + '_permil'] = df[col] / (df['Population'] / 1000000)
    return df


def get_state_options():
    state_options = []
    for index, row in df[['state', 'state_name']].drop_duplicates().fillna('NaN').iterrows():
        # print(row['state'], row['state_name'])
        if (row['state_name'] != 'NaN'):
            state_options.append(
                {'label': row['state_name'], 'value': row['state']})
    return state_options


df = get_CTP_and_Census_data()

state_options = get_state_options()
app.layout = html.Div([
    html.H1(children='The Covid Tracking Project - in Dash',
            style={'backgroundColor': colors['background'], 'textAlign': 'center',
                   'color': colors['text']
                   }),
    dcc.Dropdown(id='states-dropdown',
                 options=state_options,
                 value=[
                     'FL', 'NY', 'AZ', 'TX'],
                 multi=True
                 ),
    dcc.Tabs(id='tabs-example', children=[
        dcc.Tab(label='View 1', children=html.Div(
            children=[
                html.Div([
                    dcc.Graph(
                        id='tests-7day')
                ], style={'display': 'inline-block', 'width': '49%'}),
                html.Div([
                    dcc.Graph(
                        id='tests-7day_permil')
                ], style={'display': 'inline-block', 'width': '49%'}),
                html.Div([
                    dcc.Graph(
                        id='cases-7day')
                ], style={'display': 'inline-block', 'width': '49%', 'height': '24%'}),
                html.Div([
                    dcc.Graph(
                        id='cases-7day-permil')
                ], style={'display': 'inline-block', 'width': '49%', 'height': '24%'}),
                html.Div([
                    dcc.Graph(
                        id='cur_hosp-7day')
                ], style={'display': 'inline-block', 'width': '49%', 'height': '24%'}),
                html.Div([
                    dcc.Graph(
                        id='cur_hosp-7day_permil')
                ], style={'display': 'inline-block', 'width': '49%', 'height': '24%'}),
                html.Div([
                    dcc.Graph(
                        id='deaths-7day')
                ], style={'display': 'inline-block', 'width': '49%', 'height': '24%'}),
                html.Div([
                    dcc.Graph(
                        id='deaths-7day_permil')
                ], style={'display': 'inline-block', 'width': '49%', 'height': '24%'}),


            ])),
        dcc.Tab(label='View 2', children=html.Div([
            html.Div([
                dcc.Graph(
                    id='states_permil2-1')
            ], style={'height': '400'},),
            html.Div([
                dcc.Graph(
                    id='states_permil2-2')
            ]),
            html.Div([
                dcc.Graph(
                    id='states_permil2-3')
            ]),
        ])),
        dcc.Tab(label='View 3', children=html.Div([
            html.Div([
                dcc.Graph(
                    id='states_permil3-1')
            ]),
            html.Div([
                dcc.Graph(
                    id='states_permil3-2')
            ]),
            html.Div([
                dcc.Graph(
                    id='states_permil3-3')
            ]),
            html.Div([
                dcc.Graph(
                    id='states_permil3-4')
            ]),
        ])),
    ])
])


@app.callback(
    dash.dependencies.Output('states_permil2-1', 'figure'),
    [dash.dependencies.Input('states-dropdown', 'value')])
def update_output(value):
    df3 = df[df['state'].isin(value)]
    fig4 = px.line(df3,
                   x="date_val", y=['totalTestResultsIncrease_7day_permil', 'positiveIncrease_7day_permil'],
                   facet_col='state', facet_col_wrap=4,
                   width=800,
                   hover_name="state", title='Tests and Cases - per million', color='state')
    return fig4


@app.callback(
    dash.dependencies.Output('states_permil2-2', 'figure'),
    [dash.dependencies.Input('states-dropdown', 'value')])
def update_output(value):
    df3 = df[df['state'].isin(value)]
    fig4 = px.line(df3,
                   x="date_val", y=['hospitalizedCurrently_7day_permil', 'positiveIncrease_7day_permil'],
                   facet_col='state', facet_col_wrap=4,
                   width=800,
                   hover_name="state", title='Hosipitalized and Cases - per million', color='state')
    return fig4


@app.callback(
    dash.dependencies.Output('states_permil2-3', 'figure'),
    [dash.dependencies.Input('states-dropdown', 'value')])
def update_output(value):
    df3 = df[df['state'].isin(value)]
    fig4 = px.line(df3,
                   x="date_val", y=['hospitalizedCurrently_7day_permil', 'deathIncrease_7day_permil'],
                   facet_col='state', facet_col_wrap=4,
                   width=800,
                   hover_name="state", title='Hosipitalized and Deaths - per million', color='state')
    return fig4


@app.callback(
    dash.dependencies.Output('states_permil3-1', 'figure'),
    [dash.dependencies.Input('states-dropdown', 'value')])
def update_output(value):
    df3 = df[df['state'].isin(value)]
    fig4 = px.line(df3,
                   x="date_val", y='totalTestResultsIncrease_7day_permil',
                   facet_col='state', facet_col_wrap=4,
                   width=800,
                   hover_name="state", title='Tests - per million', color='state')
    return fig4


@app.callback(
    dash.dependencies.Output('states_permil3-2', 'figure'),
    [dash.dependencies.Input('states-dropdown', 'value')])
def update_output(value):
    df3 = df[df['state'].isin(value)]
    fig4 = px.line(df3,
                   x="date_val", y='positiveIncrease_7day_permil',
                   facet_col='state', facet_col_wrap=4,
                   width=800,
                   hover_name="state", title='Cases - per million', color='state')
    return fig4


@app.callback(
    dash.dependencies.Output('states_permil3-3', 'figure'),
    [dash.dependencies.Input('states-dropdown', 'value')])
def update_output(value):
    df3 = df[df['state'].isin(value)]
    fig4 = px.line(df3,
                   x="date_val", y='hospitalizedCurrently_7day_permil',
                   facet_col='state', facet_col_wrap=4,
                   width=800,
                   hover_name="state", title='Hospitalized - per million', color='state')
    return fig4


@app.callback(
    dash.dependencies.Output('states_permil3-4', 'figure'),
    [dash.dependencies.Input('states-dropdown', 'value')])
def update_output(value):
    df3 = df[df['state'].isin(value)]
    fig4 = px.line(df3,
                   x="date_val", y='deathIncrease_7day_permil',
                   facet_col='state', facet_col_wrap=4,
                   width=800,
                   hover_name="state", title='Deaths - per million', color='state')
    return fig4


@ app.callback(
    dash.dependencies.Output('cases-7day', 'figure'),
    [dash.dependencies.Input('states-dropdown', 'value')])
def update_output(value):
    df3 = df[df['state'].isin(value)]
    fig4 = px.line(df3,
                   x="date_val", y='positiveIncrease_7day',
                   hover_name="state", title='New Cases (7 day average)', color='state')
    return fig4


@ app.callback(
    dash.dependencies.Output('cases-7day-permil', 'figure'),
    [dash.dependencies.Input('states-dropdown', 'value')])
def update_output(value):
    df3 = df[df['state'].isin(value)]
    fig4 = px.line(df3, x="date_val", y='positiveIncrease_7day_permil',
                   hover_name="state", title='New Cases (7 day average per million people)', color='state')
    return fig4


@ app.callback(
    dash.dependencies.Output('tests-7day', 'figure'),
    [dash.dependencies.Input('states-dropdown', 'value')])
def update_output(value):
    df3 = df[df['state'].isin(value)]
    fig4 = px.line(df3, x="date_val", y='totalTestResultsIncrease_7day',
                   hover_name="state",
                   title='New Tests (7 day average)',
                   color='state')
    return fig4


@ app.callback(
    dash.dependencies.Output('tests-7day_permil', 'figure'),
    [dash.dependencies.Input('states-dropdown', 'value')])
def update_output(value):
    df3 = df[df['state'].isin(value)]
    fig4 = px.line(df3, x="date_val", y='totalTestResultsIncrease_7day_permil',
                   hover_name="state",
                   title='New Tests (7 day average  per million people)',
                   color='state')
    return fig4


@ app.callback(
    dash.dependencies.Output('cur_hosp-7day', 'figure'),
    [dash.dependencies.Input('states-dropdown', 'value')])
def update_output(value):
    df3 = df[df['state'].isin(value)]
    fig4 = px.line(df3, x="date_val", y='hospitalizedCurrently_7day',
                   hover_name="state",
                   title='Currently Hospitalized (7 day average)',
                   color='state')
    return fig4


@ app.callback(
    dash.dependencies.Output('cur_hosp-7day_permil', 'figure'),
    [dash.dependencies.Input('states-dropdown', 'value')])
def update_output(value):
    df3 = df[df['state'].isin(value)]
    fig4 = px.line(df3, x="date_val", y='hospitalizedCurrently_7day_permil',
                   hover_name="state",
                   title='Currently Hospitalized (7 day average per million people)',
                   color='state')
    return fig4


@ app.callback(
    dash.dependencies.Output('deaths-7day', 'figure'),
    [dash.dependencies.Input('states-dropdown', 'value')])
def update_output(value):
    df3 = df[df['state'].isin(value)]
    fig4 = px.line(df3, x="date_val", y='deathIncrease_7day',
                   hover_name="state",
                   title='Deaths (7 day average)',
                   color='state')
    return fig4


@ app.callback(
    dash.dependencies.Output('deaths-7day_permil', 'figure'),
    [dash.dependencies.Input('states-dropdown', 'value')])
def update_output(value):
    df3 = df[df['state'].isin(value)]
    fig4 = px.line(df3, x="date_val", y='deathIncrease_7day_permil',
                   hover_name="state",
                   title='Deaths (7 day average per million people)',
                   color='state')
    return fig4


if __name__ == '__main__':
    app.run_server(debug=True)
