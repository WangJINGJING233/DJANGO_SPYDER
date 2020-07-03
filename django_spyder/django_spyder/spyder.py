# -*- coding: utf-8 -*-

#     _____
#    / ___/  _   __    ____  __    __    __
#   / /__   / / / /   / __ \ \ \  /  \  / /
#  / ___/  / /_/ /   / / / /  \ \/ /\ \/ /
# /_/     /____\_\  /_/ /_/    \__/  \__/

import os
import sys
import re
import time
import random
import requests
import datetime as dt
import json
import pymysql
import warnings
import logging

# warnings.filterwarnings("ignore")
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(filename)s:%(lineno)s - %(levelname)s: %(message)s')


def timer(function):
    def wrapper(*args, **kwargs):
        time_start = time.time()
        logging.info(time_start)
        res = function(*args, **kwargs)
        time_end = time.time()
        logging.info(time_end)
        logging.info(time_end - time_start)
        return res

    return wrapper


class Weibo(object):
    _headers = [
        "Mozilla/5.0 (Linux; Android 6.0.1; Moto G (4)) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Mobile Safari/537.36",
        "Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Mobile Safari/537.36",
        "Mozilla/5.0 (Linux; Android 8.0; Pixel 2 Build/OPD3.170816.012) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Mobile Safari/537.36Mozilla/5.0 (Linux; Android 8.0.0; Pixel 2 XL Build/OPD1.170816.004) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Mobile Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_1 like Mac OS X) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.0 Mobile/14E304 Safari/602.1",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (iPad; CPU OS 11_0 like Mac OS X) AppleWebKit/604.1.34 (KHTML, like Gecko) Version/11.0 Mobile/15A5341f Safari/604.1",
        "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Mobile Safari/537.36Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.18362"
    ]
    # _user_info_url = "https://m.weibo.cn/api/container/getIndex?containerid=10505{uid}"
    _user_info_url = "https://m.weibo.cn/profile/info?uid={uid}"
    # _weibo_info_url = "https://m.weibo.cn/api/container/getIndex?page_type=03&containerid=107603{uid}&page={page}"
    _weibo_info_url = "https://m.weibo.cn/api/container/getIndex?containerid=107603{uid}&page={page}"
    _weibo_detail_url = "https://m.weibo.cn/detail/{id}"
    _user_keys = ['id',
                  'screen_name',
                  'gender',
                  'statuses_count',
                  'follow_count',
                  'followers_count',
                  'description',
                  'profile_image_url',
                  'cover_image_phone']
    _weibo_keys = ['id',
                   'bid',
                   'user_id',
                   'screen_name',
                   'created_at',
                   'source',
                   'text',
                   'pics',
                   'media',
                   'reposts_count',
                   'attitudes_count',
                   'comments_count',
                   'retweet_id']
    _user_mysql_config = {
        'host': 'localhost',
        'port': 3306,
        'user': 'root',
        'password': 'root',
        'database': 'db_weibo',
        'charset': 'utf8mb4'
    }
    _weibo_mysql_config = {
        'host': 'localhost',
        'port': 3306,
        'user': 'root',
        'password': 'root',
        'database': 'db_weibo',
        'charset': 'utf8mb4'
    }

    def __init__(self, config):
        """初始化"""
        self.uid = config['uid']
        self.screen_name = config['screen_name']
        self.cookies = config['cookies']
        self.user = dict()
        self.filename = ""

    def handle_request(self, url):
        """请求响应"""
        # https://m.weibo.cn/detail/4452673212653363 服务器走丢了，状态码400
        # https://m.weibo.cn/detail/4472859173013373 cookie用户才能打开，状态码200
        logging.info(url)
        for i in range(1, 11):
            try:
                response = requests.get(url,
                                        headers={"User-Agent": random.choice(self._headers)},
                                        cookies={"Cookie": self.cookies},
                                        timeout=5)
                if response.status_code == 200:
                    time.sleep(random.uniform(2, 3))
                    return response
                elif response.status_code == 400:
                    logging.error(url)
                    return None
                logging.info("Request status code {0} retry for {1} times".format(response.status_code, i))
            except Exception as e:
                logging.error("Request error and retry for {0} times".format(i))
                logging.error(e)
            time.sleep(60)
        self.exit("failed for too many times and exit")

    def correct_time(self, created_at):
        """修正显示时间"""
        if u"前" in created_at:
            created_at = dt.datetime.now().strftime("%Y-%m-%d")
        elif u"昨天" in created_at:
            created_at = (dt.datetime.now() - dt.timedelta(days=1)).strftime("%Y-%m-%d")
        elif len(created_at) == 5:
            created_at = dt.datetime.now().strftime("%Y-") + created_at
        return dt.datetime.strptime(created_at, "%Y-%m-%d")

    def correct_pics_url(self, url):
        """修正图片信息"""
        return url[url.rfind("/") + 1:url.rfind(".")]

    def correct_text(self, text):
        """修正文本"""
        mtext = text.replace("/status/", "https://m.weibo.cn/status/"). \
            replace("src=\"//h5.sinaimg", "src=\"https://h5.sinaimg"). \
            replace("src=\'//h5.sinaimg", "src=\'https://h5.sinaimg"). \
            replace("/n/", "https://m.weibo.cn/n/"). \
            replace("http://u1.sinaimg.cn/upload/2014/10/16/timeline_card_small_video_default.png",
                    "https://h5.sinaimg.cn/upload/2015/09/25/3/timeline_card_small_video_default.png")
        return mtext

    def correct_pics(self, mblog):
        """修正图片"""
        if not mblog.get("pics"): return ""
        pic_num = mblog['pic_num'] if mblog['pic_num'] <= 9 else 9  # 最多显示9张图
        if pic_num > 9:
            weibo_detail_response = self.handle_request(self._weibo_detail_url.format(uid=mblog['idstr']))
            if not weibo_detail_response: return None
            mpics = re.search(r"\"pic_ids\": (?P<mpics>\[[\s\S]*?\])", weibo_detail_response.text, re.U)
            if not mpics: return ""
            mpics = eval(mpics.group("mpics"))
        else:
            mpics = [mblog['pics'][i]['pid'] for i in range(pic_num)]
        return ",".join(mpics)

    def correct_media(self, mblog):
        """获取多媒体文件video（视频）,article（文章）,webpage（外链）,live（直播）,hongbao（红包）,topic（话题）"""
        if mblog.get('page_info') and mblog['page_info'].get('type'):
            return mblog['page_info']['type']
        return ""

    def add_user(self, users):
        """添加作者信息"""
        muser = []
        for user in users:
            tuser = {key: value for key, value in user.items() if key in self._user_keys}
            tuser["gender"] = 1 if tuser["gender"] == "m" else 0
            # tuser["profile_image_url"] = self.correct_pics_url(tuser["profile_image_url"])
            # tuser["cover_image_phone"] = self.correct_pics_url(tuser["cover_image_phone"])
            muser.append(tuser)
        return muser

    def insert_user_info(self, users):
        """插入用户信息"""
        users = self.add_user(users)
        try:
            conn = pymysql.connect(**self._user_mysql_config)
            cursor = conn.cursor()
            table = "tb_user"
            cols = ",".join('`{}`'.format(key) for key in self._user_keys)
            values = ",".join('%({})s'.format(key) for key in self._user_keys)
            update = ",".join(["`{0}`=values({0}) ".format(key) for key in self._user_keys])
            sql = "INSERT INTO {table}({cols}) VALUES({values}) ON DUPLICATE KEY UPDATE {update}". \
                format(table=table, cols=cols, values=values, update=update)
            print(sql)
            cursor.executemany(sql, users)
            conn.commit()
        except pymysql.Error as e:
            logging.info(e)
            conn.rollback()
        finally:
            cursor.close()
            conn.close()

    def add_og_weibo(self, mblog):
        """原创微博"""
        mcard = {key: None for key in self._weibo_keys}
        mcard['id'] = mblog['idstr']
        mcard['bid'] = mblog['bid']
        mcard['source'] = mblog['source']
        mcard['created_at'] = self.correct_time(mblog['created_at'])
        mcard['text'] = self.correct_text(mblog['text'])
        mcard['pics'] = self.correct_pics(mblog)
        mcard['media'] = self.correct_media(mblog)
        if mblog.get('reposts_count'):
            mcard['reposts_count'] = mblog['reposts_count'] if isinstance(mblog['reposts_count'], int) else 1e6
            mcard['comments_count'] = mblog['comments_count'] if isinstance(mblog['comments_count'], int) else 1e6
            mcard['attitudes_count'] = mblog['attitudes_count'] if isinstance(mblog['attitudes_count'], int) else 1e6
        else:
            mcard['reposts_count'], mcard['comments_count'], mcard['attitudes_count'] = 0, 0, 0
        mcard['user_id'], mcard['screen_name']
        if mblog.get('user') is None:
            mcard['user_id'], mcard['screen_name'] = "2016713117", "微博客服"
        else:
            mcard['user_id'], mcard['screen_name'] = mblog['user']['id'], mblog['user']['screen_name']
        mcard['retweet_id'] = mblog['retweeted_status']['idstr'] if mblog.get('retweeted_status') is not None else ""
        return mcard

    def add_weibo_info(self, cards):
        """添加微博"""
        mcards = []
        for card in cards:
            if card['card_type'] != 9: continue
            # 添加原创微博
            mcards.append(self.add_og_weibo(card['mblog']))
            # 添加转发微博
            if card['mblog'].get('retweeted_status'):
                mcards.append(self.add_og_weibo(card['mblog']['retweeted_status']))
        return mcards

    def insert_weibo_info(self, cards):
        """插入微博信息"""
        cards = self.add_weibo_info(cards)
        try:
            conn = pymysql.connect(**self._weibo_mysql_config)
            cursor = conn.cursor()
            table = "tb_weibo"
            cols = ",".join('`{}`'.format(key) for key in self._weibo_keys)
            values = ",".join('%({})s'.format(key) for key in self._weibo_keys)
            update = ",".join(["`{0}`=values({0}) ".format(key) for key in self._weibo_keys])
            sql = "INSERT INTO {table}({cols}) VALUES({values}) ON DUPLICATE KEY UPDATE {update}". \
                format(table=table, cols=cols, values=values, update=update)
            print(sql)
            cursor.executemany(sql, cards)
            conn.commit()
        except pymysql.Error as e:
            logging.error(e)
            conn.rollback()
        finally:
            cursor.close()
            conn.close()

    def get_user_info(self, uid):
        """获取用户信息"""
        logging.info("Enter Weibo get_user_info")
        user_info_url = self._user_info_url.format(uid=uid)
        user_info_response = self.handle_request(user_info_url)
        try:
            user_info_response = user_info_response.json()
            user = user_info_response['data']['user']
            if user['screen_name'] != self.screen_name:
                self.exit("uid and screen_name do not match")
            self.insert_user_info([user])
            self.user = user
            return user
        except json.decoder.JSONDecodeError:
            logging.info(user_info_response.text)
            self.exit("uid error and return wrong json")

    def get_one_page_weibo(self, page):
        """获取单页微博"""
        weibo_info_url = self._weibo_info_url.format(uid=self.user['id'], page=page)
        weibo_info_response = self.handle_request(weibo_info_url)
        try:
            weibo_info_response = weibo_info_response.json()
            return weibo_info_response
        except json.decoder.JSONDecodeError:
            logging.info(weibo_info_response.text)
            self.exit("weibo error and return wrong json")

    def get_all_weibo_info(self):
        """获取所有微博"""
        logging.info("Enter Weibo get_all_weibo_content")
        # 页码不准确
        total_page = self.user['statuses_count'] // 10 + 10
        if total_page>10: total_page=2;
        for page in range(1, total_page):
            # for page in range(0, total_page, 100):
            weibo_info_response = self.get_one_page_weibo(page)
            cards = weibo_info_response['data']['cards']
            self.insert_weibo_info(cards)

    def exit(self, info):
        """程序退出"""
        sys.exit(info)

    def start(self):
        """启动爬虫"""
        logging.info("Enter Weibo start")
        self.get_user_info(self.uid)
        self.get_all_weibo_info()


