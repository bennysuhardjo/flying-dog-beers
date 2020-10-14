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
import os
import psycopg2

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

headers = {'AccountKey':'/cwI6AoOQzefPZARL5M4Eg==', 'accept': 'application/json'}
results = []
while True:
	new_results = requests.get("http://datamall2.mytransport.sg/ltaodataservice/CarParkAvailabilityv2",headers=headers,params={'$skip': len(results)}).json()['value']
	if new_results == []:
        	break
	else:
         	results += new_results
json_data = []
for i in results: 
	json_data.append( [i["CarParkID"],i["Area"],i["Development"],i["Location"],i["AvailableLots"],i["LotType"],i["Agency"]]) 
df_carPark = pd.DataFrame.from_records( json_data ).rename(columns={0: "CarParkID", 1: "Area", 2: "Development", 3: "Location", 4: "AvailableLots", 5: "LotType", 6: "Agency"})
isChosen = df_carPark['Development'].str.upper().str.find("TIONG") != -1
Chosen = df_carPark[isChosen]

Chosen_Latest = Chosen
Chosen_Latest[['Latitude','Longitude']] = Chosen_Latest.Location.str.split(" ",expand=True)
#Chosen_Latest = Chosen_Latest.drop(columns=['a','b'])
Chosen_Latest['Latitude'] = pd.to_numeric(Chosen_Latest['Latitude'],errors='coerce')
Chosen_Latest['Longitude'] = pd.to_numeric(Chosen_Latest['Longitude'],errors='coerce')

figCarParkAvailability = px.scatter_mapbox(Chosen_Latest, lat='Latitude', lon='Longitude', color="AvailableLots", zoom=15, height=500, hover_name='Development')

figCarParkAvailability.update_layout(mapbox_style="stamen-terrain")

#headers = {'AccountKey': '/cwI6AoOQzefPZARL5M4Eg==',
#           'accept': 'application/json'
#}

#results = []

#while True:
#     new_results = requests.get(
#         "http://datamall2.mytransport.sg/ltaodataservice/BusServices",
#         headers=headers,
#         params={'$skip': len(results)}
#     ).json()['value']
#     if new_results == []:
#         break
#     else:
#         results += new_results



#results =requests.get("http://datamall2.mytransport.sg/ltaodataservice/BusServices", headers=headers).json()['value']


#json_data = []

#data['value']

#for i in results: 
    #print(i, i["BusStopCode"]) 
#    json_data.append( [i["ServiceNo"],i["Operator"],
#                       i["Direction"],i["Category"],
#                       i["OriginCode"],i["DestinationCode"]

                      
                      
#                      ]) 


#df_busService = pd.DataFrame.from_records( json_data ).rename(columns={0: "ServiceNo", 1: "Operator", 2: "Direction", 3: "Category", 4: "OriginCode"
#                                                                     , 5: "DestinationCode"})


#headers = {'AccountKey': '/cwI6AoOQzefPZARL5M4Eg==',
#           'accept': 'application/json'
#}
# MPHd2F+USH+1hA1FDikGeA==
# NQD/ZccwR5SEDj/MehpKww== 

#r =requests.get("http://datamall2.mytransport.sg/ltaodataservice/PV/Bus", headers=headers).json()


#url = r['value'][0]['Link']
#file_name = 'myzip.zip'

#with urllib.request.urlopen(url) as response, open(file_name, 'wb') as out_file:
#    shutil.copyfileobj(response, out_file)
#    with zipfile.ZipFile(file_name) as zf:
#        zf.extractall()
#df_busStopStats = pd.read_csv(file_name)



DATABASE_URL = os.environ['DATABASE_URL']
conn = psycopg2.connect(DATABASE_URL, sslmode='require')

# Connect to your postgres DB
# conn = psycopg.connect("dbname=test user=postgres")
# Open a cursor to perform database operations
cur = conn.cursor()
# Execute a query
#monthString = "'202008'"
#ptType = "'BUS'"
cur.execute('SELECT "DAY_TYPE","TIME_PER_HOUR", "TOTAL_TAP_IN_VOLUME" FROM "TransactionByHour"');
# Retrieve query results
df_busStopStats = pd.DataFrame(cur.fetchall()).rename(columns={0: "DAY_TYPE", 1: "TIME_PER_HOUR", 2: "TOTAL_TAP_IN_VOLUME"}) 

df_busStopStatsSummary = df_busStopStats.groupby(["DAY_TYPE","TIME_PER_HOUR"], as_index=False)[["TOTAL_TAP_IN_VOLUME"]].sum()

fig = go.Figure(data=go.Heatmap(
                   z=df_busStopStatsSummary['TOTAL_TAP_IN_VOLUME'],
                   x=df_busStopStatsSummary['TIME_PER_HOUR'],
                  y=df_busStopStatsSummary['DAY_TYPE'],
                   hoverongaps = False))
fig.update_layout(
    title="Tap-In Volume (Bus & Train) by Hours of the Day"
)


cur.execute('SELECT "ServiceNo","Operator" FROM "BusService"');
# Retrieve query results
df_busService = pd.DataFrame(cur.fetchall()).rename(columns={0: "ServiceNo", 1: "Operator"}) 


