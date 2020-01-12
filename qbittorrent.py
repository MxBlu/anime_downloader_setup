import os
import json
from uuid import uuid4

from helper import *

LOCK_PATH = "/rss/storage.lock"
FEED_PATH = "/rss/feeds.json"
DL_PATH = "/rss/download_rules.json"

def check_lock(config_path):
    return os.path.exists(config_path + LOCK_PATH)

def add_rss_feed(config_path, feed_name, feed_url):
    with open(config_path + FEED_PATH, 'r') as f:
        rss_conf = json.load(f)

    if exists(lambda x: x['url'] == feed_url, rss_conf.values()):
        return

    uuid = None
    while True:
        uuid = uuid4()
        if not exists(lambda x: x['uid'] == '{{{:s}}}'.format(str(uuid)), rss_conf.values()):
            break
    
    rss_conf[feed_name] = {
        "uid": "{{{:s}}}".format(str(uuid)),
        "url": feed_url
    }

    with open(config_path + FEED_PATH, 'w') as f:
        json.dump(rss_conf, f, indent=4)

def add_download_rule(config_path, rule_name, category_name, download_path, feed_urls, search_term):
    with open(config_path + DL_PATH, 'r') as f:
        download_conf = json.load(f)

    if rule_name in download_conf:
        raise Exception("Rule name already exists")

    download_conf[rule_name] = {
        "addPaused": None,
        "affectedFeeds": feed_urls,
        "assignedCategory": category_name,
        "createSubfolder": None,
        "enabled": True,
        "episodeFilter": "",
        "ignoreDays": 0,
        "lastMatch": "",
        "mustContain": search_term,
        "mustNotContain": "",
        "previouslyMatchedEpisodes": [ ],
        "savePath": download_path,
        "smartFilter": False,
        "useRegex": False
    }

    with open(config_path + DL_PATH, 'w') as f:
        json.dump(download_conf, f, indent=4)