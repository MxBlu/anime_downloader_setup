#!/usr/bin/env python3

import sys, os, errno, atexit
import json

import nyaa
import qbittorrent
from helper import *

config = {}

download_path_f = "{:s}/{:s} [{:s}]"
catchup_f = "{:s} - Catchup"

def load_config():
    global config
    try:
        with open("config.json", 'r') as f:
            config = json.load(f)
    except IOError as e:
        if e.errno == errno.ENOENT:
            pass
        else:
            raise e

def save_config():
    with open("config.json", 'w') as f:
        json.dump(config, f, indent=4)

atexit.register(save_config)

def init_config():
    load_config()

    if 'config_path' not in config:
        config['config_path'] = os.path.expandvars(input("Enter qBittorrent config path: "))
    if 'download_path' not in config:
        config['download_path'] = os.path.expandvars(input("Enter download path: "))
    if qbittorrent.check_lock(config['config_path']):
        print("Please close qBittorrent")
        sys.exit(1)

def handle_subber(search_term):
    torrents = nyaa.search(search_term)
    subbers = nyaa.get_subbers(torrents)

    print("Subbers available:")
    for sub in subbers.values():
        print("{:s} [{:s}] - {:s}".format(sub['subber'], sub['quality'], ', '.join(sub['availableRes'])))
        print("\tEx.: {:s}".format(sub['associatedTorrent']['title']))

    subber_k = input_or("Choose subber", list(subbers.keys())[0])
    if subber_k not in subbers:
        raise Exception('Invalid subber')
    subber =  subbers[subber_k]

def handle_anime(anime):
    search_term = input_or("Enter search term", anime.split()[0])
    subber = handle_subber(search_term)

    res = input_or("Choose resolution", list(subber['availableRes'])[0])
    search_res = "{:s} {:s}".format(search_term, res)
    
    user = nyaa.get_subber_from(subber['associatedTorrent']['link'])
    subber_rss = nyaa.get_subber_rss(user)
    catchup_rss = nyaa.get_catchup_rss(user, search_res)

    download_path = download_path_f.format(config['download_path'], anime, subber['subber'])
    
    qbittorrent.add_rss_feed(config['config_path'], subber['subber'], subber_rss)
    qbittorrent.add_download_rule(config['config_path'], anime, anime, download_path, subber_rss, search_res)
    
    qbittorrent.add_rss_feed(config['config_path'], catchup_f.format(anime), catchup_rss)
    qbittorrent.add_download_rule(config['config_path'], catchup_f.format(anime), anime, download_path, catchup_rss, search_res)

def main():
    init_config()

    while True:
        anime = input("Enter anime [Enter to exit]: ")
        if anime == "":
            return

        handle_anime(anime)

if __name__ == "__main__":
    main()