# import ccxt
# import pprint
# import time
# from numpy import short
# import pandas as pd
# import datetime
# import larry
# import math
import requests


# api_key = "mF7PJ1yW3YtETZi4uxjDpf5NQGJO2bKedAEMnzBagdux37s5vA8IKnAwhq5CPHZy"
# secret = "rsffphg33Pu3CQ1ZUwbiWOYRKKzKGf7hK5YAo9gvjWjYeNYlesTtD170nLE2S84i"

# binance = ccxt.binance(config={
#     'apiKey': api_key, 
#     'secret': secret,
#     'enableRateLimit': True,
#     'options': {
#         'defaultType': 'future'
#     }
# })
# symbol = "BTC/USDT"

# ticker = binance.fetch_ticker(symbol)
# cur_price = ticker['last']

# def rsi(exchange, symbol, cur_price):
#     btc = exchange.fetch_ohlcv(
#         symbol=symbol,
#         timeframe='1m', 
#         since=None, 
#         limit=14
#     )
#     df = pd.DataFrame(data=btc, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
#     df['size'] = df['close'] - df['open']    
#     au = 0
#     ad = 0
#     cur = cur_price - df.iloc[-1]['open']
#     for i in df.iloc[:14]['size']:
#         if i >= 0:
#             au += i / 14
#         else:
#             ad += i / 14 * (-1)
#     if cur >= 0:
#         au += cur / 14
#     else:
#         ad += cur / 14 * (-1)
#     rs = au / ad
#     rsi = rs / ( 1 + rs) * 100
#     if rsi >= 70:
#         return "short"
#     elif rsi <= 30:
#         return "long"
#     else:
#         return rsi
# print(rsi(binance, symbol, cur_price))


def a(num1, num2):
    num = num1 + num2
    return num
 
def b(num1, num2):
    num = num1 * num2
    num = a(num, num)
    return num
print(b(2, 3))