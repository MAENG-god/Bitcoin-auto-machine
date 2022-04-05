import pandas as pd 

# volatility breakout 
def cal_target(exchange, symbol):
    btc = exchange.fetch_ohlcv(
        symbol=symbol,
        timeframe='3m', 
        since=None, 
        limit=10
    )
    df = pd.DataFrame(data=btc, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
    df['datetime'] = pd.to_datetime(df['datetime'], unit='ms')
    df.set_index('datetime', inplace=True)

    yesterday = df.iloc[-2]
    today = df.iloc[-1]
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
    
    
    