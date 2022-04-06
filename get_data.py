import websocket, json, ta
import pandas as pd
import sqlalchemy
import numpy as np
import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)

engine = sqlalchemy.engine.create_engine('sqlite:///testingstream.db')

symbol = 'btcusdt'
interval = '1m'

SOCKET = f"wss://stream.binance.com:9443/ws/{symbol}@kline_{interval}" 

def format_df(msg):
    frame = pd.DataFrame(msg)
    frame = frame.loc[:,['T', 'o', 'h', 'l', 'c', 'V']]
    frame.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume']
    frame = frame.set_index('Time')
    frame.index = pd.to_datetime(frame.index, unit='ms')
    frame = frame.astype(float)
    return frame
 
def on_open(ws):
    print('opened connection')

def on_close(ws):
    print('closed connection')

def on_message(ws, message):
    # printing received messages
    respond = json.loads(message)
    candle = respond['k']
    df = format_df([candle])
    
    #add to live database    
    df.to_sql('testingstream', engine, if_exists='append', index=True)
    
ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
ws.run_forever()
