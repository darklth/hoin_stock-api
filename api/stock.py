from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import yfinance as yf

app = Flask(__name__)

# 한국 주식 크롤링 함수
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

# 미국 주식 API 함수
def get_us_stock_price(symbol):
    try:
        stock = yf.Ticker(symbol)
        data = stock.history(period="1d")
        return f"{float(data['Close'].iloc[-1]):.2f}" if not data.empty else "조회 실패"
    except:
        return "조회 실패"

@app.route("/api/stock", methods=["GET"])
def stock_api():
    # 1. name이나 ticker 중 아무거나 받아오기
    name_val = request.args.get("name")
    ticker_val = request.args.get("ticker")
    
    # 둘 중 하나라도 입력된 값을 검색어로 사용
    query = name_val or ticker_val
    
    if not query:
        return jsonify({"error": "name 또는 ticker 파라미터가 필요합니다."})

    # 2. 종목 판별 로직
    query_upper = query.upper()
    
    if query == "삼성전자" or query == "005930":
        price = get_korean_stock_price("005930")
        final_name = "삼성전자"
    elif query == "LG전자" or query == "066570":
        price = get_korean_stock_price("066570")
        final_name = "LG전자"
    elif query_upper == "TSLA" or query_upper == "테슬라":
        price = get_us_stock_price("TSLA")
        final_name = "TSLA"
    elif query_upper == "AAPL" or query_upper == "애플":
        price = get_us_stock_price("AAPL")
        final_name = "AAPL"
    else:
        # 그 외의 경우 yfinance로 시도 (미국 주식 티커라고 가정)
        price = get_us_stock_price(query_upper)
        final_name = query_upper

    return jsonify({"name": final_name, "price": price, "query": query})

if __name__ == "__main__":
    app.run()
