import os
import dash
from dash import Dash, dcc, html,  Input, Output,  State
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import numpy as np


df = pd.read_excel(
    "assets/dashboard.xlsx",
)

totac=df.groupby('Date')['Outcome'].count()
totsuc=df[df['Outcome']=='Success'].groupby('Date')['Outcome'].count()
totnsuc=df[df['Outcome']=='Failure'].groupby('Date')['Outcome'].count()
#a
df1 = pd.DataFrame({'name': ['Total']*len(totac),
                    'Dates': totac.index,
                    'numbers': totac.values})

df2 = pd.DataFrame({'name': ['Success']*len(totsuc),
                    'Dates': totsuc.index,
                    'numbers': totsuc.values})
df3 = pd.DataFrame({'name': ['Failure']*len(totnsuc),
                    'Dates': totnsuc.index,
                    'numbers': totnsuc.values})

df4 = pd.DataFrame({'name': ['Ratio%']*len(totsuc),
                    'Dates': totsuc.index,
                    'numbers': totsuc.values*100/totac[totsuc.index]})


dft = pd.concat([df1, df2,df3, df4])

fig = px.line(dft, x = 'Dates', y = 'numbers', color = 'name', markers = True)

fig1a=px.line(totac, x = totac.index, y = 'Outcome')
fig1b=px.line(totsuc, x = totsuc.index, y = 'Outcome')
fig1c=px.line(totnsuc, x = totnsuc.index, y = "Outcome")
fig1d=px.line(totsuc, x = totsuc.index, y = totsuc.values*100/totac[totsuc.index])

# b
totac2=df.groupby('State')['Outcome'].count()
totsuc2=df[df['Outcome']=='Success'].groupby('State')['Outcome'].count()
totnsuc2=df[df['Outcome']=='Failure'].groupby('State')['Outcome'].count()


#f

def zero(time_period):
    if len(time_period)<=10:
        return "0"+time_period
    else:
        return time_period

df["Time_Period"] = df["Time_Period"].apply(zero)
totsucT=df[df['Outcome']=='Success'].groupby('Time_Period')['Outcome'].count()
totnsucT=df[df['Outcome']=='Failure'].groupby('Time_Period')['Outcome'].count()
totsucT=totsucT.sort_index()


#ploting
app = dash.Dash(__name__)
server = app.server



state_options = df["State"].unique()
state_options=np.insert(state_options, 0, "All")
time_options=df["Time_Period"].unique()
time_options=time_options
time_options=np.insert(time_options, 0, "All")
app.layout =html.Div( 
style={'background':'white', 'textAlign':'center',"width":"75%","display":"flex","align-items":"center", 'margin':"auto"},

   children=[ html.Div(
    [
        html.H1("Dynamic Graphs"), 
        html.H1("Calls Analytics"), 
        html.H3("a. We want to see this data in a graph with a time series legend. Then we want to see in the same graph the ratio of success /total calls as a function of date"),
        dcc.Dropdown([
            {'label': 'All', 'value': 'all'},
            {'label': 'Success', 'value': '1a'},
            {'label': 'Failure', 'value': '1b'},
            {'label': 'Time out', 'value': '1c'},
            {'label': 'Ratio', 'value': '1d'}],
            value='all',
            id="input1", ),
            dcc.Graph(id="output1"),
        html.H3("b-We want to see another graph that presents the success and failure by State in the form of a bar graph."),
        dcc.RadioItems(options=state_options,
            value="All",
            id="input2"),
        dcc.Graph(id="output2"),

        html.H3("c-We want to see a piechart that displays failure-success-timeout as a percentage"),
        dcc.DatePickerRange(
            id="date-picker",
            start_date=df.Date.min().date(),
            end_date=df.Date.max().date(),
            display_format="DD/MM/YYYY",
        ),
        dcc.Graph(id="output3"),


        html.H3("d-We want to see at the end which state was the most ' successful ' in share ratios."),
        dcc.DatePickerRange(
            id="input4",
            start_date=df.Date.min().date(),
            end_date=df.Date.max().date(),
            display_format="DD/MM/YYYY",
        ),
        html.H1(id="output4"),
        dcc.Graph(id="output4a"),



        html.H3("e-We also want to see a double piechart that displays the total number of actions/ State and number of success / state ."),
        dcc.DatePickerRange(
            id="input5",
            start_date=df.Date.min().date(),
            end_date=df.Date.max().date(),
            display_format="DD/MM/YYYY",
        ),
        dcc.Graph(id="output5"),


        html.H3("f-We want to know the number of succes by Time_Period (be careful with the ordering)"),
        dcc.Dropdown(options=time_options,
            value="All",
            id="input6"),
        dcc.Graph(id="output6")
              
        ],

   
    
)])

@app.callback(
    Output('output1', 'figure'),
    Input('input1', 'value')
)
def update_output(value):
    if value == "all":
        return fig

    if value == "1a":
        return fig1a

    if value == "1b":
        return fig1b

    if value == "1c":
        return fig1c

    if value == "1d":
        return fig1d

