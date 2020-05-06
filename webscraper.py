import os
import sys
import config
import logging
import kakao_win_API
import requests as rs
from time import sleep
from bs4 import BeautifulSoup
from datetime import datetime


def _scrap_by_uid(user):
    logging.info("SCRAP user "+user)
    soup = BeautifulSoup(rs.get(config.base_url + user).text, 'html.parser')
    p_num = soup.find(class_='problem_title tooltip-click')
    p_num, p_text = p_num.text, p_num['title']
    mem = soup.find(class_='memory').text
    p_time = soup.find(class_='time').text
    res = soup.find(class_='result').text
    time = soup.find(class_='real-time-update')['title']
    return p_num, p_text, mem, p_time, res, time


def _make_msg(user, p_num, p_text, mem, p_time, res, time):
    return user + " " + p_num + " " + p_text + "\n" + \
           mem + "kb " + p_time + "ms " + res + \
           "\n" + ''.join(time.split()[3:5])


def check_db_diff():
    logging.info("=== START CHECKING ===")
    with open(config.USER_DB, 'r', encoding='utf-8') as db:
        last_solve_time = db.readlines()
        for idx, user in enumerate(config.user_id):
            data, time = _scrap_by_uid(user)
            if time != last_solve_time[idx].strip():
                msg = _make_msg(user, *data, time)
                last_solve_time[idx] = time + '\n'
                logging.info("UPDATE user " + user)
                kakao_win_API.send(config.kakao_opentalk_name, msg)
                logging.info("SEND MESSAGE BELOW\n"+msg)
            sleep(config.user_request_interval)

    logging.info("=== START RECODING ===")
    with open(config.USER_DB, 'w+', encoding='utf-8') as db:
        for time in last_solve_time:
            db.write(time)
    logging.info("=== GET SLEEP ===")
    sleep(config.total_request_interval)


def init_db():
    logging.info("=== INIT USER DATA ===")
    with open(config.USER_DB, 'w+', encoding='utf-8') as db:
        for user in config.user_id:
            *_, time = _scrap_by_uid(user)
            db.write(time + '\n')
            logging.info("UPDATE user " + user)
            sleep(config.user_request_interval)


# LOGGING ----------------------------------------------------------------------

if not os.path.isdir(config.LOG_DIR):
    os.makedirs(config.LOG_DIR)
logging.basicConfig(
    level=logging.INFO,
    filename=os.path.join(config.LOG_DIR, f'{datetime.now():%Y%m%d}.log'),
    format='[%(asctime)s][%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)

logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))


# MAIN ------------------------------------------------------------------------
def scraper():
    logging.info("=== START WEB SCRAPER ===")
    init_db()
    while True:
        try:
            check_db_diff()
        except KeyboardInterrupt:
            logging.info("=== END WEB SCRAPER ===")
        except Exception as e:
            logging.error(e)

if __name__ == '__main__':
    scraper()

