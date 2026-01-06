from flask import Flask, request, Response
import requests
from bs4 import BeautifulSoup
import yfinance as yf
import json

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
        # 에러 메시지도 한글로 안전하게 처리
        error_res = json.dumps({"error": "파라미터가 필요합니다."}, ensure_ascii=False)
        return Response(error_res, content_type="application/json; charset=utf-8")

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
    elif val_upper in ["AAPL", "애플"]:
        price = get_us_stock_price("AAPL")
        final_name = "애플"
    else:
        price = get_us_stock_price(val_upper)
        final_name = val

    # [핵심] 딕셔너리를 먼저 만들고, json.dumps로 직접 변환
    result_dict = {"name": final_name, "price": price}
    
    # ensure_ascii=False는 한글을 깨지 말라는 뜻입니다.
    # .encode('utf-8')을 붙여서 바이트 형태로 확실히 변환합니다.
    json_output = json.dumps(result_dict, ensure_ascii=False).encode('utf-8')
    
    # Response에 직접 담아서 내보내면 Vercel이 마음대로 변환하지 못합니다.
    return Response(json_output, content_type="application/json; charset=utf-8")

if __name__ == "__main__":
    app.run()
