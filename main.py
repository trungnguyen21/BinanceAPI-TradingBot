from distutils.debug import DEBUG
import sqlalchemy, time, ta, os, logging
import pandas as pd
import numpy as np
import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)

LOG_FORMAT = "%(asctime)s - %(message)s"
logging.basicConfig(filename='D:\Python_Projects\kucoin-RSI-bot\RSI-bot\order_log.log', level=logging.DEBUG, format=LOG_FORMAT)
logger = logging.getLogger()

engine = sqlalchemy.engine.create_engine('sqlite:///testingstream.db')

symbol = 'btcusdt'
interval = '1m'

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

def applytech(df):
    df['%K'] = ta.momentum.stoch(df.High, df.Low, df.Close, window=14, smooth_window=3)
    df['%D'] = df['%K'].rolling(3).mean()
    df['rsi'] = ta.momentum.rsi(df.Close, window=14)
    df['macd'] = ta.trend.macd_diff(df.Close)
    df.dropna(inplace=False)

def strategy(qty, open_position=False):
    df = pd.read_sql('testingstream', engine)
    applytech(df)
    inst = Signals(df, 15)
    inst.decide()
    os.system('cls')
    print(f'current Close price of {symbol} is ' + str(df.Close.iloc[-1]))
    if df.Buy.iloc[-1]:
        buy_price = df.Close.iloc[-1]
        logger.info(f"Executed BUY signal at {buy_price}")
        #insert binance BUY order
        print('BUY BTC right now!!')        

        open_position = True

        while open_position:
            time.sleep(0.5)
            df = pd.read_sql('testingstream', engine)
            os.system('cls')
            print(f'current Target price ' + str(buy_price * 1.005))
            print(f'current Stoploss ' + str(buy_price * 0.995))
            print(f'current Close ' + str(df.Close.iloc[-1]))


            if df.Close.iloc[-1] <= buy_price * 0.995 or df.Close.iloc[-1] >= buy_price* 1.002:
                sell_price = df.Close.iloc[-1]
                logger.info(f"Executed SELL signal at {sell_price}")
                #insert binance SELL order
                print("SELL BTC NOW!!")
                break

while True:
    strategy(0.001)
    time.sleep(1)