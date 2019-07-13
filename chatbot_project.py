# -*- coding: utf-8 -*-

import urllib.request
import urllib.parse
from bs4 import BeautifulSoup
from flask import Flask
from slack import WebClient
from selenium import webdriver
import time
from slack.web.classes.blocks import *
from slack.web.classes.elements import *
from slackeventsapi import SlackEventAdapter
from slack.web.classes import extract_json

SLACK_TOKEN = "xoxb-672078783539-689721577381-W5c1jfH0el8ZfzZhGe6Z3ulo"
SLACK_SIGNING_SECRET = "8cbee2327c1d9214b94837b38afd001c"

app = Flask(__name__)

slack_events_adaptor = SlackEventAdapter(SLACK_SIGNING_SECRET, "/listening", app)
slack_web_client = WebClient(token=SLACK_TOKEN)


def _salary_job(text):
    url = "http://www.jobkorea.co.kr/Salary/"
    req = urllib.request.Request(url)

    sourcecode = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(sourcecode, "html.parser")

    f_Text = []  # 인기기업
    d_Text = []  # 대기업
    j_Text = []  # 중견기업
    i = 0
    for keyword in soup.find_all("div", class_="company"):
        if i < 50:
            f_Text.append(keyword.get_text().strip())
        elif i < 100 and i >= 50:
            d_Text.append(keyword.get_text().strip())
        elif i < 150 and i >= 100:
            j_Text.append(keyword.get_text().strip())
        i += 1
    fs_Text = []  # 인기기업 연봉
    ds_Text = []  # 대기업 연봉
    js_Text = []  # 중견기업 연봉
    i = 0
    for keyword in soup.find_all("div", class_="salary"):
        if i < 50:
            fs_Text.append(keyword.get_text().strip())
        elif i < 100 and i >= 50:
            ds_Text.append(keyword.get_text().strip())
        elif i < 150 and i >= 100:
            js_Text.append(keyword.get_text().strip())
        i += 1

    message1 = []
    message2 = []
    message3 = []
    message1.append(SectionBlock(text="*<인기검색 기업별 평균 연봉>*"))
    message1.append(DividerBlock())
    message2.append(SectionBlock(text="*<대기업 평균 연봉>*"))
    message2.append(DividerBlock())
    message3.append(SectionBlock(text="*<중견기업 평균 연봉>*"))
    message3.append(DividerBlock())
    for i in range(10):
        message1.append(SectionBlock(text=f_Text[i] + " : " + fs_Text[i] + " 만원"))
        message1.append(DividerBlock())
        message2.append(SectionBlock(text=d_Text[i] + " : " + ds_Text[i] + " 만원"))
        message2.append(DividerBlock())
        message3.append(SectionBlock(text=j_Text[i] + " : " + js_Text[i] + " 만원"))
        message3.append(DividerBlock())

    if text == 1:
        return message1
    elif text == 2:
        return message2
    else:
        return message3
#지역별 찾기
def _crawl_job_chart(region_code):
    url = "http://www.saramin.co.kr/zf_user/jobs/list/domestic?loc_mcd=" + str(
        100000 + region_code[1]) + "&panel_type=&search_optional_item=n&search_done=y&panel_count=y"
    req = urllib.request.Request(url)
    sourcecode = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(sourcecode, "html.parser")

    titles = []
    explains = []
    descs = []
    href_list = []
    imgg = []
    image_block_list = []
    for i, img in enumerate(soup.find_all("span", class_="logo")):
        if i < 10:
            temp = img.find("img")
            imgg.append(temp.get("src"))
            image_block_list.append(ImageElement(
                image_url=temp.get("src"),
                alt_text="기업사진"
            ))

    for i, title in enumerate(soup.find_all("span", class_="corp")):
        if i < 10:
            titles.append(title.get_text().strip())

    for i, explain in enumerate(soup.find_all("strong", class_="tit")):
        if i < 10:
            explains.append(explain.get_text().strip())

    for i, desc in enumerate(soup.find_all("ul", class_="desc")):
        if i < 10:
            word = desc.get_text().strip().replace("\n", "\t").split()
            descs.append(word[0]+"\t"+word[1])

    for hrefs in (soup.find_all("ul", class_="list_product")):
        for i, href in enumerate(hrefs.find_all("li", class_="item")):
            if i < 10:
                href_list.append("http://www.saramin.co.kr" + href.find("a")["href"])

    print('titles: ', titles)
    print('explains: ', explains)
    print('desks: ', descs)
    print('href: ', href_list)

    block_result = []

    block_result.append(SectionBlock(text="*<"+ str(region_code[0]) + " 지역 채용 추천>*"))
    block_result.append(DividerBlock())
    for i in range(len(titles)):
        block_result.append(SectionBlock(
            text='추천기업' + str(i + 1) + ' : <' + href_list[i] + ' | ' + titles[i] + '>'
                      + "\n채용부문 : " + explains[i] + "\n학력사항 : " + descs[i] + "\n",
            accessory=image_block_list[i]))
        block_result.append(DividerBlock())
    return block_result

