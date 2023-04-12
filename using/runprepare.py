import pandas as pd
import ta
import numpy as np
import time
from datetime import timedelta, datetime
from binance import Client
from sys import argv
import ast

namescript, apikey, apisecret, investment, symbols = argv

symbols = ast.literal_eval(symbols)

client = Client(api_key=apikey, api_secret=apisecret)

tradesdf = pd.DataFrame({'symbol':symbols})

tradesdf['open_trade'] = False
tradesdf['quantity'] = 0
tradesdf['buytime'] = 0

def changepos(symbol, order):
    if order['side'] == 'BUY' and order['status'] != 'CANCELED':
        tradesdf.loc[tradesdf.symbol == symbol, 'open_trade'] = True
        tradesdf.loc[tradesdf.symbol == symbol, 'quantity'] = float(order['origQty'])
        tradesdf.loc[tradesdf.symbol == symbol, 'buytime'] = datetime.now() + timedelta(hours=3)
    else:
        tradesdf.loc[tradesdf.symbol == symbol, 'open_trade'] = False
        tradesdf.loc[tradesdf.symbol == symbol, 'quantity'] = 0
        tradesdf.loc[tradesdf.symbol == symbol, 'buytime'] = 0


def gethourdata(symbol):
    frame = pd.DataFrame(client.get_historical_klines(symbol,'1h','210 hours ago UTC'))
    frame = frame[[0,4]]
    frame.columns = ['Time','Close']
    frame.set_index('Time', inplace=True)
    frame.index = pd.to_datetime(frame.index, unit='ms')
    frame.Close = frame.astype(float)
    return frame


def applyindicators(df):
    df['SMA_200'] = df.Close.rolling(200).mean()
    df['SMA_20'] = df.Close.rolling(20).mean()
    df['stddev'] = df.Close.rolling(20).std()
    df['Upper'] = df.SMA_20 + 2 * df.stddev
    df['Lower'] = df.SMA_20 - 2 * df.stddev
    df['rsi'] = ta.momentum.rsi(df.Close, 2)


def conditions(df):
    df['Buy'] = np.where((df.Close > df.SMA_200) &
                        (df.Close < df.Lower), 1, 0)

    df['Sell'] = np.where((df.rsi > 47), 1, 0)


def pricecalc(symbol, limit=0.96):
    raw_price = float(client.get_symbol_ticker(symbol=symbol)['price'])
    dec_len = len(str(raw_price).split('.')[1])
    price = raw_price * limit
    return round(price, dec_len)


def right_rounding(Lotsize):
    splitted = str(Lotsize).split('.')
    if float(splitted[0]) == 1:
        return 0
    else:
        return len(splitted[1])


def quantitycalc(symbol, investment):
    info = client.get_symbol_info(symbol=symbol)
    Lotsize = float([i for i in info['filters'] if i['filterType'] == 'LOT_SIZE'][0]['minQty'])
    price = pricecalc(symbol)
    qty = round(investment/price, right_rounding(Lotsize))
    return qty


def buy(symbol, investment):
    order = client.order_limit_buy(
    symbol=symbol,
    price = pricecalc(symbol),
    quantity=quantitycalc(symbol,investment))
    changepos(symbol,order)
    # print(order)


def sell(symbol):
    order = client.create_order(
    symbol = symbol,
    side='SELL',
    type='MARKET',
    quantity = tradesdf[tradesdf.symbol == symbol].quantity.values[0])
    changepos(symbol,order)
    # print(order)


def cancel(symbol, orderId):
    order = client.cancel_order(
    symbol=symbol,
    orderId=orderId)
    changepos(symbol,order)
    # print(order)


def trader(investment):
    for symbol in tradesdf[tradesdf.open_trade == True].symbol:

        opens = client.get_open_orders(symbol=symbol)
        buytimeplus = tradesdf.loc[tradesdf.symbol == symbol, 'buytime']
        orderId = opens[0]['orderId']

        df = gethourdata(symbol)
        applyindicators(df)
        conditions(df)

        lasttwo = df.tail(2)
        lastrow = lasttwo.shift(1).dropna()

        if lastrow.Sell.values[0] == 1 and not opens:
            sell(symbol)

        elif opens and buytimeplus.iloc[0] <= datetime.now():
            cancel(symbol, orderId)

        elif lastrow.Sell.values[0] == 1 and float(opens[0]['executedQty']) > 0:
            tradesdf.loc[tradesdf.symbol == symbol, 'quantity'] = float(opens[0]['executedQty'])
            cancel(symbol, orderId)
            sell(symbol)

    for symbol in tradesdf[tradesdf.open_trade == False].symbol:
        df = gethourdata(symbol)
        applyindicators(df)
        conditions(df)
        lastrow = df.tail(1)
        if lastrow.Buy.values[0] == 1:
            buy(symbol, investment)

def start(investment):
    while True:
        time.sleep(5)
        # print(tradesdf[tradesdf.open_trade == True].symbol)
        try:
            trader(investment)
        except KeyboardInterrupt:
            break
        except:
            continue

start(investment)