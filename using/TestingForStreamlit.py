
from sqlalchemy import create_engine
import pandas as pd
import numpy as np
import ta

def applyindicators(df):
    df['SMA_200'] = df.Close.rolling(200).mean()
    df['SMA_20'] = df.Close.rolling(20).mean()
    df['stddev'] = df.Close.rolling(20).std()
    df['Upper'] = df.SMA_20 + 2.5 * df.stddev
    df['Lower'] = df.SMA_20 - 2.5 * df.stddev
    df['rsi'] = ta.momentum.rsi(df.Close, 2)

def conditions(df):
    df['Buy'] = np.where((df.Close.shift(1) > df.SMA_200.shift(1)) &
                        (df.Close.shift(1) < df.Lower.shift(1)) &
                         (0.96 * df.Close.shift(1) >= df.Low), 1, 0)
    
    df['Sell'] = np.where((df.rsi.shift(1) > 47), 1, 0)
    
    df['Buyprice'] = 0.96 * df.Close.shift(1)
    df['Sellprice'] = df.Open.shift(-1)

def matchtrades(df):
    Buy_Sells = df[(df.Buy == 1) | (df.Sell == 1)]
    matched_Buy_Sells = Buy_Sells[(Buy_Sells.Buy.diff() == 1) | (Buy_Sells.Sell.diff() == 1)]
    return matched_Buy_Sells

def main(symbols):
    engine = create_engine('sqlite:///using/RaynerDB.db')
    
    amounsymbol = len(symbols)
    
    tradeslist = []

    for symbol in symbols:
        df = pd.read_sql(symbol, engine, index_col='Date')
        df.Close = df['Close']
        applyindicators(df)
        conditions(df)
        trades = matchtrades(df)
        tradeslist.append(trades)
        
    tradesdf = pd.concat(tradeslist)
    
    tradesdf['profit'] = (tradesdf.Sellprice.shift(-1) - tradesdf.Buyprice) / tradesdf.Buyprice
    frame = pd.DataFrame({'profit': tradesdf[::2].profit.values,
                          'Buydates':tradesdf[::2].index,
                          'Selldates': tradesdf[1::2].index})
    sorted_df = frame.sort_values(by='Buydates')
    sorted_df = sorted_df.set_index('Buydates', drop=False)
    profit = (sorted_df.profit + 1).cumprod() #Какой-то график

    arraycheck = sorted_df.Buydates.shift(-1) > sorted_df.Selldates
    sorted_df['realtrade'] = arraycheck.shift(1).fillna('True')
    realtrades = sorted_df[sorted_df.realtrade == True]

    worsttrade = realtrades.profit.min() #Худший трейд

    realtrades = realtrades[~(realtrades.profit == realtrades.profit.min())]
    
    besttrade = realtrades.profit.max() #Лучший трейд

    persent = len([i for i in realtrades.profit if i > 0]) / len(realtrades.profit) #Процент удачных сделок

    averageprofit = realtrades.profit.mean() #Средний профит за сделку

    quantitytrade = len((realtrades.profit + 1).cumprod())
    
    profitpercentnocom = (realtrades.profit + 1).cumprod() # Фрейм с профитом не считая комиссии

    realtrades['Net Profit'] = realtrades['profit'] - 0.005

    profitpercentcom = (realtrades['Net Profit'] + 1).cumprod() # Фрейм с профитом и комиссией
    
    return worsttrade, besttrade, persent, averageprofit, amounsymbol, quantitytrade, profit, profitpercentnocom, profitpercentcom