@app.callback(
    Output('output2', 'figure'),
    Input('input2', 'value')
)
def update_output(value):
    all=df[df['State']==value].groupby('State')['Outcome'].count()
    ts2=df[(df['Outcome']=='Success')&(df['State']==value)].groupby('State')['Outcome'].count()
    tns2=df[(df['Outcome']=='Failure')&(df['State']==value)].groupby('State')['Outcome'].count()
    figure = go.Figure(layout_yaxis_range=[0,30])

    if value=="All":
        figure.add_trace(trace=go.Bar(x=totsuc2.index, y=totsuc2.values, name="Success"), )
        figure.add_trace(trace=go.Bar(x=totnsuc2.index, y=totnsuc2.values, name="Failure"))
    else:     
        figure["layout"]["xaxis"]["title"] = "State"
        figure["layout"]["yaxis"]["title"] = "Number of calls"
        figure.add_trace(trace=go.Bar(
                    x=all.index,
                    y=all.values,
                    name="All",
                ))
        figure.add_trace(trace=go.Bar(
                    x=ts2.index,
                    y=ts2.values,
                    name="Success",
                ))
        figure.add_trace(trace=go.Bar(
                    x=tns2.index,
                    y=tns2.values,
                    name="Failure",
                ))
    return figure

      
@app.callback(
    Output('output3', 'figure'),
    [Input("date-picker", "start_date"), Input("date-picker", "end_date")],
)
def update_output(start_date, end_date):
    global df
    df1=df[(df.Date>=start_date)&(df.Date<=end_date)]
    all_together = df1.groupby("Outcome")["Outcome"].count()
    figure=go.Figure()
    figure.add_trace(
            trace=go.Pie(
                labels=all_together.index,
                values=all_together.values,
            ))

    return figure

@app.callback(
    Output('output4', 'children'),
     [Input("input4", "start_date"), Input("input4", "end_date")],
)
def update_output(start_date, end_date):
    global df
    df=df[(df.Date>=start_date)&(df.Date<=end_date)]
    all_together = df.groupby("State")["Outcome"].count()
    all_suc=df[df["Outcome"]=="Success"].groupby("State")["Outcome"].count()
    ratio= (all_suc / all_together * 100).sort_values(ascending=False)
    best=ratio.sort_values(ascending=False).index[0]
    return best

@app.callback(
    Output('output4a', 'figure'),
     [Input("input4", "start_date"), Input("input4", "end_date")],
)
def update_output(start_date, end_date):
    global df
    df=df[(df.Date>=start_date)&(df.Date<=end_date)]
    all_together = df.groupby("State")["Outcome"].count()
    all_suc=df[df["Outcome"]=="Success"].groupby("State")["Outcome"].count()
    ratio= (all_suc / all_together * 100).sort_values(ascending=False)
    figure=go.Figure()
    figure.add_trace(
            trace=go.Bar(
                x=ratio.index,
                y=ratio.values,
            ))

    return figure

@app.callback(
    Output('output5', 'figure'),
    [Input("input5", "start_date"), Input("input5", "end_date")],
)
def update_output(start_date, end_date):
    global df
    df=df[(df.Date>=start_date)&(df.Date<=end_date)]

    totac1 = df.groupby("State")["Outcome"].count()
    totsuc1 = df[df["Outcome"] == "Success"].groupby("State")["Outcome"].count()
    figure=go.Figure()
    figure.add_trace(
            go.Pie(
                labels=totac1.index,
                values=totac1.values,
                textinfo="none",
                name="total calls",
                hole=0.6,
            ),
        )

    figure.add_trace(
            go.Pie(
                labels=totsuc1.index,
                values=totsuc1.values,
                textinfo="none",
                name="success calls",
                hole=0.45,
            ),
        )

    figure.data[0].domain = {"x": [0, 1], "y": [1, 1]}
    figure.data[1].domain = {"x": [0, 1], "y": [0.22, 0.78]}
    figure.update_traces(hoverinfo="label+percent+name")


    return figure
        


@app.callback(
    Output('output6', 'figure'),
    Input('input6', 'value')
)
def update_output(value):
    # all=df[df['Time_Period']==value].groupby('Time_Period')['Outcome'].count()
    ts2=df[(df['Outcome']=='Success')&(df['Time_Period']==value)].groupby('Time_Period')['Outcome'].count()
    tns2=df[(df['Outcome']=='Failure')&(df['Time_Period']==value)].groupby('Time_Period')['Outcome'].count()
    figure = go.Figure(layout_yaxis_range=[0,45])
    figure["layout"]["xaxis"]["title"] = "Time Period"
    figure["layout"]["yaxis"]["title"] = "Number of calls"
    if value=="All":
        figure.add_trace(trace=go.Bar(x=totsucT.index, y=totsucT.values, name="Success"))
        # figure.add_trace(trace=go.Bar(x=totnsucT.index, y=totnsucT.values, name="Failure"))
    else:
        figure.add_trace(trace=go.Bar(
                    x=ts2.index,
                    y=ts2.values,
                    name="Success",
                ))
        figure.add_trace(trace=go.Bar(
                    x=tns2.index,
                    y=tns2.values,
                    name="Failure",
                ))
    return figure

if __name__ == "__main__":
    app.run_server("0.0.0.0", debug=False, port=int(
        os.environ.get('PORT', 8000)))
