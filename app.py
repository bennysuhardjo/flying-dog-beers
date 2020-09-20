import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd
import requests
import plotly.express as px
from dash.dependencies import Input, Output, State
import time


########### Define your variables
mytitle='Stock Trend'
tabtitle='Stock Trend'
myheading='Stock Trend'



#def generate_table(dataframe, max_rows=10):
#    return html.Table([
#        html.Thead(
#            html.Tr([html.Th(col) for col in dataframe.columns])
#        ),
#        html.Tbody([
#            html.Tr([
#                html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
#            ]) for i in range(min(len(dataframe), max_rows))
#        ])
#    ])



########### Initiate the app
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.title=tabtitle

########### Set up the layout
app.layout = html.Div(children=[
    html.H1(myheading),

    html.Label('US Stock Ticker: '),
    dcc.Input(id='stock_ticker', value='IBM', type='text'),
    html.Button(id='submit-button-state', n_clicks=0, children='Submit'),
    
    html.Table([
        html.Tr([html.Td(['Name:']), html.Td(id='name'), html.Td(['.                    Sector:']), html.Td(id='sector')]),

        html.Tr([html.Td(['Forward PE:']), html.Td(id='forwardpe'), html.Td(['.                    Analyst Target Price:']), html.Td(id='AnalystTargetPrice')]),
        html.Tr([html.Td(['Dividend Per Share:']), html.Td(id='DividendPerShare')]),
        html.Tr([html.Td(['Dividend Yield (%):']), html.Td(id='DividendYield')]),
        html.Tr([html.Td(['Ex-Dividend Date:']), html.Td(id='ExDividendDate')]),
        html.Tr([html.Td(['EPS:']), html.Td(id='EPS')]),
        html.Tr([html.Td(['52 Week High:']), html.Td(id='52WeekHigh')]),
        html.Tr([html.Td(['52 Week Low:']), html.Td(id='52WeekLow')]),
        html.Tr([html.Td(['50 Day Moving Average:']), html.Td(id='50DayMovingAverage')]),
        html.Tr([html.Td(['200 Day Moving Average:']), html.Td(id='200DayMovingAverage')])  

    ]),
    
    dcc.Graph(
        id='example-stock-1'
    ),
    #generate_table(df_mod_2020),
    ]
)

@app.callback(
    [Output('example-stock-1', 'figure'),
     Output('name', 'children'),
     Output('sector', 'children'),
     Output('forwardpe', 'children'),
     Output('AnalystTargetPrice', 'children'),
     Output('DividendPerShare', 'children'),
     Output('DividendYield', 'children'),
     Output('ExDividendDate', 'children'),
     Output('EPS', 'children'),
     Output('52WeekHigh', 'children'),
     Output('52WeekLow', 'children'),
     Output('50DayMovingAverage', 'children'),
     Output('200DayMovingAverage', 'children')

    
    
    
    ],
    [Input('submit-button-state', 'n_clicks')],
    [State('stock_ticker', 'value')]
)
def update_output_div(n_clicks, stock_tick):
    getStringRequest = "https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol="+stock_tick+"&outputsize=compact&apikey=L5W8DWNNL7QRMNH9"
    data =requests.get(getStringRequest).json()
    time.sleep(3)
    json_data = []

    for i in data['Time Series (Daily)']: 
        #print(i, data['Time Series (Daily)'][i]) 
        json_data.append( [i,data['Time Series (Daily)'][i]["1. open"],data['Time Series (Daily)'][i]["2. high"],
                         data['Time Series (Daily)'][i]["3. low"], data['Time Series (Daily)'][i]["4. close"],
                         data['Time Series (Daily)'][i]["5. adjusted close"],
                         data['Time Series (Daily)'][i]["6. volume"],
                         data['Time Series (Daily)'][i]["7. dividend amount"],
                         data['Time Series (Daily)'][i]["8. split coefficient"]]) 


    df_all = pd.DataFrame.from_records( json_data )

    df_mod = df_all.rename(columns={0: "Date", 1: "Open", 2: "High", 3: "Low", 4: "Close", 5: "Adj Close", 6: "Volume", 7: "Dividend", 8: "Split Coefficient"})

    df_mod_2020 = df_mod[df_mod['Date'].str[:4] == "2020"]

    figStock = go.Figure(data=[go.Candlestick(x=df_mod_2020["Date"],
                open=df_mod_2020["Open"],
                high=df_mod_2020["High"],
                low=df_mod_2020["Low"],
                close=df_mod_2020["Close"])])
    #figStock.update_layout(transition_duration=1000)

    
    getStringRequestOverview = "https://www.alphavantage.co/query?function=OVERVIEW&symbol="+stock_tick+"&apikey=L5W8DWNNL7QRMNH9"
    dataOverview =requests.get(getStringRequestOverview).json()

    try:
        return figStock, dataOverview['Name'], dataOverview['Sector'], dataOverview['ForwardPE'], dataOverview['AnalystTargetPrice'], dataOverview['DividendPerShare'], dataOverview['DividendYield'], dataOverview['ExDividendDate'], dataOverview['EPS'], dataOverview['52WeekHigh'], dataOverview['52WeekLow'], dataOverview['50DayMovingAverage'], dataOverview['200DayMovingAverage']
    
    except:
        return figStock, " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "
    else:
        return figStock, dataOverview['Name'], dataOverview['Sector'], dataOverview['ForwardPE'], dataOverview['AnalystTargetPrice'], dataOverview['DividendPerShare'], dataOverview['DividendYield'], dataOverview['ExDividendDate'], dataOverview['EPS'], dataOverview['52WeekHigh'], dataOverview['52WeekLow'], dataOverview['50DayMovingAverage'], dataOverview['200DayMovingAverage']


if __name__ == '__main__':
    app.run_server()
