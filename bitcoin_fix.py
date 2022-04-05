import ccxt
import pprint
import time
from numpy import short
import pandas as pd
import datetime
import larry
import math

#바이낸스 객체 생성
api_key = "mF7PJ1yW3YtETZi4uxjDpf5NQGJO2bKedAEMnzBagdux37s5vA8IKnAwhq5CPHZy"
secret = "rsffphg33Pu3CQ1ZUwbiWOYRKKzKGf7hK5YAo9gvjWjYeNYlesTtD170nLE2S84i"

binance = ccxt.binance(config={
    'apiKey': api_key, 
    'secret': secret,
    'enableRateLimit': True,
    'options': {
        'defaultType': 'future'
    }
})

#마켓조회
# markets = binance.load_markets()
# for m in markets:
#     print(m)
    
#선물 잔고 조회
balance = binance.fetch_balance(params={"type": "future"})
print(balance['USDT'])

#현재가 조회
# btc = binance.fetch_ticker("BTC/USDT")
# print(btc)

#과거 데이터 조회
# btc = binance.fetch_ohlcv(
#     symbol="BTC/USDT", 
#     timeframe='1d', 
#     since=None, 
#     limit=10)

# df = pd.DataFrame(btc, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
# df['datetime'] = pd.to_datetime(df['datetime'], unit='ms')
# df.set_index('datetime', inplace=True)
# print(df)

#매수/롱 포지션 진입
# order = binance.create_market_buy_order(
#     symbol = "BTC/USDT",
#     amount = 0.001
# )

# pprint.pprint(order)

#매수/롱 포지션 정리
# order = binance.create_market_sell_order(
#     symbol="BTC/USDT",
#     amount=0.001
# )

# pprint.pprint(order)

#매도/숏 포지션 진입
# order = binance.create_market_sell_order(
#     symbol="BTC/USDT",
#     amount=0.001, 
# )

# pprint.pprint(order)

#매도/숏 포지션 정리
# order = binance.create_market_buy_order(
#     symbol = "BTC/USDT",
#     amount = 0.001
# )

# pprint.pprint(order)

#대기 주문 조회
# open_orders = binance.fetch_open_orders(
#     symbol="BTC/USDT"
# )
# pprint.pprint(open_orders)

#선물 현재가 출력하기
# while True: 
#     btc = binance.fetch_ticker(symbol)
#     print(btc['last'])
#     time.sleep(1)

#현재 시간 출력하기
# while True: 
#     btc = binance.fetch_ticker(symbol)
#     now = datetime.datetime.now()
#     print(now, btc['last'])
#     time.sleep(1)


#수량계산 함수
def cal_amount(usdt_balance, cur_price):
    portion = 1
    usdt_trade = usdt_balance * portion
    amount = math.floor((usdt_trade * 1000000)/cur_price) / 1000000
    return amount 

#포지션 진입 함수
def enter_position(exchange, symbol, cur_price, long_target, short_target, amount, position, usdt):
    global enter_price
    if cur_price > long_target:         # 현재가 > long 목표가
        position['type'] = 'long'
        position['amount'] = amount
        enter_price = cur_price
        exchange.create_market_buy_order(symbol=symbol, amount=amount)
        print("드가자~", "잔액:", usdt, "포지션: long")
    elif cur_price < short_target:      # 현재가 < short 목표가
        position['type'] = 'short'
        position['amount'] = amount
        enter_price = cur_price
        exchange.create_market_sell_order(symbol=symbol, amount=amount)
        print("드가자~", "잔액:", usdt, "포지션: short")

#포지션 종료 함수
def exit_position(exchange, symbol, position, cur_price, enter_price, usdt, trade_history):
    amount = position['amount']
    if position['type'] == 'long':
        target = enter_price * (1 + 0.0028)
        sell = 0
        if cur_price < enter_price * (1 - 0.0012):
            exchange.create_market_sell_order(symbol=symbol, amount=amount)
            position['type'] = None
            print("손절;;", "잔액:", usdt)
            trade_history.append(["잔액", usdt])
        if cur_price > target:
            sell = target
            target += enter_price * (0.002)
        elif cur_price < sell: 
            exchange.create_market_sell_order(symbol=symbol, amount=amount)
            position['type'] = None 
            print("컷!", "잔액:", usdt)
            trade_history.append(["잔액", usdt])
    elif position['type'] == 'short':
        target = enter_price * (1 - 0.0028)
        sell = 10000000
        if cur_price > enter_price * (1 + 0.0012):
            exchange.create_market_buy_order(symbol=symbol, amount=amount)
            position['type'] = None 
            print("손절;;", "잔액:", usdt)
            trade_history.append(["잔액", usdt])
        if cur_price < target:
            sell = target
            target -= enter_price * (0.002)
        elif cur_price > sell:
            exchange.create_market_buy_order(symbol=symbol, amount=amount)
            position['type'] = None 
            print("컷!", "잔액:", usdt)
            trade_history.append(["잔액", usdt])
        
#레버리지 설정
markets = binance.load_markets()
symbol = "BTC/USDT"
market = binance.market(symbol)
leverage = 5

resp = binance.fapiPrivate_post_leverage({
    'symbol': market['id'],
    'leverage': leverage
})
        
#동작
symbol = "BTC/USDT"
long_target, short_target = larry.cal_target(binance, symbol)
balance = binance.fetch_balance()
usdt = balance['total']['USDT']
position = {
    "type": None,
    "amount": 0
} 
enter_price = 0
trade_history = []

while True: 
    long_target, short_target = larry.cal_target(binance, symbol)
    balance = binance.fetch_balance()
    usdt = balance['total']['USDT']

    #현재 가격 가져오고 수량 정하기
    ticker = binance.fetch_ticker(symbol)
    cur_price = ticker['last']
    amount = cal_amount(usdt, cur_price) * leverage
    
    #포지션 진입
    if position['type'] is None:
        enter_position(binance, symbol, cur_price, long_target, short_target, amount, position, usdt)
    
    #포지션 정리
    if position['type'] is not None:    
        exit_position(binance, symbol, position, cur_price, enter_price, usdt, trade_history)
    