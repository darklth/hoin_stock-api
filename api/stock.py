from flask import Flask, request, Response
import requests
from bs4 import BeautifulSoup
import yfinance as yf
import json

app = Flask(__name__)

# 한국 주식 가격 가져오는 함수 (네이버 금융 크롤링)
def get_korean_stock_price(ticker):
    url = f"https://finance.naver.com/item/main.naver?code={ticker}"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        html = requests.get(url, headers=headers).text
        soup = BeautifulSoup(html, "html.parser")
        price = soup.select_one(".no_today .blind").text
        return price
    except:
        return "조회 실패"

# 미국 주식 가격 가져오는 함수 (yfinance API)
def get_us_stock_price(symbol):
    try:
        stock = yf.Ticker(symbol)
        data = stock.history(period="1d")
        if not data.empty:
            return f"{float(data['Close'].iloc[-1]):.2f}"
        else:
            return "조회 실패"
    except:
        return "조회 실패"

@app.route("/api/stock", methods=["GET"])
def stock_api():
    # 1. 파라미터 받기 (name 또는 ticker)
    val = request.args.get("name") or request.args.get("ticker")
    
    if not val:
        result = {"error": "name 또는 ticker 파라미터가 필요합니다."}
        return Response(json.dumps(result, ensure_ascii=False), content_type="application/json; charset=utf-8")

    val_upper = val.upper()
    final_name = val
    price = "조회 실패"

    # 2. 종목 판별 로직
    if val == "삼성전자" or val == "005930":
        price = get_korean_stock_price("005930")
        final_name = "삼성전자"
    elif val == "LG전자" or val == "066570":
        price = get_korean_stock_price("066570")
        final_name = "LG전자"
    elif val_upper in ["TSLA", "테슬라"]:
        price = get_us_stock_price("TSLA")
        final_name = "테슬라"
    elif val_upper in ["AAPL", "애플"]:
        price = get_us_stock_price("AAPL")
        final_name = "애플"
    else:
        # 그 외에는 미국 티커로 간주하여 시도
        price = get_us_stock_price(val_upper)
        final_name = val

    # 3. 결과 생성
    result = {"name": final_name, "price": price}
    
    # ensure_ascii=False 설정을 통해 한글이 깨지지 않게 변환합니다.
    json_data = json.dumps(result, ensure_ascii=False)
    
    # Response 객체를 사용해 강제로 UTF-8 인코딩을 지정합니다.
    return Response(json_data, content_type="application/json; charset=utf-8")

if __name__ == "__main__":
    app.run()
