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

class Signals:
    def __init__(self, df, lags):
        self.df = df
        self.lags = lags
    
    def gettrigger(self):
        dfx = pd.DataFrame()
        for i in range(self.lags + 1):
            mask = (self.df['%K'].shift(i) < 20) & (self.df['%D'].shift(i) < 20)
            dfx = dfx.append(mask, ignore_index=True)
        return dfx.sum(axis=0)

    def decide(self):
        self.df['trigger'] = np.where(self.gettrigger(), 1, 0)
        self.df['Buy'] = np.where((self.df.trigger) & 
        (self.df['%K'].between(20,80)) & (self.df['%D'].between(20,80)) &
        (self.df.rsi > 60) & (self.df.macd > 0), 1, 0) 

def format_df(msg):
    frame = pd.DataFrame(msg)
    frame = frame.loc[:,['T', 'o', 'h', 'l', 'c', 'V']]
    frame.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume']
    frame = frame.set_index('Time')
    frame.index = pd.to_datetime(frame.index, unit='ms')
    frame = frame.astype(float)
    return frame

def applytech(df):
    df['%K'] = ta.momentum.stoch(df.High, df.Low, df.Close, window=14, smooth_window=3)
    df['%D'] = df['%K'].rolling(3).mean()
    df['rsi'] = ta.momentum.rsi(df.Close, window=14)
    df['macd'] = ta.trend.macd_diff(df.Close)
    df.dropna(inplace=True)
 
def on_open(ws):
    print('opened connection')

def on_close(ws):
    print('closed connection')

def on_message(ws, message):
    # print('received message')
    respond = json.loads(message)
    candle = respond['k']
    df = format_df([candle])
    
    #add to live database    
    df.to_sql('testingstream', engine, if_exists='append', index=True)
    
ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
ws.run_forever()