import time
import pyupbit
import datetime
import numpy as np
import json
import requests

# with open("kakao_code.json", "r") as fp:
#     tokens = json.load(fp)

def send_kakao_message(message):
    url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
    headers = {
        "Authorization": "Bearer " + "hlB4yE2ii-t7eRpWXo3RVNbGEVFF-O3s3W-CFl3-Cj11nAAAAYhnrBTF"
    }
    data = {
        "template_object": json.dumps({
            "object_type": "text",
            "text": message,
            "link": {
                "web_url": "www.naver.com"
            }
        })
    }
    response = requests.post(url, headers=headers, data=data)
    return response.status_code

def get_ror(ticker, k=0.5, count=30):
    df = pyupbit.get_ohlcv(ticker, count=count)
    df['range'] = (df['high'] - df['low']) * k
    df['target'] = df['open'] + df['range'].shift(1)
    df['ror'] = np.where(df['high'] > df['target'], df['close'] / df['target'], 1)
    ror = df['ror'].cumprod()[-2]
    return ror

def get_best_k(ticker):
    best_k = 0
    best_ror = 0
    for k in np.arange(0.1, 1.0, 0.1):
        ror = get_ror(ticker, k=k, count=30)
        if ror > best_ror:
            best_k = k
            best_ror = ror
    return best_k

def get_target_price(ticker, k):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price

def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    if df is not None and not df.empty:
        return df.index[0]
    return None


def get_ma15(ticker):
    """15일 이동 평균선 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=15)
    ma15 = df['close'].rolling(15).mean().iloc[-1]
    return ma15

def get_current_price(ticker):
    """현재가 조회"""
    orderbook = pyupbit.get_orderbook(ticker=ticker)
    if orderbook:
        return orderbook["orderbook_units"][0]["ask_price"]
    return None


def get_top_tickers():
    """시가 기준 상위 15위 종목 조회"""
    tickers = pyupbit.get_tickers(fiat="KRW")
    ticker_market_cap = {}

    for ticker in tickers:
        try:
            df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
            if df is not None and not df.empty:
                market_cap = df.iloc[0]['open'] * df.iloc[-1]['volume']
                ticker_market_cap[ticker] = market_cap
        except Exception:
            continue

    sorted_ticker_market_cap = sorted(ticker_market_cap.items(), key=lambda x: x[1], reverse=True)
    top_15_tickers = [ticker for ticker, _ in sorted_ticker_market_cap[:15]]

    return top_15_tickers



print("추천 시작")

while True:
    try:
        now = datetime.datetime.now()
        top_15_tickers = get_top_tickers()

        for ticker in top_15_tickers:
            best_k = get_best_k(ticker)
            start_time = get_start_time(ticker)
            if start_time is not None:
                end_time = start_time + datetime.timedelta(days=1)

                if start_time < now < end_time - datetime.timedelta(seconds=10):
                    target_price = get_target_price(ticker, best_k)
                    ma15 = get_ma15(ticker)
                    current_price = get_current_price(ticker)
                    if current_price and target_price < current_price and ma15 < current_price:
                        current_time = now.strftime("%Y-%m-%d %H:%M:%S")
                        message = f"({current_time}) 변동성 돌파 전략 조건 충족! 종목 추천: {ticker}" + "\nwww.naver.com"
                        status_code = send_kakao_message(message)
                        print("뿡뿡")
                        print(f"메시지 전송 결과: {status_code}")

        time.sleep(3)

        time.sleep(3)
    except Exception as e:
        print(e)
        time.sleep(3)