cur.execute('SELECT "YEAR_MONTH","DAY_TYPE", "TIME_PER_HOUR", "PT_TYPE", "PT_CODE", "TOTAL_TAP_IN_VOLUME", "TOTAL_TAP_OUT_VOLUME", "BusStopCode", "RoadName", "BusStopDescription", "Latitude", "Longitude" FROM "selectedBusStopVolume1"');
# Retrieve query results
combined = pd.DataFrame(cur.fetchall()).rename(columns={0: "YEAR_MONTH", 1: "DAY_TYPE", 2: "TIME_PER_HOUR", 3: "PT_TYPE",
							     4: "PT_CODE", 5: "TOTAL_TAP_IN_VOLUME", 6: "TOTAL_TAP_OUT_VOLUME", 7: "BusStopCode",
							     8: "RoadName", 9: "BusStopDescription", 10: "Latitude", 11: "Longitude"}) 

	   
fig1 = px.scatter_mapbox(combined[combined["DAY_TYPE"]=="WEEKDAY"].sort_values(by=['TIME_PER_HOUR']), lat="Latitude", lon="Longitude", 
                  size_max=15, zoom=14, 
                  hover_name = combined[combined["DAY_TYPE"]=="WEEKDAY"].sort_values(by=['TIME_PER_HOUR'])['BusStopDescription'] ,
                  mapbox_style="carto-positron",
                  size = combined[combined["DAY_TYPE"]=="WEEKDAY"].sort_values(by=['TIME_PER_HOUR'])['TOTAL_TAP_IN_VOLUME'] ,     
                  animation_frame = combined[combined["DAY_TYPE"]=="WEEKDAY"].sort_values(by=['TIME_PER_HOUR'])['TIME_PER_HOUR']  , 
                  animation_group = combined[combined["DAY_TYPE"]=="WEEKDAY"].sort_values(by=['TIME_PER_HOUR'])["BusStopDescription" ]    
                  
                       )
fig1.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = 24
fig1.layout.updatemenus[0].buttons[0].args[1]["transition"]["duration"] = 24
fig1.layout.coloraxis.showscale = False
fig1.layout.sliders[0].pad.t = 10
fig1.layout.updatemenus[0].pad.t= 10         
fig1.update_layout(
    title="Tap-In Volume For Bus Stops around Raffles Place Throughout The Day (0 --> 00:00 to 00:59, 1 --> 01:00 to 01:59, etc)"
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
       dcc.Tab(label='Public Transport (Bus & Train)', children=[
            dbc.Row([
            		dbc.Col(
	    			dcc.Graph(
                			figure={
                    				'data': [{'x': df_busService['Operator'],
                    		 			  'type': 'histogram'},
                    					],
						'layout': {'title': 'No of Bus Services by Operators'}
                			}
            			), width=4
			),
	    		dbc.Col(
	    			dcc.Graph(
                			figure=fig
            			), width=8)
	    	]),
	    dbc.Row([
		dbc.Col(
			dcc.Graph(
				figure = fig1
			), width=12)	
			    
	    ])
        ]),
	dcc.Tab(label='CarPark Availability', children=[
		
		html.Label('Carpark Availability - Type in your location:   '),
            	dcc.Input(id='location_ticker', value='TIONG', type='text'),
            	html.Button(id='location-button-state', n_clicks=0, children='Submit'),

		dcc.Graph(
                	id='carparkavailability', config={ 'scrollZoom': True }
            	),	
	    	dash_table.DataTable(
    			id='locationtable',
    			columns=[{"name": i, "id": i} for i in Chosen.columns]
	    	)
	    
        ]),
        dcc.Tab(label='Banking', children=[
            html.A("Log-in to DBS (Work-In-Progress)", href="https://bankapitest.herokuapp.com/", target="_blank")
	    #dcc.Graph(
            #    figure={
            #        'data': [
            #            {'x': [1, 2, 3], 'y': [2, 4, 3],
            #                'type': 'bar', 'name': 'SF'},
            #            {'x': [1, 2, 3], 'y': [5, 4, 3],
            #             'type': 'bar', 'name': u'Montréal'},
            #        ]
            #    }
            #)
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


@app.callback(
	[Output('locationtable','data'),
	 Output('carparkavailability','figure')],
   	[Input('location-button-state', 'n_clicks')],
        [State('location_ticker', 'value')])
def set_cities_options(n_clicks, selected_location):
	isChosen = df_carPark['Development'].str.upper().str.find(selected_location.upper()) != -1
	Chosen = df_carPark[isChosen]
	
	Chosen_Latest = Chosen
	Chosen_Latest[['Latitude','Longitude']] = Chosen_Latest.Location.str.split(" ",expand=True)
	#Chosen_Latest = Chosen_Latest.drop(columns=['a','b'])
	Chosen_Latest['Latitude'] = pd.to_numeric(Chosen_Latest['Latitude'],errors='coerce')
	Chosen_Latest['Longitude'] = pd.to_numeric(Chosen_Latest['Longitude'],errors='coerce')

	figCarParkAvailability = go.Figure(data=[go.Scattermapbox(lat=Chosen_Latest.Latitude, lon=Chosen_Latest.Longitude, mode='markers', marker=go.scattermapbox.Marker(
            size=17,
            color='rgb(255, 0, 0)',
            opacity=0.7
        ), text=Chosen_Latest.Development)])

	latCentre = 1.3691
	lonCentre = 103.8454
	figCarParkAvailability.update_layout(mapbox_style="stamen-terrain", autosize=True, hovermode='closest', mapbox=dict(center=go.layout.mapbox.Center(lat=latCentre,lon=lonCentre),zoom=10))
	
	
	return Chosen.to_dict('records'), figCarParkAvailability

if __name__ == '__main__':
    app.run_server()
