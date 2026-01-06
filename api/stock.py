from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import yfinance as yf

app = Flask(__name__)
# 한글 깨짐(유니코드 출력) 방지 설정
app.config['JSON_AS_ASCII'] = False

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

def get_us_stock_price(symbol):
    try:
        stock = yf.Ticker(symbol)
        data = stock.history(period="1d")
        return f"{float(data['Close'].iloc[-1]):.2f}" if not data.empty else "조회 실패"
    except:
        return "조회 실패"

@app.get("/api/stock")
def stock_api():
    # name 또는 ticker 파라미터 둘 다 지원
    val = request.args.get("name") or request.args.get("ticker")
    
    if not val:
        return jsonify({"error": "name 또는 ticker 파라미터가 필요합니다."})

    val_upper = val.upper()
    
    # 종목 판별 로직
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
        price = get_us_stock_price(val_upper)
        final_name = val

    return jsonify({"name": final_name, "price": price})

if __name__ == "__main__":
    app.run()
