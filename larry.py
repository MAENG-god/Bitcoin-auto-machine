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
    # if abs(yesterday['high'] - yesterday['low']) < 30:
    #     long_target = 1000000
    #     short_target = 1
    # else:
    long_target = today['open'] + (yesterday['high'] - yesterday['low']) * 0.5
    short_target = today['open'] - (yesterday['high'] - yesterday['low']) * 0.5
    return long_target, short_target 

#상승장, 하락장 계산
def cal_market(exchange, symbol, cur_price):
    btc = exchange.fetch_ohlcv(
        symbol=symbol,
        timeframe='15m', 
        since=None, 
        limit=10
    )
    df = pd.DataFrame(data=btc, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
    fift = cur_price - df.iloc[-1]['open']
    
    btc2 = exchange.fetch_ohlcv(
        symbol=symbol,
        timeframe='5m', 
        since=None, 
        limit=10
    )
    df2 = pd.DataFrame(data=btc2, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
    fift2 = cur_price - df.iloc[-1]['open']
    if fift > 0 and fift2 > 0:
        return "up"
    elif fift < 0 and fift2 < 0:
        return "down"
    
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
    
    if rsi >= 60:
        return "don't_up"
    elif rsi <= 30:
        return "don't_down"
    else:
        return "all"
    
