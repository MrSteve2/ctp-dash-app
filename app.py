import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from plotly.subplots import make_subplots

large_rockwell_template = dict(
    layout=go.Layout(title_font=dict(family="Rockwell", size=24))
)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

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

# Setup Option values for each state in the dataset
state_options = []
for index, row in df[['state', 'state_name']].drop_duplicates().fillna('NaN').iterrows():
    #print(row['state'], row['state_name'])
    if (row['state_name'] != 'NaN'):
        state_options.append(
            {'label': row['state_name'], 'value': row['state']})
print(state_options)

app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    html.H1(children='The Covid Tracking Project - in Dash',
            style={'textAlign': 'center',
                   'color': colors['text']
                   }),

    html.Div(children='''Dash: A web application framework for Python.
    ''', style={'textAlign': 'center',
                'color': colors['text']
                }),
    html.Label('Multi-Select Dropdown'),
    dcc.Dropdown(id='states-dropdown',
                 options=state_options,
                 value=['FL'],  # ,'CT', 'AZ', 'TX'],
                 multi=True
                 ),

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


])


@app.callback(
    dash.dependencies.Output('cases-7day', 'figure'),
    [dash.dependencies.Input('states-dropdown', 'value')])
def update_output(value):
    print(value)
    df3 = df[df['state'].isin(value)]
    fig4 = px.line(df3, x="date_val", y='positiveIncrease_7day',
                   hover_name="state", title='New Cases (7 day average)', color='state')
    return fig4


@app.callback(
    dash.dependencies.Output('cases-7day-permil', 'figure'),
    [dash.dependencies.Input('states-dropdown', 'value')])
def update_output(value):
    print(value)
    # print(yDropdown)
    df3 = df[df['state'].isin(value)]
    fig4 = px.line(df3, x="date_val", y='positiveIncrease_7day_permil',
                   hover_name="state", title='New Cases (7 day average per million people)', color='state')
    return fig4


@app.callback(
    dash.dependencies.Output('tests-7day', 'figure'),
    [dash.dependencies.Input('states-dropdown', 'value')])
def update_output(value):
    print(value)
    df3 = df[df['state'].isin(value)]
    fig4 = px.line(df3, x="date_val", y='totalTestResultsIncrease_7day',
                   hover_name="state",
                   title='New Tests (7 day average)',
                   color='state')
    return fig4


@app.callback(
    dash.dependencies.Output('tests-7day_permil', 'figure'),
    [dash.dependencies.Input('states-dropdown', 'value')])
def update_output(value):
    print(value)
    df3 = df[df['state'].isin(value)]
    fig4 = px.line(df3, x="date_val", y='positive',
                   hover_name="state",
                   title='New Tests (7 day average)',
                   color='state')
    return fig4


@app.callback(
    dash.dependencies.Output('cur_hosp-7day', 'figure'),
    [dash.dependencies.Input('states-dropdown', 'value')])
def update_output(value):
    print(value)
    df3 = df[df['state'].isin(value)]
    fig4 = px.line(df3, x="date_val", y='hospitalizedCurrently_7day',
                   hover_name="state",
                   title='Currently Hospitalized (7 day average)',
                   color='state')
    return fig4


@app.callback(
    dash.dependencies.Output('cur_hosp-7day_permil', 'figure'),
    [dash.dependencies.Input('states-dropdown', 'value')])
def update_output(value):
    print(value)
    df3 = df[df['state'].isin(value)]
    fig4 = px.line(df3, x="date_val", y='hospitalizedCurrently_7day_permil',
                   hover_name="state",
                   title='Currently Hospitalized (7 day average per million people)',
                   color='state')
    return fig4


@app.callback(
    dash.dependencies.Output('deaths-7day', 'figure'),
    [dash.dependencies.Input('states-dropdown', 'value')])
def update_output(value):
    print(value)
    df3 = df[df['state'].isin(value)]
    fig4 = px.line(df3, x="date_val", y='deathIncrease_7day',
                   hover_name="state",
                   title='Deaths (7 day average)',
                   color='state')
    return fig4


@app.callback(
    dash.dependencies.Output('deaths-7day_permil', 'figure'),
    [dash.dependencies.Input('states-dropdown', 'value')])
def update_output(value):
    print(value)
    df3 = df[df['state'].isin(value)]
    fig4 = px.line(df3, x="date_val", y='deathIncrease_7day_permil',
                   hover_name="state",
                   title='Deaths (7 day average per million people)',
                   color='state')
    return fig4


if __name__ == '__main__':
    app.run_server(debug=True)
