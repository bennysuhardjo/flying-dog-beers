import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd
import requests
import plotly.express as px
from dash.dependencies import Input, Output, State
import time
import dash_table
import zipfile, urllib.request, shutil
import dash_bootstrap_components as dbc

########### Define your variables
mytitle='Stock Trend'
tabtitle='Stock Trend'
myheading='Stock Trend'



def generate_table(dataframe, max_rows=10):
    return html.Table([
        html.Thead(
            html.Tr([html.Th(col) for col in dataframe.columns])
        ),
        html.Tbody([
            html.Tr([
                html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
            ]) for i in range(min(len(dataframe), max_rows))
        ])
    ])

headers = {'AccountKey': '/cwI6AoOQzefPZARL5M4Eg==',
           'accept': 'application/json'
}

results = []

#while True:
#     new_results = requests.get(
#         "http://datamall2.mytransport.sg/ltaodataservice/BusRoutes",
#         headers=headers,
#         params={'$skip': len(results)}
#     ).json()['value']
#     if new_results == []:
#         break
#     else:
#         results += new_results



results =requests.get("http://datamall2.mytransport.sg/ltaodataservice/BusRoutes", headers=headers).json()['value']


json_data = []

#data['value']

for i in results: 
    #print(i, i["BusStopCode"]) 
    json_data.append( [i["ServiceNo"],i["Operator"],
                       i["Direction"],i["StopSequence"],
                       i["BusStopCode"],i["Distance"],
                       i["WD_FirstBus"],i["WD_LastBus"],
                       i["SAT_FirstBus"],i["SAT_LastBus"],
                       i["SUN_FirstBus"],i["SUN_LastBus"]

                      
                      
                      ]) 


df_busRoute = pd.DataFrame.from_records( json_data ).rename(columns={0: "ServiceNo", 1: "Operator", 2: "Direction", 3: "StopSequence", 4: "BusStopCode"
                                                                     , 5: "Distance", 6: "WD_FirstBus", 7: "WD_LastBus", 8: "SAT_FirstBus", 9: "SAT_LastBus"
                                                                    , 10: "SUN_FirstBus", 11: "SUN_LastBus"})


headers = {'AccountKey': 'NQD/ZccwR5SEDj/MehpKww== ',
           'accept': 'application/json'
}
# MPHd2F+USH+1hA1FDikGeA==
# NQD/ZccwR5SEDj/MehpKww== 

r =requests.get("http://datamall2.mytransport.sg/ltaodataservice/PV/Bus", headers=headers).json()


url = r['value'][0]['Link']
file_name = 'myzip.zip'

with urllib.request.urlopen(url) as response, open(file_name, 'wb') as out_file:
    shutil.copyfileobj(response, out_file)
    with zipfile.ZipFile(file_name) as zf:
        zf.extractall()
df_busStopStats = pd.read_csv(file_name)
df_busStopStatsSummary = df_busStopStats.groupby(['DAY_TYPE','TIME_PER_HOUR'], as_index=False)[["TOTAL_TAP_IN_VOLUME"]].sum()

fig = go.Figure(data=go.Heatmap(
                   z=df_busStopStatsSummary['TOTAL_TAP_IN_VOLUME'],
                   x=df_busStopStatsSummary['TIME_PER_HOUR'],
                  y=df_busStopStatsSummary['DAY_TYPE'],
                   hoverongaps = False))
fig.update_layout(
    title="Tap-In Volume (Bus) by Hours of the Day"
)



########### Initiate the app
external_stylesheets = [dbc.themes.BOOTSTRAP]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.title=tabtitle

