import os
import io
import sys
import time
import json
import shutil
import random
from datetime import datetime
from urllib.parse import urlsplit
from concurrent.futures import ThreadPoolExecutor

import requests
from PIL import Image

TIME_OUT = 20
MAX_TRY = 3
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36'
WHITE_LIST = ['dianr.cn', 'noheart.cn',
              'get233.com', 'zpblogs.cn', 'ax127.fun']
TODAY = datetime.today().strftime('%Y-%m-%d')

CONF_PATH = 'asset/data/friends.json'
CONF_CACHED_PATH = 'asset/data/friends-cached.json'
IMG_PATH = 'asset/img'


class FriendLinkDoctor:
    def __init__(self, init=False):
        self.init = init
        conf = CONF_PATH if init else CONF_CACHED_PATH

        with open(conf, mode='r', encoding='utf-8') as f:
            self.friends = json.load(f)

    @staticmethod
    def get(url, **args):
        return requests.get(
            url,
            timeout=TIME_OUT,
            headers={"User-Agent": USER_AGENT},
            **args
        )

    """                 
    msg = str(e)
    if msg.find('get local issuer certificate') > -1:
        return True
    elif msg.find('certificate has expired') > -1:
        return fail()
    elif msg.find('sslv3 alert handshake failure') > -1:
        return fail()
    elif msg.find('Connection reset by peer') > -1:
        return fail()
    elif msg.find('length mismatch') > -1:
        return fail()
    elif msg.find('doesn\'t match') > -1:
        return fail()
    elif msg.find('Temporary failure in name resolution') > -1:
        return fail()
    elif msg.find('No address associated with hostname') > -1:
        return fail()
    elif msg.find('Name or service not known') > -1:
        return fail()
    elif msg.find('getaddrinfo failed') > -1:
        return fail()
    print(e) 
    """
    @staticmethod
    def try_your_best(fn, fail):
        for _ in range(MAX_TRY):
            try:
                return fn()
            except Exception as e:
                msg = str(e)
                if msg.find('get local issuer certificate') > -1:
                    return True
                print(msg)
                time.sleep(random.randint(2, 5))
                pass

        return fail()

    @staticmethod
    def save_image(friend):
        requests.packages.urllib3.disable_warnings()
        link = friend['link']
        identity = urlsplit(link).netloc

        def save():
            resp = FriendLinkDoctor.get(friend['avatar'], verify=False)

            path = urlsplit(friend['avatar']).path
            if path.find('.') > 0:
                suffix = path.split('.')[-1]
            else:
                suffix = resp.headers.get('content-type').split('/')[-1]
                if suffix == 'jpeg':
                    suffix = 'jpg'

            name = f'{IMG_PATH}/{identity}.{suffix}'
            img = Image.open(io.BytesIO(resp.content))
            img.thumbnail((200, 200))
            img.save(name)
            friend['avatar'] = name

        def fail():
            for img in os.listdir(IMG_PATH):
                if img.find(identity) > -1:
                    friend['avatar'] = f'{IMG_PATH}/{img}'
                    print(f'failure, using cached file: {link}')
                    return
            print(f'failure: {link}')

        FriendLinkDoctor.try_your_best(save, fail)
        return friend

    @staticmethod
    def is_online(url):
        for host in WHITE_LIST:
            if url.find(host) > 0:
                return True

        url_404 = f'{url}/not-exists/be4b3658-2045-4468-8530-cc11c2145849'
        error_text = 'www.beian.miit.gov.cn/state/outPortal/loginPortal.action'

        def fail():
            print(f'offline: {url}')
            return False

        def req():
            if FriendLinkDoctor.get(url_404).text.find(error_text) == -1:
                return True
            return fail()

        return FriendLinkDoctor.try_your_best(req, fail)

    def save_config(self, results):
        if self.init:
            def retrieve_online_date(friend, old_result):
                old_friend = list(
                    filter(lambda old_friend: old_friend['link'] == friend['link'], old_result))
                if len(old_friend) == 1 and 'lastOnlineDate' in old_friend[0]:
                    friend['lastOnlineDate'] = old_friend[0]['lastOnlineDate']
                return friend

            with open(CONF_CACHED_PATH, mode='r', encoding='utf-8') as f:
                old_result = json.load(f)
                results = list(map(lambda friend: retrieve_online_date(
                    friend, old_result), results))

        with open(CONF_CACHED_PATH, mode='w', encoding='utf-8') as f:
            json.dump(
                results,
                f,
                ensure_ascii=False,
                sort_keys=True,
                indent=2
            )

    def concurrent_task(self, fn):
        futures, pool = [], ThreadPoolExecutor(5)
        for friend in self.friends:
            futures.append(pool.submit(fn, friend))

        results = []
        for future in futures:
            results.append(future.result())

        self.save_config(results)

        return results

    def check_boby(self):
        def check(friend):
            if self.is_online(friend['link']):
                friend['lastOnlineDate'] = TODAY
            return friend

        return self.concurrent_task(check)

    def get_images(self):
        if os.path.exists(IMG_PATH):
            shutil.copytree(IMG_PATH, IMG_PATH + '_copied')
            # shutil.rmtree(IMG_PATH)
        else:
            os.mkdir(IMG_PATH)

        self.concurrent_task(self.save_image)


if __name__ == '__main__':
    if len(sys.argv) != 1 and sys.argv[1] == 'init':
        FriendLinkDoctor(init=True).get_images()
    else:
        FriendLinkDoctor().check_boby()
