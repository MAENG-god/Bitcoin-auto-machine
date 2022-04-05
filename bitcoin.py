import ccxt
import pprint
import time
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
    portion = 0.1 
    usdt_trade = usdt_balance * portion
    amount = math.floor((usdt_trade * 1000000)/cur_price) / 1000000
    return amount 

#포지션 진입 함수
def enter_position(exchange, symbol, cur_price, long_target, short_target, amount, position):
    if cur_price > long_target:         # 현재가 > long 목표가
        position['type'] = 'long'
        position['amount'] = amount
        exchange.create_market_buy_order(symbol=symbol, amount=amount)
    elif cur_price < short_target:      # 현재가 < short 목표가
        position['type'] = 'short'
        position['amount'] = amount
        exchange.create_market_sell_order(symbol=symbol, amount=amount)

#포지션 종료 함수
def exit_position(exchange, symbol, position):
    amount = position['amount']
    if position['type'] == 'long':
        exchange.create_market_sell_order(symbol=symbol, amount=amount)
        position['type'] = None 
    elif position['type'] == 'short':
        exchange.create_market_buy_order(symbol=symbol, amount=amount)
        position['type'] = None 
        
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
op_mode = False 
position = {
    "type": None,
    "amount": 0
} 

while True: 
    now = datetime.datetime.now()

    if now.hour == 8 and now.minute == 50 and (0 <= now.second < 10):
        if op_mode and position['type'] is not None:
            exit_position(binance, symbol, position)
            op_mode = False         # 9시 까지는 다시 포지션 진입하지 않음 

    # udpate target price
    if now.hour == 9 and now.minute == 0 and (20 <= now.second < 30):
        long_target, short_target = larry.cal_target(binance, symbol)
        balance = binance.fetch_balance()
        usdt = balance['total']['USDT']
        op_mode = True 
        time.sleep(10)

    ticker = binance.fetch_ticker(symbol)
    cur_price = ticker['last']
    amount = cal_amount(usdt, cur_price)

    if op_mode and position['type'] is None:
        enter_position(binance, symbol, cur_price, long_target, short_target, amount, position)

    print(now, cur_price)
    time.sleep(1)