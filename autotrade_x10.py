import ccxt
import pprint
import time
from numpy import short
import pandas as pd
import datetime
import larry_x10
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

#선물 잔고 조회
balance = binance.fetch_balance(params={"type": "future"})
print(balance['USDT'])

#수량계산 함수
def cal_amount(usdt_balance, cur_price):
    portion = 0.5
    usdt_trade = usdt_balance * portion
    amount1 = math.floor((usdt_trade * 1000000)/cur_price) / 1000000
    return amount1

def cal_amount2(usdt_balance, cur_price):
    portion = 0.5
    usdt_trade = usdt_balance * portion
    amount2 = math.floor((usdt_trade * 1000000)/cur_price) / 1000000
    return amount2 

def cal_amount3(usdt_balance, cur_price):
    portion = 0.99
    usdt_trade = usdt_balance * portion
    amount3 = math.floor((usdt_trade * 1000000)/cur_price) / 1000000
    return amount3 

#포지션 진입 함수
def enter_position(exchange, symbol, cur_price, long_target, short_target, position, usdt):
    global enter_price
    amount1 = cal_amount(usdt, cur_price) * leverage
    if cur_price > long_target:         # 현재가 > long 목표가
        if flow == "up":
            position['type'] = 'long'
            position['amount'] = amount1
            exchange.create_market_buy_order(symbol=symbol, amount=amount1)
            enter_price = cur_price
            text = "드가자~ 잔액:{}, 포지션: long".format(usdt)
            print(text)
            
    elif cur_price < short_target:      # 현재가 < short 목표가
        if flow == "down":    
            position['type'] = 'short'
            position['amount'] = amount1
            exchange.create_market_sell_order(symbol=symbol, amount=amount1)
            enter_price = cur_price
            text = "드가자~ 잔액:{}, 포지션: short".format(usdt)
            print(text)

#포지션 종료 함수
def exit_position(exchange, symbol, position, cur_price, enter_price, usdt):
    global target, sell_long, sell_short, second_chance, third_chance

    if position['type'] == 'long':
        if target == 0:
            target = enter_price * (1 + 0.008)
        #분할매수
        if second_chance == 1:
            if cur_price < enter_price * (1 - 0.001):
                amount2 = cal_amount2(usdt, cur_price) * leverage
                position['amount'] += amount2
                exchange.create_market_buy_order(symbol=symbol, amount=amount2)
                second_chance = 0
        elif third_chance == 1:
            if cur_price < enter_price * (1 - 0.002):
                amount3 = cal_amount3(usdt, cur_price) * leverage
                position['amount'] += amount3
                exchange.create_market_buy_order(symbol=symbol, amount=amount3)
                third_chance = 0
                
        elif cur_price < enter_price * (1 - 0.004):
            exchange.create_market_sell_order(symbol=symbol, amount=position['amount'])
            position['type'] = None
            text = "손절합니다.. 잔액:{}".format(usdt)
            print(text)
        if cur_price > target:
            sell_long = target
            target += enter_price * (0.002)
        if cur_price < sell_long - enter_price * (0.001): 
            exchange.create_market_sell_order(symbol=symbol, amount=position['amount'])
            position['type'] = None 
            text = "개꿀따라시! 잔액:{}".format(usdt)
            print(text)
    elif position['type'] == 'short':
        if target == 0:    
            target = enter_price * (1 - 0.008)
        #분할매수
        if second_chance == 1:
            if cur_price > enter_price * (1 + 0.001):
                amount2 = cal_amount2(usdt, cur_price) * leverage
                position['amount'] += amount2
                exchange.create_market_sell_order(symbol=symbol, amount=amount2)
                second_chance = 0
        elif third_chance == 1:
            if cur_price > enter_price * (1 + 0.002):
                amount3 = cal_amount3(usdt, cur_price) * leverage
                position['amount'] += amount3
                exchange.create_market_sell_order(symbol=symbol, amount=amount3)
                third_chance = 0
                
        elif cur_price > enter_price * (1 + 0.004):
            exchange.create_market_buy_order(symbol=symbol, amount=position['amount'])
            position['type'] = None 
            text = "손절합니다.. 잔액:{}".format(usdt)
            print(text)
        if cur_price < target:
            sell_short = target
            target -= enter_price * (0.002)
        if cur_price > sell_short + enter_price * (0.001):
            exchange.create_market_buy_order(symbol=symbol, amount=position['amount'])
            position['type'] = None 
            text = "개꿀따라시! 잔액:{}".format(usdt)
            print(text)
        
#레버리지 설정
markets = binance.load_markets()
symbol = "BTC/USDT"
market = binance.market(symbol)
leverage = 10

resp = binance.fapiPrivate_post_leverage({
    'symbol': market['id'],
    'leverage': leverage
})
        
#동작
symbol = "BTC/USDT"
long_target, short_target = larry_x10.cal_target(binance, symbol)
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
    long_target, short_target = larry_x10.cal_target(binance, symbol)
    try:
        balance = binance.fetch_balance()
        usdt = balance['free']['USDT']
    except:
        usdt = -1

    #현재 가격 가져오고 수량 정하기
    ticker = binance.fetch_ticker(symbol)
    cur_price = ticker['last']
    
    #시장 흐름 파악
    flow = larry_x10.rsi(binance, symbol, cur_price)
    
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
                position['amount'] = 0
    time.sleep(0.2)