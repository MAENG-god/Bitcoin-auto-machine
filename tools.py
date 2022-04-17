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
    u = 0
    ad = 0
    d = 0
    # cur = cur_price - df.iloc[-1]['open']
    for i in df.iloc[:14]['size']:
        if i >= 0:
            au += i
            u += 1
        else:
            ad += -i
            d += 1
    au /= u
    ad /= d
    # if cur >= 0:
    #     au += cur / 14
    # else:
    #     ad += cur / 14 * (-1)
    rs = au / ad
    rsi = rs / ( 1 + rs) * 100
    
    if rsi >= 50:
        return "down"
    elif rsi < 50:
        return "up"

#이동평균선
def ma(exchange, symbol):
    btc = exchange.fetch_ohlcv(
        symbol=symbol,
        timeframe='5m', 
        since=None, 
        limit=26
    )
    df = pd.DataFrame(data=btc, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
    ma7 = sum(df.iloc[-1:-8:-1]['close']) / 7
    ma25 = sum(df.iloc[-1:-26:-1]['close']) / 25
    ma = ma7 - ma25
    if ma > 0:
        return "up"
    else:
        return "down"
#스위칭
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
    
#캔들 파악
def candle(exchange, symbol, cur_price):
    btc = exchange.fetch_ohlcv(
        symbol=symbol,
        timeframe='5m', 
        since=None, 
        limit=26
    )
    df = pd.DataFrame(data=btc, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
    df['body'] = abs(df['close'] - df['open'])
    
    ma7 = sum(df.iloc[-2:-9:-1]['close']) / 7
    ma25 = sum(df.iloc[-2:-27:-1]['close']) / 25
    ma = ma7 - ma25
    
    if ma > 0: # 상승장일때
        if df.iloc[-3]['close'] - df.iloc[-3]['open'] > 0 and df.iloc[-2]['close'] - df.iloc[-2]['open'] > 0:
            if df.iloc[-3]['body'] > df.iloc[-2]['body'] * 2:
                if cur_price < df.iloc[-3]['close'] - df.iloc[-3]['body'] * 0.5:
                    return "night star" # 저녁별형
        elif min(df.iloc[-2]['open'], df.iloc[-2]['close']) - df.iloc[-2]['low'] > df.iloc[-2]['body'] * 2:
            if min(df.iloc[-2]['open'], df.iloc[-2]['close']) - df.iloc[-2]['low'] > 40:
                if cur_price < min(df.iloc[-2]['open'], df.iloc[-2]['close']):
                    return "hanging" # 교수형
        elif df.iloc[-2]['high'] - max(df.iloc[-2]['open'], df.iloc[-2]['close']) > df.iloc[-2]['body'] * 2:
            if df.iloc[-2]['high'] - max(df.iloc[-2]['open'], df.iloc[-2]['close']) > 40:
                return "meteor" # 유성형
        elif df.iloc[-2]['body'] > df.iloc[-3]['body']:
            if df.iloc[-2]['close'] - df.iloc[-2]['open'] < 0 and df.iloc[-3]['close'] - df.iloc[-3]['open'] > 0:
                return "down grap" # 하락장악형
        
    else: # 하락장일때
        if df.iloc[-3]['close'] - df.iloc[-3]['open'] < 0 and df.iloc[-2]['close'] - df.iloc[-2]['open'] < 0:
            if df.iloc[-3]['body'] > df.iloc[-2]['body'] * 2:
                if cur_price > df.iloc[-3]['close'] + df.iloc[-3]['body'] * 0.5:
                    return "mornig star" # 샛별형
        elif min(df.iloc[-2]['open'], df.iloc[-2]['close']) - df.iloc[-2]['low'] > df.iloc[-2]['body'] * 2:
            if min(df.iloc[-2]['open'], df.iloc[-2]['close']) - df.iloc[-2]['low'] > 40:
                return "hammer" # 망치형
        elif df.iloc[-2]['high'] - max(df.iloc[-2]['open'], df.iloc[-2]['close']) > df.iloc[-2]['body'] * 2:
            if df.iloc[-2]['high'] - max(df.iloc[-2]['open'], df.iloc[-2]['close']) > 40:
                if cur_price > max(df.iloc[-2]['open'], df.iloc[-2]['close']):
                    return "reverse hammer" # 역망치형
        elif df.iloc[-2]['body'] > df.iloc[-3]['body']:
            if df.iloc[-2]['close'] - df.iloc[-2]['open'] > 0 and df.iloc[-3]['close'] - df.iloc[-3]['open'] < 0:
                return "up grap" # 상승장악형
