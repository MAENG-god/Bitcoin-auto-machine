import ccxt
import pprint
import time
from numpy import short
import pandas as pd
import datetime
import larry
import math
import requests

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
#슬랙 알림
# def post_message(text):
#     channel = "#automachine"
#     token = "xoxb-3352068368884-3346884420261-NcqE2bBfTZtHZSP42wMf0ft4"
#     response = requests.post("https://slack.com/api/chat.postMessage",
#         headers={"Authorization": "Bearer "+token},
#         data={"channel": channel,"text": text}
#     )
#     print(response)

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

#기록 함수
# def record(position, win_or_lose, balance):
#     f = open("/Users/kimmingi/코딩/bitcoin/record.txt", "a")
#     data = "진입포지션:{}, 승패:{}, 잔고:{} \n".format(position, win_or_lose, balance)
#     f.write(data)
#     f.close()

#수량계산 함수
def cal_amount(usdt_balance, cur_price):
    portion = 0.4
    usdt_trade = usdt_balance * portion
    amount = math.floor((usdt_trade * 1000000)/cur_price) / 1000000
    return amount 

def cal_amount2(usdt_balance, cur_price):
    portion = 0.5
    usdt_trade = usdt_balance * portion
    amount = math.floor((usdt_trade * 1000000)/cur_price) / 1000000
    return amount 

def cal_amount3(usdt_balance, cur_price):
    portion = 0.99
    usdt_trade = usdt_balance * portion
    amount = math.floor((usdt_trade * 1000000)/cur_price) / 1000000
    return amount 

#포지션 진입 함수
def enter_position(exchange, symbol, cur_price, long_target, short_target, position, usdt):
    global enter_price
    amount = cal_amount(usdt, cur_price) * leverage
    if cur_price > long_target:         # 현재가 > long 목표가
        if flow != "don't_up":
            position['type'] = 'long'
            position['amount'] = amount
            exchange.create_market_buy_order(symbol=symbol, amount=amount)
            enter_price = cur_price
            text = "드가자~ 잔액:{}, 포지션: long".format(usdt)
            print(text)
            
    elif cur_price < short_target:      # 현재가 < short 목표가
        if flow != "don't_down":    
            position['type'] = 'short'
            position['amount'] = amount
            exchange.create_market_sell_order(symbol=symbol, amount=amount)
            enter_price = cur_price
            text = "드가자~ 잔액:{}, 포지션: short".format(usdt)
            print(text)

#포지션 종료 함수
def exit_position(exchange, symbol, position, cur_price, enter_price, usdt):
    global target, sell_long, sell_short, second_chance, third_chance
    amount = position['amount']
    if position['type'] == 'long':
        if target == 0:
            target = enter_price * (1 + 0.01)
        #분할매수
        if second_chance == 1:
            if cur_price < enter_price * (1 - 0.001):
                print(usdt)
                amount2 = cal_amount2(usdt, cur_price) * leverage
                position['amount'] += amount2
                exchange.create_market_buy_order(symbol=symbol, amount=amount2)
                second_chance = 0
        elif third_chance == 1:
            if cur_price < enter_price * (1 - 0.002):
                print(usdt)
                amount3 = cal_amount3(usdt, cur_price) * leverage
                position['amount'] += amount3
                exchange.create_market_buy_order(symbol=symbol, amount=amount3)
                third_chance = 0
                
        elif cur_price < enter_price * (1 - 0.006):
            exchange.create_market_sell_order(symbol=symbol, amount=amount)
            position['type'] = None
            text = "손절합니다.. 잔액:{}".format(usdt)
            print(text)
        if cur_price > target:
            sell_long = target
            target += enter_price * (0.002)
        if cur_price < sell_long - enter_price * (0.001): 
            exchange.create_market_sell_order(symbol=symbol, amount=amount)
            position['type'] = None 
            text = "개꿀따라시! 잔액:{}".format(usdt)
            print(text)
    elif position['type'] == 'short':
        if target == 0:    
            target = enter_price * (1 - 0.01)
        #분할매수
        if second_chance == 1:
            if cur_price > enter_price * (1 + 0.001):
                print(usdt)
                amount2 = cal_amount2(usdt, cur_price) * leverage
                position['amount'] += amount2
                exchange.create_market_sell_order(symbol=symbol, amount=amount2)
                second_chance = 0
        elif third_chance == 1:
            if cur_price > enter_price * (1 + 0.002):
                print(usdt)
                amount3 = cal_amount3(usdt, cur_price) * leverage
                position['amount'] += amount3
                exchange.create_market_sell_order(symbol=symbol, amount=amount3)
                third_chance = 0
                
        elif cur_price > enter_price * (1 + 0.006):
            exchange.create_market_buy_order(symbol=symbol, amount=amount)
            position['type'] = None 
            text = "손절합니다.. 잔액:{}".format(usdt)
            print(text)
        if cur_price < target:
            sell_short = target
            target -= enter_price * (0.002)
        if cur_price > sell_short + enter_price * (0.001):
            exchange.create_market_buy_order(symbol=symbol, amount=amount)
            position['type'] = None 
            text = "개꿀따라시! 잔액:{}".format(usdt)
            print(text)
        
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
usdt = balance['free']['USDT']
position = {
    "type": None,
    "amount": 0
} 
enter_price = 0
trade_history = []

target = 0
sell_long = 0
sell_short = 1000000
second_chance = 1
third_chance = 1

while True: 
    long_target, short_target = larry.cal_target(binance, symbol)
    try:
        balance = binance.fetch_balance()
        usdt = balance['free']['USDT']
    except:
        usdt = -1

    #현재 가격 가져오고 수량 정하기
    ticker = binance.fetch_ticker(symbol)
    cur_price = ticker['last']
    
    #시장 흐름 파악
    flow = larry.rsi(binance, symbol, cur_price)
    
    #포지션 진입
    if position['type'] is None:
        if usdt != -1:
            enter_position(binance, symbol, cur_price, long_target, short_target, position, usdt)
    
    #포지션 정리
    if position['type'] is not None:   
        if usdt != -1: 
            exit_position(binance, symbol, position, cur_price, enter_price, usdt)
            if position['type'] is None:
                target = 0
                sell_long = 0
                sell_short = 1000000
                second_chance = 1
                third_chance = 1
    time.sleep(0.2)