########### Set up the layout
app.layout = html.Div([
    dcc.Tabs([
        dcc.Tab(label='Financial Market', children=[
            

            html.Label('US Stock Ticker: '),
            dcc.Input(id='stock_ticker', value='IBM', type='text'),
            html.Button(id='submit-button-state', n_clicks=0, children='Submit'),

            html.Table([
                html.Tr([html.Td(['Name:']), html.Td(id='name'), html.Td(['|Sector:']), html.Td(id='sector')]),
                html.Tr([html.Td(['Forward PE:']), html.Td(id='forwardpe'), html.Td(['|Analyst Target Price ($):']), html.Td(id='AnalystTargetPrice')]),
                html.Tr([html.Td(['Dividend Per Share ($):']), html.Td(id='DividendPerShare'), html.Td(['|Dividend Yield (%):']), html.Td(id='DividendYield')]),
                html.Tr([html.Td(['Ex-Dividend Date:']), html.Td(id='ExDividendDate'), html.Td(['|EPS ($):']), html.Td(id='EPS')]),
                html.Tr([html.Td(['52-Week High ($):']), html.Td(id='52WeekHigh'), html.Td(['|52-Week Low ($):']), html.Td(id='52WeekLow')]),
                html.Tr([html.Td(['50-Day Moving Average ($):']), html.Td(id='50DayMovingAverage'), html.Td(['|200-Day Moving Average ($):']), html.Td(id='200DayMovingAverage')])
                

            ]),

            dcc.Graph(
                id='example-stock-1'
            ),
	    html.Label('News: '),
            html.Table([
                html.Tr([html.Td(['']), html.Td(id='news1')]),  
		html.Tr([html.Td(['']), html.Td(id='news2')]), 
		html.Tr([html.Td(['']), html.Td(id='news3')]), 
		html.Tr([html.Td(['']), html.Td(id='news4')]), 
		html.Tr([html.Td(['']), html.Td(id='news5')]),            

            ])
       ]),
       dcc.Tab(label='Public Transport', children=[
            dbc.Row([
            		dbc.Col(
	    			dcc.Graph(
                			figure={
                    				'data': [{'x': df_busRoute['Operator'],
                    		 			  'type': 'histogram'},
                    					],
						'layout': {'title': 'No of Buses by Operators'}
                			}
            			), width=4
			),
	    		dbc.Col(
	    			dcc.Graph(
                			figure=fig
            			), width=8)
	    	])
        ]),
        dcc.Tab(label='Banking', children=[
            dcc.Graph(
                figure={
                    'data': [
                        {'x': [1, 2, 3], 'y': [2, 4, 3],
                            'type': 'bar', 'name': 'SF'},
                        {'x': [1, 2, 3], 'y': [5, 4, 3],
                         'type': 'bar', 'name': u'Montréal'},
                    ]
                }
            )
        ])
    ])

])

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
     Output('200DayMovingAverage', 'children'),
     Output('news1','children'),
     Output('news2','children'),
     Output('news3','children'),
     Output('news4','children'),
     Output('news5','children'),
    
    
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
    figStock.update_xaxes(
        rangebreaks=[
            dict(bounds=["sat", "mon"]), #hide weekends
            dict(values=["2015-12-25", "2016-01-01"])  # hide Christmas and New Year's
        ]
    )
    
    getStringRequestOverview = "https://www.alphavantage.co/query?function=OVERVIEW&symbol="+stock_tick+"&apikey=L5W8DWNNL7QRMNH9"
    dataOverview =requests.get(getStringRequestOverview).json()

    json_data = []
    getStringNews = "https://newsapi.org/v2/everything?q="+stock_tick+"&apiKey=e8fc661fec95488d884a597bbed80481"
    news = requests.get(getStringNews).json()
    for i in news['articles']: 
    	json_data.append( [i['publishedAt'] + ": " + i['title']]) 

    
    dfNews = pd.DataFrame.from_records( json_data )
    dfNews_mod = dfNews.rename(columns={0: "NewsTitle"}).sort_values(by=['NewsTitle'],ascending=False)

    
    
    try:
        return figStock, dataOverview['Name'], dataOverview['Sector'], dataOverview['ForwardPE'], dataOverview['AnalystTargetPrice'], dataOverview['DividendPerShare'], dataOverview['DividendYield'], dataOverview['ExDividendDate'], dataOverview['EPS'], dataOverview['52WeekHigh'], dataOverview['52WeekLow'], dataOverview['50DayMovingAverage'], dataOverview['200DayMovingAverage'], dfNews_mod.iloc[0]['NewsTitle'], dfNews_mod.iloc[1]['NewsTitle'], dfNews_mod.iloc[2]['NewsTitle'], dfNews_mod.iloc[3]['NewsTitle'], dfNews_mod.iloc[4]['NewsTitle']

    
    except:
        return figStock, " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "
    else:
        return figStock, dataOverview['Name'], dataOverview['Sector'], dataOverview['ForwardPE'], dataOverview['AnalystTargetPrice'], dataOverview['DividendPerShare'], dataOverview['DividendYield'], dataOverview['ExDividendDate'], dataOverview['EPS'], dataOverview['52WeekHigh'], dataOverview['52WeekLow'], dataOverview['50DayMovingAverage'], dataOverview['200DayMovingAverage'], dfNews_mod.iloc[0]['NewsTitle'], dfNews_mod.iloc[1]['NewsTitle'], dfNews_mod.iloc[2]['NewsTitle'], dfNews_mod.iloc[3]['NewsTitle'], dfNews_mod.iloc[4]['NewsTitle']


if __name__ == '__main__':
    app.run_server()
