import re
import json
import random
from base64 import b64decode

import requests

TIME_OUT = 15
MAX_TRY = 10
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36'
PAGE = 'https://logi.im/about.html'
WHITE_LIST = [
    "myql.xyz",
    "zpblogs.cn",
    "qlogo.cn",
    "zhimg.com",
    "jsdelivr.net",
    "sevencdn.com",
    "spoience.com"
]


def get(url,  headers={}, **args):
    try:
        resp = requests.get(
            url,
            headers={"User-Agent": USER_AGENT},
            allow_redirects=False
        )
        location = resp.headers.get('Location')
        if location:
            url = location
    except Exception:
        pass

    return requests.get(
        url,
        timeout=TIME_OUT,
        headers={
            **headers,
            "User-Agent": USER_AGENT,
        },
        **args
    )


def html_ok(url):
    for host in WHITE_LIST:
        if url.find(host) > 0:
            return True

    try:
        for _ in range(MAX_TRY):
            if get(f'{url}/not-exists/be4b3658-2045-4468-8530-cc11c2145849', allow_redirects=False).status_code in [404, 200]:
                return True
            sleep(0.5)
    except Exception:
        return False

    return Falsec


def img_ok(url):
    if re.findall(r'avatar\/[0-9a-z]+', url):
        return True

    for host in WHITE_LIST:
        if url.find(host) > 0:
            return True

    try:
        for _ in range(MAX_TRY):
            if get(url, headers={"referer": PAGE}).status_code == 200:
                return True
            sleep(0.5)
    except Exception:
        return False

    return False


def check_healthy():
    with open('data.json', mode='r', encoding='utf-8') as f:
        links = json.load(f)

    for link in links:
        link['pageOnline'] = html_ok(link['link'])
        link['avatarOnline'] = img_ok(link['avatar'])
        # if link['pageOnline'] and link['avatarOnline']:
        #     continue

        print(link)

    random.shuffle(links)
    with open('data.json', mode='w', encoding='utf-8') as f:
        json.dump(links, f,  ensure_ascii=False, sort_keys=True, indent=4)


check_healthy()
