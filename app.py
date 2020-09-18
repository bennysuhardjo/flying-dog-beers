import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd
import requests
import plotly.express as px
from dash.dependencies import Input, Output


########### Define your variables
beers=['Chesapeake Stout', 'Snake Dog IPA', 'Imperial Porter', 'Double Dog IPA']
ibu_values=[35, 60, 85, 75]
abv_values=[5.4, 7.1, 9.2, 4.3]
color1='lightblue'
color2='darkgreen'
mytitle='Stock Trend'
tabtitle='Stock Trend'
myheading='Stock Trend'
label1='IBU'
label2='ABV'



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

    html.Label('Stock Ticker: '),
    dcc.Input(id='stock_ticker', value='IBM', type='text'),

    dcc.Graph(
        id='example-stock-1'
    ),
    #generate_table(df_mod_2020),
    ]
)

@app.callback(
    Output('example-stock-1', 'figure'),
    [Input('stock_ticker', 'value')]
)
def update_output_div(stock_tick):
    getStringRequest = "https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol="+stock_tick+"&outputsize=full&apikey=L5W8DWNNL7QRMNH9"
    data =requests.get(getStringRequest).json()
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

    return figStock

if __name__ == '__main__':
    app.run_server()