#직무별 찾기
def _crawl_work_chart(region_code):
    print("region_code : ", region_code)
    url = "http://www.saramin.co.kr/zf_user/jobs/list/job-category?cat_cd=" + str(region_code[1]) + "&panel_type=&search_optional_item=n&search_done=y&panel_count=y"
    print("url : ", url)
    req = urllib.request.Request(url)
    sourcecode = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(sourcecode, "html.parser")

    titles = []
    explains = []
    descs = []
    href_list = []
    imgg = []
    image_block_list = []

    for i, img in enumerate(soup.find_all("span", class_="logo")):
        if i < 10:
            temp = img.find("img")
            imgg.append(temp.get("src"))
            image_block_list.append(ImageElement(
                image_url=temp.get("src"),
                alt_text="기업사진"
            ))

    for i, title in enumerate(soup.find_all("span", class_="corp")):
        print(title)
        if i < 10:
            titles.append(title.get_text().strip())

    for i, explain in enumerate(soup.find_all("strong", class_="tit")):
        if i < 10:
            explains.append(explain.get_text().strip())

    for i, desc in enumerate(soup.find_all("ul", class_="desc")):
        if i < 10:
            descs.append(desc.get_text().strip().replace("\n", "\t"))

    for hrefs in (soup.find_all("ul", class_="list_product")):
        for i, href in enumerate(hrefs.find_all("li", class_="item")):
            if i < 10:
                href_list.append("http://www.saramin.co.kr" + href.find("a")["href"])


    print('titles: ', titles)
    print('explains: ', explains)
    print('desks: ', descs)
    print('href: ', href_list)

    block_result = []
    block_result.append(SectionBlock(text="*<"+ str(region_code[0]) + " 직무별 채용 추천>*"))
    block_result.append(DividerBlock())
    for i in range(len(titles)):
        block_result.append(SectionBlock(
            text='추천기업' + str(i + 1) + ' : <' + href_list[i] + ' | ' + titles[i] + '>'
                      + "\n채용부문 : " + explains[i] + "\n학력사항 : " + descs[i] + ".\n",
            accessory=image_block_list[i]))
        block_result.append(DividerBlock())
    return block_result

#셀레니움으로 이메일 확인
def check_mail_selenium(text1, text2):
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('window-size=1920x1080')
    #chrome_options=options
    driver = webdriver.Chrome('C:\Dev_ssafy\chromedriver_win32 (2)\chromedriver.exe')
    driver.implicitly_wait(10)
    # url에 접근한다.
    driver.get('https://nid.naver.com/nidlogin.login')
    # 아이디/비밀번호를 입력해준다.

    id = ''
    pw = ''
    driver.execute_script("document.getElementsByName('id')[0].value=\'" + id + "\'")
    time.sleep(0.5)
    driver.execute_script("document.getElementsByName('pw')[0].value=\'" + pw + "\'")
    time.sleep(0.5)
    driver.find_element_by_xpath('//*[@id="frmNIDLogin"]/fieldset/input').click()
    time.sleep(0.5)
    driver.find_element_by_class_name('btn_cancel').click()
    time.sleep(0.5)
    driver.get('https://mail.naver.com/')
    print('check')
    time.sleep(0.5)
    driver.find_element_by_id("searchHelp").click()
    time.sleep(0.5)
    element = driver.find_element_by_id("ipt_sender")
    element.send_keys(text1)
    time.sleep(0.5)
    element = driver.find_element_by_id("ipt_query")
    element.send_keys(text2)
    time.sleep(0.5)
    driver.find_element_by_class_name('ngfix').click()
    time.sleep(0.5)

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    subject = []
    mail_sender_list = []
    href_list = []
    for data in (soup.find_all("div", class_="subject")):
        href = data.find("a")["href"]
        mail_subject = data.find('strong').get_text()
        # 메일10개만 가져오기
        if len(subject) <= 10:
            subject.append(mail_subject[6:])
            href_list.append("https://mail.naver.com" + href)

    for data in (soup.find_all("div", class_="name _ccr(lst.from)")):
        mail_sender = data.find('a').get_text().strip()
        # print('mail_sender : ', mail_sender)
        # 보낸이 10개만 가져오기
        if len(mail_sender_list) <= 10:
            mail_sender_list.append(mail_sender)

    print('href: ', href_list)
    print('subject : ', subject)
    print('mail_sender : ', mail_sender_list)

    # result = []
    # for i in range(len(subject)):
    #     result.append('보낸이 : ' + mail_sender_list[i] + "\n메일제목 : <" + href_list[i] + ' | ' + subject[i] + '>' + "\n")
    # return result
    block_result = []
    block_result.append(SectionBlock(text="*<"+str(text1) + " 기업 채용 지원 메일 확인>*\n\n"))
    block_result.append(DividerBlock())
    for i in range(len(subject)):
        block_result.append(SectionBlock(
            text='보낸이 : ' + mail_sender_list[i] + "\n메일제목 : <" + href_list[i] + ' | ' + subject[i] + '>' + "\n"))
        block_result.append(DividerBlock())
    return block_result

