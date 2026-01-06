from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import yfinance as yf

app = Flask(__name__)
# [핵심] Flask 시스템 전체에 한글 변환 금지 명령을 내립니다.
app.json.ensure_ascii = False 

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
        return jsonify({"error": "파라미터가 필요합니다."})

    val_upper = val.upper()
    final_name = val
    price = "조회 실패"

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

    # 이제 jsonify만 써도 위에서 설정한 ensure_ascii = False 덕분에 한글이 나옵니다.
    return jsonify({"name": final_name, "price": price})

if __name__ == "__main__":
    app.run()
