import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_table
import pandas as pd
import plotly
import plotly.graph_objs as go
import plotly.express as px
import numpy as np
from dash.dependencies import Input, Output
pd.options.mode.chained_assignment = None  # default='warn'

pd.options.display.float_format = '{:,}'.format

confirmed = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv').groupby('Country/Region', as_index=False).sum()
death = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv').groupby('Country/Region', as_index=False).sum()
recovered = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv').groupby('Country/Region', as_index=False).sum()
reported_countries = len(confirmed['Country/Region'])

confirmed_daily = confirmed.drop(['Lat','Long'],1).transpose().reset_index()
confirmed_daily = pd.DataFrame(confirmed_daily.values[1:], columns=confirmed_daily.iloc[0,:])
confirmed_daily['Global'] = confirmed_daily.iloc[:,1:].sum(axis=1)
confirmed_daily = confirmed_daily.rename(columns={'Country/Region':'Date'})
death_daily = death.drop(['Lat','Long'],1).transpose().reset_index()
death_daily = pd.DataFrame(death_daily.values[1:], columns=death_daily.iloc[0,:])
death_daily['Global'] = death_daily.iloc[:,1:].sum(axis=1)
death_daily = death_daily.rename(columns={'Country/Region':'Date'})
recovered_daily = recovered.drop(['Lat','Long'],1).transpose().reset_index()
recovered_daily = pd.DataFrame(recovered_daily.values[1:], columns=recovered_daily.iloc[0,:])
recovered_daily['Global'] = recovered_daily.iloc[:,1:].sum(axis=1)
recovered_daily = recovered_daily.rename(columns={'Country/Region':'Date'})

table = confirmed[['Country/Region','Long','Lat']]
table['ConfirmedCases'] = confirmed.iloc[:,-1]
table['NewConfirmedCases'] = confirmed.iloc[:,-1] - confirmed.iloc[:,-2]
table['DeathCases'] = death.iloc[:,-1]
table['NewDeathCases'] = death.iloc[:,-1] - death.iloc[:,-2]
table['RecoveredCases'] = recovered.iloc[:,-1]
table['NewRecoveredCases'] = recovered.iloc[:,-1] - recovered.iloc[:,-2]
table = table.fillna(0)
table['ActiveCases'] = table['ConfirmedCases'] - table['DeathCases'] - table['RecoveredCases']
table['NewActiveCases'] = table['NewConfirmedCases'] - table['NewDeathCases'] - table['NewRecoveredCases']
table = table.sort_values(by='Country/Region')

active_total = table['ActiveCases'].sum()
active_new_total = table['NewActiveCases'].sum()
confirmed_total = table['ConfirmedCases'].sum()
confirmed_new_total = table['NewConfirmedCases'].sum()
death_total = table['DeathCases'].sum()
death_new_total = table['NewDeathCases'].sum()
recovered_total = table['RecoveredCases'].sum()
recovered_new_total = table['NewRecoveredCases'].sum()
death_rate = death_total/confirmed_total
recovered_rate = recovered_total/confirmed_total
summary_total = {'Cases':['Active','Confirmed','Death','Recovered'],'Total':[f'{active_total:,}',f'{confirmed_total:,}',f'{death_total:,}',f'{recovered_total:,}'],'New':[f'{active_new_total:,}',f'{confirmed_new_total:,}',f'{death_new_total:,}',f'{recovered_new_total:,}']}
summary_total = pd.DataFrame(summary_total, columns = ['Cases','Total','New'])

confirmed_table = table[['ConfirmedCases','Country/Region']].groupby('Country/Region', as_index=False).agg({"ConfirmedCases": "sum"})
death_table = table[['DeathCases','Country/Region']].groupby('Country/Region', as_index=False).agg({"DeathCases": "sum"})
recovered_table = table[['RecoveredCases','Country/Region']].groupby('Country/Region', as_index=False).agg({"RecoveredCases": "sum"})

