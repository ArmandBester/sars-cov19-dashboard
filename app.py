import plotly.express as px
#from jupyter_dash import JupyterDash
import dash
import flask
import dash_core_components as dcc
import dash_html_components as html
#import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import pandas as pd
import numpy as np
import scipy
from scipy import signal
import plotly.graph_objects as go


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

#source:
# https://github.com/CSSEGISandData/COVID-19.git

default = ['South Africa', 'United Kingdom', 'Germany', 'Italy']

source = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv"

mkdwn = open('README.md').read()





def data_prep():

    df = pd.read_csv(source)

    countries = df['Country/Region'].unique()

    df.drop(['Province/State', 'Lat', 'Long'], inplace=True, axis=1)
    df = df.melt(id_vars=['Country/Region'], value_name='Confirmed', var_name='Date')
    df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%y')
    df = df.groupby(['Country/Region', 'Date']).sum().reset_index()

    df = df[df['Confirmed'] >= 1]
    df
    df.sort_values(by=['Country/Region', 'Date'], inplace=True)

    newDf = pd.DataFrame()
    for c in countries:
        tmp = df[df['Country/Region'] == c]
        dateList = []
        for i in np.arange(0, tmp.shape[0], 1):
            dateList.append((tmp.iloc[i, 1] - tmp.iloc[0, 1]).days)
        tmp['DaysFromFirstConf'] = dateList
        tmp['DailyNewConf'] = tmp['Confirmed'].diff()

        newDf = newDf.append(tmp)
    #placesDict = [{'label': k, 'value': k} for k in countries]
    return newDf, countries

# prep the data
newDf, countries, = data_prep()


# create some colours
colors = px.colors.qualitative.Bold
# Build App
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = 'COVID19 dash'
server = app.server


## Layout
#####################################################################################
app.layout = html.Div(children=[
    dcc.Tabs([
        dcc.Tab(label='Graphics', children=[

            html.H3(children='COVID-19 rates',
                style={'textAlign': 'center'}),

            html.H5('Countries:'),

            dcc.Dropdown(
                id='selection',
                options=[{'label': v, 'value': v} for v in countries],
                value=default,
                multi=True
            ),                       

            html.Div([
                html.H6('Choose polyorder:'),
                dcc.Slider(
                    id='poly-slider',
                    min=1,
                    max=10,
                    step=1,
                    value=3,
                    dots=True,
                    marks=dict((i, str(i)) for i in range(1,11,1))
                ),
            

                html.Br(),                

                ## Daily New
                dcc.Graph(id='Daily_new'),
                
                ],style= {'width': '49%', 'display': 'inline-block'}),
            
            html.Div([
                html.H6('Choose window:'),
                dcc.Slider(
                    id='window-slider',
                    min=7,
                    max=31,
                    step=2,
                    value=21,
                    dots=True,
                    marks=dict((i, str(i)) for i in range(7,33,2))
                ),

                html.Br(),

                ## Derivative
                dcc.Graph(id='d1')
            ],style= {'width': '49%', 'display': 'inline-block'}),    
            

            html.Div([
            ## Cumulative
                dcc.Graph(id='cumulative')
            ],style= {'width': '49%', 'display': 'inline-block'}),        

            html.Br()
        ]),

        dcc.Tab(label='About', children=[
            html.Div([
                dcc.Markdown(mkdwn)
                ], style={'marginLeft': 300, 'marginRight': 300, 
                'marginTop': 10, 'marginBottom': 10})
        ])

    ])
])



### Callbacks   ###

# Sliders
#####################################################################################




# Daily new
#####################################################################################
@app.callback(
    Output('Daily_new', 'figure'),
    [Input('selection', 'value'),
    Input('poly-slider', 'value'),
    Input('window-slider', 'value')])

def update_new(default, polyOrder, window_length):
    keep = default
    fig_new = go.Figure()
    i = 0
    for c in keep:
        tmp = newDf[newDf['Country/Region'] == c]
        fig_new.add_trace(go.Scatter(
            x=tmp['DaysFromFirstConf'],
            y=tmp['DailyNewConf'],
            mode='lines+markers',
            marker=dict(size=3, color=colors[i]),
            line = dict(dash='dot'),
            hovertext=tmp['Date'].dt.date,
            name=c
        ))

        fig_new.add_trace(go.Scatter(
            x=tmp['DaysFromFirstConf'],
            y=signal.savgol_filter(tmp['DailyNewConf'],
                                  window_length = window_length,
                                  polyorder=polyOrder, deriv=0),
            mode='lines',
            opacity=0.7,
            marker=dict(size=5, color=colors[i]),
            hovertext=tmp['Date'].dt.date,
            name=c
        ))
        i += 1

    fig_new.update_layout(template="plotly_white",
                      title="New COVID-19 cases",
                      yaxis_title="Daily new",
                      xaxis_title="Days from first")
    return fig_new


#Delta change
#####################################################################################
@app.callback(
    Output('d1', 'figure'),
    [Input('selection', 'value'),
    Input('poly-slider', 'value'),
    Input('window-slider', 'value')])

def update_d1(default, polyOrder, window_length):
    keep = default
    fig_d1 = go.Figure()
    i = 0
    for c in keep:
        tmp = newDf[newDf['Country/Region'] == c]
        fig_d1.add_trace(go.Scatter(
            x=tmp['DaysFromFirstConf'],
            y=signal.savgol_filter(tmp['DailyNewConf'],
                                  window_length = window_length,
                                  polyorder=polyOrder, deriv=1),
            mode='lines+markers',
            opacity=0.7,
            marker=dict(size=5, color=colors[i]),
            hovertext=tmp['Date'].dt.date,
            name=c
        ))
        i += 1

    fig_d1.update_layout(template="plotly_white",
                      title="First derivative of new COVID-19 cases",
                      yaxis_title="Change in new cases",
                      xaxis_title="Days from first")

    return fig_d1

# Cumulative figure
#####################################################################################
@app.callback(
    Output('cumulative', 'figure'),
    [Input('selection', 'value')])

def update_cum(default):
    keep = default
    fig_cum = go.Figure()
    i = 0
    for c in keep:
        tmp = newDf[newDf['Country/Region'] == c]
        fig_cum.add_trace(go.Scatter(
            x=tmp['DaysFromFirstConf'],
            y=tmp['Confirmed'],
            mode='lines',
            marker=dict(size=5, color=colors[i]),
            hovertext=tmp['Date'].dt.date,
            name=c
        ))
        i += 1

    fig_cum.update_layout(yaxis_type="log",
                      template="plotly_white",
                      title="Cumulative COVID-19 cases",
                      yaxis_title="Cumulative cases",
                      xaxis_title="Days from first")
    return fig_cum

if __name__ == '__main__':
    app.run_server(debug=True)
