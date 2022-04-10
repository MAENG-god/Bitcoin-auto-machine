import pandas as pd 

# volatility breakout 
def cal_target(exchange, symbol):
    btc = exchange.fetch_ohlcv(
        symbol=symbol,
        timeframe='5m', 
        since=None, 
        limit=10
    )
    df = pd.DataFrame(data=btc, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
    df['datetime'] = pd.to_datetime(df['datetime'], unit='ms')
    df.set_index('datetime', inplace=True)

    yesterday = df.iloc[-2]
    today = df.iloc[-1]
    if abs(yesterday['high'] - yesterday['low']) < 50:
        long_target = 1000000
        short_target = 1
    else:
        long_target = today['open'] + (yesterday['high'] - yesterday['low']) * 0.5
        short_target = today['open'] - (yesterday['high'] - yesterday['low']) * 0.5
    return long_target, short_target 
    
#rsi 지표 포지션 선정
def rsi(exchange, symbol, cur_price):
    btc = exchange.fetch_ohlcv(
        symbol=symbol,
        timeframe='5m', 
        since=None, 
        limit=15
    )
    df = pd.DataFrame(data=btc, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
    df['size'] = df['close'] - df['open']    
    au = 0
    ad = 0
    # cur = cur_price - df.iloc[-1]['open']
    for i in df.iloc[:14]['size']:
        if i >= 0:
            au += i / 14
        else:
            ad += i / 14 * (-1)
    # if cur >= 0:
    #     au += cur / 14
    # else:
    #     ad += cur / 14 * (-1)
    rs = au / ad
    rsi = rs / ( 1 + rs) * 100
    
    if rsi >= 67:
        return "down"
    elif rsi <= 27:
        return "up"

def rsi_2(exchange, symbol, cur_price):
    btc = exchange.fetch_ohlcv(
        symbol=symbol,
        timeframe='5m', 
        since=None, 
        limit=15
    )
    df = pd.DataFrame(data=btc, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
    df['size'] = df['close'] - df['open']  
    df['datetime'] = pd.to_datetime(df['datetime'], unit='ms')
    df.set_index('datetime', inplace=True)

    yesterday = df.iloc[-2]
    today = df.iloc[-1]
    if abs(yesterday['high'] - yesterday['low']) < 50:
        long_target = 1000000
        short_target = 1
    else:
        long_target = today['open'] + (yesterday['high'] - yesterday['low']) * 0.5
        short_target = today['open'] - (yesterday['high'] - yesterday['low']) * 0.5
      
    au = 0
    ad = 0
    # cur = cur_price - df.iloc[-1]['open']
    for i in df.iloc[:14]['size']:
        if i >= 0:
            au += i / 14
        else:
            ad += i / 14 * (-1)
    # if cur >= 0:
    #     au += cur / 14
    # else:
    #     ad += cur / 14 * (-1)
    rs = au / ad
    rsi = rs / ( 1 + rs) * 100
    
    if rsi >= 67:
        if cur_price < short_target:
            return "switch short"
    elif rsi <= 27:
        if cur_price > long_target:
            return "switch long"
    else:
        return "stay"