c_fig = px.scatter_mapbox(table, lat="Lat", lon="Long", hover_name="Country/Region", hover_data=["ConfirmedCases"],
                        zoom=0.8, width=900, height=600, color="ConfirmedCases", size="ConfirmedCases", size_max=50, title="Global Distribution Map")
c_fig = c_fig.update_layout(mapbox_style="open-street-map")

d_fig = px.scatter_mapbox(table, lat="Lat", lon="Long", hover_name="Country/Region", hover_data=["DeathCases"],
                        zoom=0.8, width=900, height=600, color="DeathCases", size="DeathCases", size_max=50, title="Global Distribution Map")
d_fig = d_fig.update_layout(mapbox_style="open-street-map")

r_fig = px.scatter_mapbox(table, lat="Lat", lon="Long", hover_name="Country/Region", hover_data=["RecoveredCases"],
                        zoom=0.8, width=900, height=600, color="RecoveredCases", size="RecoveredCases", size_max=50, title="Global Distribution Map")
r_fig = r_fig.update_layout(mapbox_style="open-street-map")

a = pd.melt(confirmed_daily, id_vars='Date')
a['Cases'] = 'Confirmed'
b = pd.melt(death_daily, id_vars='Date')
b['Cases'] = 'Death'
c = pd.melt(recovered_daily, id_vars='Date')
c['Cases'] = 'Recovered'
daily = [a,b,c]
daily = pd.concat(daily)
daily['Date'] = pd.to_datetime(daily['Date'])
daily.columns = ['Date','Country/Region','NumberOfCases','Category']
daily['NumberOfCases'] = daily['NumberOfCases'].astype(int)
daily['NewCases'] = (daily['NumberOfCases'] - daily['NumberOfCases'].shift(1)).fillna(method='bfill')

# def cum_cases(country):
#     dfc = daily[daily['Country/Region'] == country]
#     fig = px.line(dfc, x="Date", y='NumberOfCases', color='Category', title=country+' Cumulative Cases')
#     return fig.show()
# def new_cases(country):
#     dfc = daily[daily['Country/Region'] == country]
#     dfc = dfc[dfc['Category'] == 'Confirmed']
#     fig = px.bar(dfc, x="Date", y='NewCases', title=country+' New Cases')
#     return fig.show()

dfc = daily[daily['Country/Region'] == 'Global']
dfc_fig = px.line(dfc, x="Date", y='NumberOfCases', color='Category', title='Global Cumulative Cases', width=400, height=350,)
dfn = dfc[dfc['Category'] == 'Confirmed']
dfn_fig = px.bar(dfn, x="Date", y='NewCases', title='Global New Cases', width=400, height=350,)

external_stylesheets =['https://codepen.io/chriddyp/pen/bWLwgP.css', dbc.themes.BOOTSTRAP]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

card = dbc.CardDeck([
    dbc.Card(html.Center([
        dbc.CardBody([
            html.H4(f'{active_total:,}', className="card-title"),
            html.P("Global Active Cases", className="card-text"),
        ]),
        dbc.CardFooter(["Changed ", f'{active_new_total:,}', " compared to yesterday"])
    ])),
    dbc.Card(html.Center([
        dbc.CardBody([
            html.H4(f'{confirmed_total:,}', className="card-title"),
            html.P("Global Confirmed Cases", className="card-text"),
        ]),
        dbc.CardFooter(["Changed ", f'{confirmed_new_total:,}', " compared to yesterday"])
    ])),
    dbc.Card(html.Center([
        dbc.CardBody([
            html.H4(f'{death_total:,}', className="card-title"),
            html.P("Global Death Cases", className="card-text"),
        ]),
        dbc.CardFooter(["Changed ", f'{death_new_total:,}', " compared to yesterday"])
    ])),
    dbc.Card(html.Center([
        dbc.CardBody([
            html.H4(f'{recovered_total:,}', className="card-title"),
            html.P("Global Recovered Cases", className="card-text"),
        ]),
        dbc.CardFooter(["Changed ", f'{recovered_new_total:,}', " compared to yesterday"])
    ]))
])