@timer
def test_user_insert():
    config = json.load(open("config.json"))
    wb = Weibo(config=config)
    fp = open("/Users/xuyizhan/PycharmProjects/WeiboSpyder/Spyder/PS3保罗/PS3保罗.txt")
    line = fp.readline()
    cnt = 0
    users = []
    while True:
        # for i in range(100):
        line = fp.readline()
        if not line: break
        card = json.loads(line)
        if card['mblog'].get('retweeted_status') and card['mblog']['retweeted_status'].get('user'):
            user = card['mblog']['retweeted_status']['user']
            users.append(user)
            if len(users) > 1000:
                logging.info(cnt)
                wb.insert_user_info(users)
                users = []
            cnt += 1
    if len(users) > 0:
        wb.insert_user_info(users)
    fp.close()


@timer
def test_weibo_insert():
    config = json.load(open("config.json"))
    wb = Weibo(config=config)
    fp = open("/Users/xuyizhan/PycharmProjects/WeiboSpyder/Spyder/PS3保罗/PS3保罗.txt")
    line = fp.readline()
    cnt = 0
    cards = []
    while True:
        line = fp.readline()
        if not line: break
        cnt += 1
        # if cnt < 7000: continue
        card = json.loads(line)
        if len(cards) > 1000:
            logging.info(cnt)
            wb.insert_weibo_info(cards)
            cards = []
        cards.append(card)
    if len(cards) > 0:
        wb.insert_weibo_info(cards)
    fp.close()


