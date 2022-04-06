# BinanceAPI-TradingBot

This bot includes 02 scripts which doing the following:
- get_data.py: Scrape live data from Binance websocket feed, tabulate and append to a database using SQLAlchemy
- main.py: Accessing the database and using a combination of RSI, MACD and Stochastic indicator to produce signals and execute BUY/SELL order accordingly

About the stategy:
- A BUY order is executed if all of the following conditions are satisfied: 
  + RSI: above 50 
  + Stochastic: The %K and %D values are between 20 and 80 
  + MACD: Above signal line
- A SELL signal is executed if either:
  + Price hit TAKE PROFIT of 1%
  + Price hit STOPLOSS of 1%


