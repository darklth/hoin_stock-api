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
        # 네이버 금융의 콤마(,) 포함된 가격 그대로 반환
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
    # 1. 입력값 받기
    val = request.args.get("name") or request.args.get("ticker")
    if not val:
        return Response('{"error": "파라미터 필요"}', content_type="application/json; charset=utf-8")

    val_upper = val.upper().strip()
    price = "조회 실패"
    final_name = val

    # 2. 판별 로직 (한국 티커인지 먼저 확인)
    if val_upper == "005930" or val == "삼성전자":
        price = get_korean_stock_price("005930")
        final_name = "삼성전자"
    elif val_upper == "066570" or val == "LG전자":
        price = get_korean_stock_price("066570")
        final_name = "LG전자"
    elif val_upper in ["TSLA", "테슬라"]:
        price = get_us_stock_price("TSLA")
        final_name = "테슬라"
    elif val_upper in ["AAPL", "애플"]:
        price = get_us_stock_price("AAPL")
        final_name = "애플"
    else:
        # 등록되지 않은 것은 일단 미국 주식으로 검색 시도
        price = get_us_stock_price(val_upper)
        final_name = val_upper

    # 3. JSON 문자열 조립 (f-string 사용으로 인코딩 보호)
    json_string = f'{{"name": "{final_name}", "price": "{price}"}}'
    
    # 4. 강제 UTF-8 응답
    return Response(json_string, content_type="application/json; charset=utf-8")

if __name__ == "__main__":
    app.run()
