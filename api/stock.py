from flask import Flask, request, Response
import requests
from bs4 import BeautifulSoup
import yfinance as yf

app = Flask(__name__)

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
        if not data.empty:
            return f"{float(data['Close'].iloc[-1]):.2f}"
        return "조회 실패"
    except:
        return "조회 실패"

@app.route("/api/stock", methods=["GET"])
def stock_api():
    val = request.args.get("name") or request.args.get("ticker")
    if not val:
        return Response('{"error": "파라미터 필요"}', content_type="application/json; charset=utf-8")

    val_upper = val.upper()
    price = "조회 실패"
    final_name = val

    if val == "삼성전자" or val == "005930":
        price = get_korean_stock_price("005930")
        final_name = "삼성전자"
    elif val == "LG전자" or val == "066570":
        price = get_korean_stock_price("066570")
        final_name = "LG전자"
    elif val_upper in ["TSLA", "테슬라"]:
        price = get_us_stock_price("TSLA")
        final_name = "테슬라"
    else:
        price = get_us_stock_price(val_upper)
        final_name = val

    # [핵심] JSON 라이브러리를 쓰지 않고 직접 문자열을 만듭니다. 
    # 이렇게 하면 파이썬이 멋대로 한글을 유니코드로 바꿀 기회가 사라집니다.
    json_string = f'{{"name": "{final_name}", "price": "{price}"}}'
    
    # UTF-8 인코딩을 명시하여 브라우저에 한글임을 선언합니다.
    return Response(json_string, content_type="application/json; charset=utf-8")

if __name__ == "__main__":
    app.run()