def table(df):
    return dash_table.DataTable(
        data=df.to_dict('records'),
        columns=[{'id': c, 'name': c} for c in df.columns],
        fixed_rows={'headers': True},
        style_table={'height': 500, 'fontSize': 16},
        style_cell_conditional=[
            {'if': {'column_id': 'Country/Region'},
            'width': '70%'},
        ],
        style_as_list_view=True,
    )

notes = html.P(
    'Data sources: COVID-19 Data Repository by the Center for Systems Science and Engineering (CSSE), Johns Hopkins University available at here'
    ), html.P(
        'Do incididunt sint Lorem mollit exercitation nisi consectetur adipisicing Lorem duis mollit occaecat est consequat. Eiusmod ex qui labore exercitation in reprehenderit fugiat nulla occaecat. Exercitation amet laborum magna reprehenderit nostrud ipsum laborum ullamco aliquip duis cillum minim.'
    )

app.layout = html.Div([
    dbc.Row(dbc.Col(html.Div(html.Center(html.H1("Corona Virus Disease 2019 Outbreak"))))),
    dbc.Row(dbc.Col(card, width=10), justify='center'),
    dbc.Row([
        dbc.Col(html.Div([
            html.Div(dbc.Row(dbc.Col([
                dcc.Tabs(id='tabs', value='tab-1', children=[
                    dcc.Tab(label='Confirmed', value='tab-1'),
                    dcc.Tab(label='Death', value='tab-2'),
                    dcc.Tab(label='Recovered', value='tab-3'),
                ]),
            ])), style={'marginTop': 25}),
            html.Div(dbc.Row(dbc.Col(id='tabs-content', align='right'), justify='center'), style={'marginBottom': 25}),
            dbc.Row(
                dbc.CardGroup([
                    dbc.Card(
                        dbc.CardBody(html.Center([
                            html.H4(reported_countries, className="card-title"),
                            html.P("Countries/Regions", className="card-text"),
                        ])),
                    ),
                    dbc.Card(
                        dbc.CardBody(html.Center([
                            html.H4([round(death_rate*100,2),'%'], className="card-title"),
                            html.P("Death Rate", className="card-text"),
                        ])),
                    ),
                    dbc.Card(
                        dbc.CardBody(html.Center([
                            html.H4([round(recovered_rate*100,2),'%'], className="card-title"),
                            html.P("Recovered Rate", className="card-text"),
                        ])),
                    ),
                ]), justify='center'
            ),
        ]),width=3),
        dbc.Col([
            dbc.Row(id='graphs-content'),
            dbc.Row(dbc.Col(notes), justify='center')
        ], width=6),
        dbc.Col(html.Div([
            dbc.Row(dcc.Graph(figure=dfc_fig)),
            dbc.Row(dcc.Graph(figure=dfn_fig)),
        ],
        ), width=3)
    ]),
])

@app.callback(Output('tabs-content', 'children'),
              [Input('tabs', 'value')])
def render_content(tab):
    if tab == 'tab-1':
        return html.Div(
                table(confirmed_table)
            ),
    elif tab == 'tab-2':
        return html.Div(
                table(death_table),
            ),
    elif tab == 'tab-3':
        return html.Div(
                table(recovered_table),
            )

@app.callback(Output('graphs-content', 'children'),
              [Input('tabs', 'value')])
def render_content(tab):
    if tab == 'tab-1':
        return html.Div(
            dcc.Graph(figure=c_fig)
            ),
    elif tab == 'tab-2':
        return html.Div(
            dcc.Graph(figure=d_fig)
            ),
    elif tab == 'tab-3':
        return html.Div(
            dcc.Graph(figure=r_fig)
            ),

if __name__ == '__main__':
    app.run_server(debug=True)
