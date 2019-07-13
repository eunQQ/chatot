# -*- coding: utf-8 -*-
import re
import urllib.request

from bs4 import BeautifulSoup

from flask import Flask
from slack import WebClient
from slackeventsapi import SlackEventAdapter
from xcoin_api_client import *
import sys
import pprint

SLACK_TOKEN = ""
SLACK_SIGNING_SECRET = ""

api_key = ""
api_secret = ""

api = XCoinAPI(api_key, api_secret)

rgParams = {
	"order_currency" : "BTC",
	#"payment_currency" : "KRW"
}

app = Flask(__name__)
# /listening 으로 슬랙 이벤트를 받습니다.
slack_events_adaptor = SlackEventAdapter(SLACK_SIGNING_SECRET, "/listening", app)
slack_web_client = WebClient(token=SLACK_TOKEN)


# 비트코인 현재가
def coin_current_price(text):
    if '현재' in text:
        print('현재 오류')
        result = api.xcoinApiCall("/public/ticker", rgParams)
        print(result)
        average_price = result["data"]["average_price"]
        min_price = result["data"]["min_price"]
        max_price = result["data"]["max_price"]
        print(type(average_price))
        return "비트코인 현재 주가는 " + average_price + "원 입니다.\n" + "24시간 이내 최고가는 " + max_price + "원, 최저가는 " + min_price + "원 입니다."
    elif '잔액' in text:
        print('잔액오류')
        rgParams2 = {
            "currency" : "BTC"
        }
        result = api.xcoinApiCall("/info/balance", rgParams2)
        print(result)
        available_krw = result["data"]["available_krw"]
        in_use_krw = result["data"]["in_use_krw"]
        return "고객의 현재 주문가능한 원화 금액은 " + available_krw + "원 입니다.\n" + "고객의 주문중 묶여있는 원화 금액은 " + in_use_krw + "원입니다."
    else:
        return None
# # 크롤링 함수 구현하기
# def _crawl_portal_keywords(text):
#     url_match = re.search(r'<(http.*?)(\|.*?)?>', text)
#     if not url_match:
#         return '올바른 URL을 입력해주세요.'

#     url = url_match.group(1)
#     source_code = urllib.request.urlopen(url).read()
#     soup = BeautifulSoup(source_code, "html.parser")

#     # 여기에 함수를 구현해봅시다.
#     keywords = []     
#     if "naver" in url :         
#         for data in (soup.find_all("span", class_="ah_k")):             
#             if not data.get_text() in keywords :                 
#             #10위까지만 크롤링하겠습니다.                 
#                 if len(keywords) >= 10 :                     
#                     break                 
#                 keywords.append(data.get_text())                      
#     elif "daum" in url :         
#         for data in soup.find_all("a", class_="link_issue"):             
#             if not data.get_text() in keywords :                 
#                 keywords.append(data.get_text()) 

#     # 키워드 리스트를 문자열로 만듭니다.
#     return '\n'.join(keywords)


# 챗봇이 멘션을 받았을 경우
@slack_events_adaptor.on("app_mention")
def app_mentioned(event_data):
    channel = event_data["event"]["channel"]
    text = event_data["event"]["text"]

    keywords = coin_current_price(text)
    slack_web_client.chat_postMessage(
        channel=channel,
        text=keywords
    )


# / 로 접속하면 서버가 준비되었다고 알려줍니다.
@app.route("/", methods=["GET"])
def index():
    return "<h1>Server is ready.</h1>"

@app.route("/rabbit", methods=["GET"])
def rabbit():
    return "<h1>I'm rabbit.</h1>"


if __name__ == '__main__':
    app.run('0.0.0.0', port=8080)
