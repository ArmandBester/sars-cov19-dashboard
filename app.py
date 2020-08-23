import plotly.express as px
#from jupyter_dash import JupyterDash
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import numpy as np
import scipy
from scipy import signal
import plotly.graph_objects as go


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

#source:
# https://github.com/CSSEGISandData/COVID-19.git

default = ['South Africa', 'United Kingdom', 'Germany', 'Singapore', 'Australia', 'Italy',
        'Japan', 'Sweden', 'New Zealand', "Afghanistan"]

source = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv"

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

# create soem colours
colors = px.colors.qualitative.Bold

# Build App

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

#####################################################################################
## Layout
app.layout = html.Div(children=[

    html.H1(children='COVID-19 rates in countries',
           style={'textAlign': 'center'}),

    html.Label('Countrie(s)'),

    dcc.Dropdown(
        id='selection',
        options=[{'label': v, 'value': v} for v in countries],
        value=default,
        multi=True
    ),

    # Output figures
    ## Cumulative
    dcc.Graph(id='cumulative'),
    ## Daily New
    dcc.Graph(id='Daily_new'),
    ## Delivative
    dcc.Graph(id='d1'),

    html.Br()
])

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
                      xaxis_title="Days from first",
                      width=1050,
                      height=600)
    return fig_cum


# Daily new
#####################################################################################
@app.callback(
    Output('Daily_new', 'figure'),
    [Input('selection', 'value')])

def update_new(default):
    keep = default
    fig_new = go.Figure()
    i = 0
    for c in keep:
        tmp = newDf[newDf['Country/Region'] == c]
        fig_new.add_trace(go.Scatter(
            x=tmp['DaysFromFirstConf'],
            y=tmp['DailyNewConf'],
            mode='lines+markers',
            marker=dict(size=5, color=colors[i]),
            line = dict(dash='dot'),
            hovertext=tmp['Date'].dt.date,
            name=c
        ))

        fig_new.add_trace(go.Scatter(
            x=tmp['DaysFromFirstConf'],
            y=signal.savgol_filter(tmp['DailyNewConf'],
                                  window_length = 21,
                                  polyorder=2, deriv=0),
            mode='lines',
            opacity=0.7,
            marker=dict(size=5, color=colors[i]),
            hovertext=tmp['Date'].dt.date,
            name=f'{c} smoothed'
        ))
        i += 1

    fig_new.update_layout(template="plotly_white",
                      title="New COVID-19 cases",
                      yaxis_title="Daily new",
                      xaxis_title="Days from first",
                      width=1050,
                      height=600)
    return fig_new


#Delta change
#####################################################################################
@app.callback(
    Output('d1', 'figure'),
    [Input('selection', 'value')])

def update_d1(default):
    keep = default
    fig_d1 = go.Figure()
    i = 0
    for c in keep:
        tmp = newDf[newDf['Country/Region'] == c]
        fig_d1.add_trace(go.Scatter(
            x=tmp['DaysFromFirstConf'],
            y=signal.savgol_filter(tmp['DailyNewConf'],
                                  window_length = 21,
                                  polyorder=2, deriv=1),
            mode='lines+markers',
            opacity=0.7,
            marker=dict(size=5, color=colors[i]),
            hovertext=tmp['Date'].dt.date,
            name=f'{c} delta cases'
        ))
        i += 1

    fig_d1.update_layout(template="plotly_white",
                      title="First derivative of new COVID-19 cases",
                      yaxis_title="Change in new cases",
                      xaxis_title="Days from first",
                      width=1050,
                      height=600)

    return fig_d1

if __name__ == '__main__':
    app.run_server(debug=True)
