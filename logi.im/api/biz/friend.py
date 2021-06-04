import os
import io
import sys
import time
import json
import shutil
import random
from urllib.parse import urlsplit
from concurrent.futures import ThreadPoolExecutor

import requests
from PIL import Image

TIME_OUT = 20
MAX_TRY = 3
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36'
WHITE_LIST = ['dianr.cn']

CONF_PATH = 'asset/data/friends.json'
CONF_HANDLED_PATH = 'asset/data/friends-cached.json'
IMG_PATH = 'asset/img'


class FriendLinkDoctor:
    def __init__(self, init=False):
        if init:
            conf = CONF_PATH
        else:
            conf = CONF_HANDLED_PATH

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

    @staticmethod
    def try_your_best(fn, fail):
        for _ in range(MAX_TRY):
            try:
                return fn()
            except Exception as e:
                msg = str(e)
                if msg.find('get local issuer certificate') > -1:
                    return True
                elif msg.find('certificate has expired') > -1:
                    return fail()
                elif msg.find('doesn\'t match') > -1:
                    return fail()
                print(e)
                time.sleep(random.randint(2, 5))
                pass

        return fail()

    @staticmethod
    def save_image(friend):
        requests.packages.urllib3.disable_warnings()
        link = friend['link']

        def save():
            resp = FriendLinkDoctor.get(friend['avatar'], verify=False)

            path = urlsplit(friend['avatar']).path
            if path.find('.') > 0:
                suffix = path.split('.')[-1]
            else:
                suffix = resp.headers.get('content-type').split('/')[-1]
                if suffix == 'jpeg':
                    suffix = 'jpg'

            prefix = f'{IMG_PATH}/{urlsplit(link).netloc}'

            for img in os.listdir(IMG_PATH):
                if img.find(prefix) > -1:
                    friend['avatar'] = img
                    return friend

            name = f'{prefix}.{suffix}'
            img = Image.open(io.BytesIO(resp.content))
            img.thumbnail((200, 200))
            img.save(name)
            friend['avatar'] = name

        FriendLinkDoctor.try_your_best(
            save, lambda: print(f'failure: {link}')
        )
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
            if (FriendLinkDoctor.get(url_404).text.find(error_text) == -1):
                return True
            return fail()

        return FriendLinkDoctor.try_your_best(req, fail)

    def save_config(self, results):
        # random.shuffle(results)
        with open(CONF_HANDLED_PATH, mode='w', encoding='utf-8') as f:
            json.dump(
                results,
                f,
                ensure_ascii=False,
                sort_keys=True,
                indent=4
            )

    def concurrent_task(self, fn):
        futures, pool = [], ThreadPoolExecutor(10)
        for friend in self.friends:
            futures.append(pool.submit(fn, friend))

        results = []
        for future in futures:
            results.append(future.result())

        self.save_config(results)

        return results

    def check_boby(self):
        def check(friend):
            friend['online'] = self.is_online(friend['link'])
            return friend

        return self.concurrent_task(check)

    def get_images(self):
        if os.path.exists(IMG_PATH):
            shutil.rmtree(IMG_PATH)
        os.mkdir(IMG_PATH)

        self.concurrent_task(self.save_image)


if __name__ == '__main__':
    if len(sys.argv) != 1 and sys.argv[1] == 'init':
        FriendLinkDoctor(init=True).get_images()
    else:
        FriendLinkDoctor().check_boby()