def test_one_weibo():
    config = json.load(open("config.json"))
    wb = Weibo(config=config)
    fp = open("/Users/xuyizhan/PycharmProjects/WeiboSpyder/Spyder/PS3保罗/PS3保罗.txt")
    # fp = open("/Users/xuyizhan/PycharmProjects/WeiboSpyder/Spyder/jimsimons/jimsimons.txt")
    line = fp.readline()
    while True:
        line = fp.readline()
        if not line: break
        card = json.loads(line)
        if card['mblog']['id'] == '4479415151219490':
            res = wb.add_weibo_info([card])
            for i in res:
                logging.info(i)
            break
    fp.close()


def test_video():
    config = json.load(open("config.json"))
    wb = Weibo(config=config)
    fp = open("/Users/xuyizhan/PycharmProjects/WeiboSpyder/Spyder/PS3保罗/PS3保罗.txt")
    line = fp.readline()
    cnt = 0
    while True:
        line = fp.readline()
        if not line: break
        card = json.loads(line)
        if card['mblog'].get('page_info'):
            logging.info(card)
            logging.info(os.linesep)


def test_one_page():
    config = json.load(open("config.json"))
    wb = Weibo(config=config)
    wb.get_user_info(config['uid'])
    response = wb.get_one_page_weibo(123)
    wb.insert_weibo_info(response['data']['cards'])


@timer
def main(user_id,screen_name,cookies):
    config = {"uid": user_id,
              "screen_name": screen_name,
              "cookies": cookies}
    wb = Weibo(config=config)
    wb.start()
    # res = wb.handle_request("https://m.weibo.cn/detail/4518762000954861")
    # print(res.text)


# if __name__ == "__main__":
#     main()
#     # test_user_insert()
#     # test_weibo_insert()
#     # test_one_weibo()
#     # test_video()
#     # test_one_page()
