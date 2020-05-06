import requests as rs
from bs4 import BeautifulSoup
from time import sleep
import send_kakao
base_url = "https://www.acmicpc.net/status?user_id="
uid= ["jhb1365","sunsu2737","rlaalswo9","bhdj0107","happiness96",
      "gg_k","tbnsok40","lightjean","soohwajo412","xogns12356","ysj2527",
      "soy1904"]
      # "audwls9095","spacerangerlightyear",
      # "soominnm","y0ungju","hk924","cake16290","gayoungkr",
      # "sonrg53","hello_jh",]
#"ys000123"
def scrap_by_uid(user_id):
    soup = BeautifulSoup(rs.get(base_url+user_id).text,'html.parser')
    P = soup.find_all(class_='problem_title tooltip-click')
    M = soup.find_all(class_='memory')
    T = soup.find_all(class_='time')
    R = soup.find_all(class_='result')
    ST = soup.find_all(class_='real-time-update')
    print(user_id)
    # for p_num,mem,time,result,sol_time in zip(P,M,T,R,ST):
    #     print(p_num['title'],mem.text,time.text,result.text,sol_time['title'])

    return P,M,T,R,ST

def check_db_diff():
    with open('last.txt', 'r', encoding='utf-8') as db:
        lastsol = db.readlines()
        for idx, user in enumerate(uid):
            P,M,T,R,ST = scrap_by_uid(user)
            if ST[0]['title'] != lastsol[idx].strip() and R[0].text=="맞았습니다!!":
                msg = user+" "+P[0].text + " " + P[0]['title'] + "\n" + \
                    M[0].text + "kb " + T[0].text + "ms " + R[0].text +\
                      "\n" + ''.join(ST[0]['title'].split()[3:5])
                print(msg)
                lastsol[idx] = ST[0]['title']+'\n'
                send_kakao.send("알고라",msg)
            sleep(10)
    with open('last.txt', 'w+', encoding='utf-8') as db:
        for time in lastsol:
            db.write(time)

def refresh_db():
    with open('last.txt','w+',encoding='utf-8') as db:
        for user in uid:
            _,_,_,_,ST = scrap_by_uid(user)
            db.write(ST[0]['title']+'\n')
            sleep(2)
#init
refresh_db()
while True:
    check_db_diff()
    sleep(300)