import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server 

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}
URL = 'https://covidtracking.com/api/states/daily'
CTP_df = pd.read_json(URL, dtype={'date': 'int64'})
CTP_df['date_val'] =  pd.to_datetime(CTP_df['date'], format='%Y%m%d')

CTP_df.sort_values(['state', 'date'], inplace=True)
CTP_df['positiveIncrease_7day'] = CTP_df.groupby('state')['positiveIncrease'].rolling(7).mean().reset_index(0,drop=True)
CTP_df['totalTestResultsIncrease_7day'] = CTP_df.groupby('state')['totalTestResultsIncrease'].rolling(7).mean().reset_index(0,drop=True)
#CTP_df.sort_values(['date', 'state'], inplace=True)

census_pop = pd.read_csv('https://data.cdc.gov/api/views/b2jx-uyck/rows.csv',
                         names=['pop_year', 'state', 'state_name', 'TopicType', 'TopicDesc', 'DataSource', 'Data_Value_Type', 'Population', 'Gender', 'Age',
                                'GeoLocation', 'Source_File_USCB', 'Data_Pulled', 'LocationID', 'TopicTypeId', 'TopicId', 'MeasureId', 'StratificationID1',
                                'StratificationID2', 'SubMeasureID', 'DisplayOrder'],
                         usecols=['pop_year', 'state', 'state_name', 'Population', 'Gender', 'Age', 'GeoLocation'],
                         skiprows=1)
max_year = census_pop.pop_year.max()
census_pop_latest = census_pop[(census_pop.Gender == 'Total')    & 
                               (census_pop.Age == 'Total')       & 
                               (census_pop.pop_year == max_year)]

df = pd.merge(CTP_df, census_pop_latest[['pop_year', 'state', 'state_name', 'Population', 'GeoLocation']], on='state', how='outer')
cols_to_per_million = ['positive', 'negative', 'pending',
       'hospitalizedCurrently', 'hospitalizedCumulative', 'inIcuCurrently',
       'inIcuCumulative', 'onVentilatorCurrently', 'onVentilatorCumulative',
       'death', 'hospitalized',
       'totalTestsViral', 'positiveTestsViral', 'negativeTestsViral',
       'positiveCasesViral', 'positiveIncrease', 'negativeIncrease',
       'totalTestResults', 'totalTestResultsIncrease',
       'deathIncrease', 'hospitalizedIncrease']
for col in cols_to_per_million:
    df[col + '_permil'] = df[col] / (df['Population'] / 1000000)
df['positiveIncrease__permil_7day'] = df.groupby('state')['positiveIncrease_permil'].rolling(7).mean().reset_index(0,drop=True)
df['totalTestResultsIncrease_permil_7day'] = df.groupby('state')['totalTestResultsIncrease_permil'].rolling(7).mean().reset_index(0,drop=True)
df['state_name'].fillna('NassN')
# Setup Option values for each state in the dataset 
state_options = []
for index, row in df[['state', 'state_name']].drop_duplicates().fillna('NaN').iterrows():
    #print(row['state'], row['state_name'])
    if (row['state_name'] != 'NaN') :
        state_options.append({'label': row['state_name'], 'value': row['state']})
print(state_options)



df2 = df[df['state'].isin(['NY', 'CA', 'AZ', 'FL', 'TX'])]
print(df2.state.unique())
#print(df2[['state', 'date', 'totalTestReCovidDataPLaysultsIncrease_permil', 'positiveIncrease_permil']])
print(df2['totalTestResultsIncrease_7day'].max(), df2['positiveIncrease_7day'].max())
print(df2['totalTestResultsIncrease_permil'].max(), df2['positiveIncrease_permil'].max())
print(CTP_df['totalTestResultsIncrease_7day'].max(), CTP_df['positiveIncrease_7day'].max())
# fig = px.scatter(df2, x="totalTestResultsIncrease_7day", y="positiveIncrease_7day", 
#                  animation_frame="date", animation_group="state", hover_name="state", facet_col='state',
#                  color='state', size='Population', text='state', height=800,
#                  range_x=[0,100000], range_y=[0,10000])
CTP_df2 = CTP_df[CTP_df.state.isin(['NY', 'CA', 'AZ', 'FL', 'TX'])].copy()
print(CTP_df2.state.unique())

fig = px.scatter(CTP_df2, x="totalTestResultsIncrease_7day", y="positiveIncrease_7day", 
                 animation_frame="date", animation_group="state", hover_name="state",
                 color='state', text='state', height=400,
                 range_x=[0,120000], range_y=[0,10000])

fig2 = px.line(CTP_df2, x="totalTestResultsIncrease_7day", y="positiveIncrease_7day", 
                 hover_name="state",
                 color='state', height=800,
                 range_x=[0,120000], range_y=[0,10000])

fig3 = px.line(df2, x="date_val", y="positiveIncrease_7day", 
                 hover_name="state",
                 color='state', height=800,)

fig4 = px.line(df2, x="date_val", y="positiveIncrease__permil_7day", 
                 hover_name="state",
                 color='state', height=800,)

# fig = px.scatter(df[df['state'].isin(['NY', 'CA', 'FL', 'TX'])], 
#                  x="date", y="positiveIncrease_permil", 
#                 hover_name="state", color='state', size='Population')

fig.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = 250
# fig = px.bar(df, x="x", y=["SF", "Montreal"], barmode="group")
# fig.update_layout(plot_bgcolor= colors['background'], paper_bgcolor=colors['background'])

app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    html.H1(children='The Covid Tracking Project - in Dash',
    style={'textAlign': 'center',
                'color': colors['text']
    }),

    html.Div(children='''Dash
        Dash: A web application framework for Python.
    ''', style={'textAlign': 'center',
                'color': colors['text']
    }),        
    dcc.Input(id="states", type="text", placeholder="", debounce=True),
    html.Label('Multi-Select Dropdown'),
    dcc.Dropdown(
        id='states-dropdown',
        options=state_options,
        multi=True
    ),
    html.Div(id='states-container'),
    dcc.Graph(
        id='example-graph',
        figure=fig
    ),
    dcc.Graph(
        id='example-graph2',
        figure=fig2
    ),
    dcc.Graph(
        id='example-graph3',
        figure=fig3
    ),
    dcc.Graph(
        id='example-graph4',
        figure=fig4
    )
    
])

@app.callback(
    dash.dependencies.Output('example-graph4', 'figure'),
    [dash.dependencies.Input('states-dropdown', 'value')])
def update_output(value):
    print(value)
    df3 = df[df['state'].isin(value)]
    fig4 = px.line(df3, x="date_val", y="positiveIncrease__permil_7day", 
                 hover_name="state",
                 color='state', height=800,)

    return fig4

if __name__ == '__main__':
    app.run_server(debug=True)