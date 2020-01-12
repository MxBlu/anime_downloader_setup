import re
import requests
from collections import OrderedDict
from bs4 import BeautifulSoup, SoupStrainer

nyaa_base = "https://nyaa.si"
nyaa_search_f = "https://nyaa.si/?f=0&c=1_2&q={:s}&s=seeders&o=desc"
nyaa_rss_user_f = "https://nyaa.si/?page=rss&u={:s}"
nyaa_catchup_rss_f = "https://nyaa.si/?page=rss&f=0&c=1_2&q={:s}&u={:s}"

results_s = '.torrent-list tbody tr'
title_s = [
    'td[colspan="2"] a:nth-of-type(2)',
    'td[colspan="2"] a' # Fallback
]

subber_user_s = 'a[title="Trusted"], a[title="User"]'

subber_x = re.compile(r'^\s*\[(.+?)\]')
res_x = {
    '480': re.compile(r'480'),
    '720': re.compile(r'720'),
    '1080': re.compile(r'1080')
}

def search(term):
    r = requests.get(nyaa_search_f.format(term))
    soup = BeautifulSoup(r.text, 'lxml')
    results = []
    for node in soup.select(results_s):
        cl = node.get('class')[0]

        title = node.select_one(title_s[0])
        if title == None:
            title = node.select_one(title_s[1])

        quality = 'Trusted' if cl == 'success' else 'Remake' if cl == 'danger' else cl

        results.append({
            'title': title.string,
            'quality': quality,
            'associatedTorrent': nyaa_base + title.get('href')
        })
    return results

def get_subbers(results):
    subbers = OrderedDict()
    for r in results:
        m = subber_x.search(r['title'])
        subber = m.group(1) if m else None
        if subber == None:
            continue

        res = ""
        for r_v, r_x in res_x.items():
            if r_x.search(r['title']):
                res = r_v
                break

        if subber not in subbers:
            subbers[subber] = {
                'subber': subber,
                'availableRes': { res },
                'quality': r['quality'],
                'associatedTorrent' : {
                    'title': r['title'],
                    'link': r['associatedTorrent']
                }
            }
        else:
            subbers[subber]['availableRes'].add(res)

    return subbers

def get_subber_from(torrent_url):
    r = requests.get(torrent_url)
    soup = BeautifulSoup(r.text, 'lxml')

    node = soup.select_one(subber_user_s)
    return node.string

def get_subber_rss(user):
    return nyaa_rss_user_f.format(user)

def get_catchup_rss(user, search_term):
    return nyaa_catchup_rss_f.format(search_term, user)