#미들웨어
def _search_job_chart(text):
    if "서울" in text:
        keyword = ("서울", 1000)
        job_result = _crawl_job_chart(keyword)
        return job_result
    elif "광주" in text:
        keyword = ("광주", 3000)
        job_result = _crawl_job_chart(keyword)
        return job_result
    elif "대구" in text:
        keyword = ("대구", 4000)
        job_result = _crawl_job_chart(keyword)
        return job_result
    elif "대전" in text:
        keyword = ("대전", 5000)
        job_result = _crawl_job_chart(keyword)
        return job_result
    elif "부산" in text:
        keyword = ("부산", 6000)
        job_result = _crawl_job_chart(keyword)
        return job_result
    elif "데이터베이스" in text:
        keyword = ("데이터베이스", 416)
        job_result = _crawl_work_chart(keyword)
        return job_result
    elif "웹" in text:
        keyword = ("웹", 404)
        job_result = _crawl_work_chart(keyword)
        return job_result
    elif "응용" in text:
        keyword = ("응용", 407)
        job_result = _crawl_work_chart(keyword)
        return job_result
    elif "네트워크" in text:
        keyword = ("네트워크", 402)
        job_result = _crawl_work_chart(keyword)
        return job_result
    elif "시스템" in text:
        keyword = ("시스템", 408)
        job_result = _crawl_work_chart(keyword)
        return job_result
    elif "ERP" in text:
        keyword = ("ERP", 409)
        job_result = _crawl_work_chart(keyword)
        return job_result
    elif "연봉" in text:
        if "인기" in text:
            result = _salary_job(1)
            return result
        elif "대기업" in text:
            result = _salary_job(2)
            return result
        else:
            result = _salary_job(3)
            return result
    elif "메일" in text:
        print('메일 확인')
        if "CJ" in text:
            job_result = check_mail_selenium("CJ", "채용")
            return job_result
        elif "한화" in text:
            job_result = check_mail_selenium("한화", "채용")
            return job_result
        elif "롯데" in text:
            job_result = check_mail_selenium("롯데", "채용")
            return job_result
        elif "LG" in text:
            job_result = check_mail_selenium("발신전용", "LG")
            return job_result
        elif "ssafy" in text:
            job_result = check_mail_selenium("ssafy", "지원")
            return job_result
        else:
            block_result=[]
            block_result.append(SectionBlock(text="기업명이 잘못 입력 됬습니다! 다시 입력해주세요!!^^"))
            return block_result
    elif "안녕" in text:
        block_result = []
        block_result.append(SectionBlock(text="안녕하세요~! 좋은 하루 되세요!!"))
        return block_result
    else:
        block_result = []
        block_result.append(SectionBlock(text="<다음과 같이 말씀해주세요>\n예시1)  \"_[광주] 지역 채용 추천해줘_ \"\n예시2)  \"_[웹개발자] 채용 추천해줘_ \"\n예시3)  \"_[대기업] [연봉] 알려줘_ \"\n예시4)  \"_[롯데] 채용 [메일] 확인해줘_ \""))
        return block_result

client_msg_id = ""
@slack_events_adaptor.on("app_mention")
def app_mentioned(event_data):
    global client_msg_id
    channel = event_data["event"]["channel"]
    text = event_data["event"]["text"]
    if client_msg_id == event_data["event"]["client_msg_id"]:
        return
    client_msg_id = event_data["event"]["client_msg_id"]
    message = _search_job_chart(text)
    try:
        slack_web_client.chat_postMessage(
            channel=channel,
            blocks = extract_json(message)
        )
    except:
        pass

@app.route("/", methods=["GET"])
def index():
    return "<h1>Server is ready.</h1>"

if __name__ == '__main__':
    app.run('0.0.0.0', port=8080)