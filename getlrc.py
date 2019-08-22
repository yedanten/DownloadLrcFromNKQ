
import os
import requests
import json
from requests.adapters import HTTPAdapter
import time
import sys
import threading
import math
from threading import Thread
import opencc
import base64
import os

def search_from_netease(song_full_name):
    cc = opencc.OpenCC('t2s')
    try:
        singer, song = song_full_name.split(' - ')
    except Exception as e:
        singer = False
        song = False

    headers = {
        'Cache-Control': 'no-cache',
        'Host': 'musicapi.leanapp.cn',
        'Pragma': 'no-cache',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
    }

    s = requests.Session()
    s.mount('http://', HTTPAdapter(max_retries = 5))
    s.mount('https://', HTTPAdapter(max_retries = 5))
    req = s.get('http://127.0.0.1:3000/search', params = {'keywords': song_full_name}, headers = headers, timeout = None)
    resp = req.json()
    
    try:
        if singer:
            for x in resp['result']['songs']:
                for artist in x['artists']:
                    if (cc.convert(artist['name'].lower()) in cc.convert(singer.lower())) or (cc.convert(singer.lower()) in cc.convert(artist['name'].lower())):
                        return x['id']
            return False
        return resp['result']['songs'][0]['id']
    except Exception as e:
        return False
        

def get_lrc_from_netease(song_id):
    headers = {
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
    }
    s = requests.Session()
    s.mount('http://', HTTPAdapter(max_retries = 5))
    s.mount('https://', HTTPAdapter(max_retries = 5))
    req = s.get('http://127.0.0.1:3000/lyric', params = {'id': song_id}, headers = headers, timeout = None)
    resp = req.json()
    
    try:
        return resp['lrc']['lyric']
    except Exception as e:
        return False

def search_from_kugou(song_full_name):
    headers = {
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
    }
    proxy = {
        'http': 'http://127.0.0.1:1080',
        'https': 'http://127.0.0.1:1080'
    }
    s = requests.Session()
    s.mount('http://', HTTPAdapter(max_retries = 5))
    s.mount('https://', HTTPAdapter(max_retries = 5))
    req = s.get('https://songsearch.kugou.com/song_search_v2', params = {'keyword': song_full_name, 'filter': 2, 'platform': 'WebFilter'}, headers = headers, timeout = None, proxies = proxy)
    resp = req.json()
    
    try:
        if resp['data']['lists']:
            return resp['data']['lists'][0]['FileHash']
        return False
    except Exception as e:
        return False

def get_lrc_from_kugou(song_hash):
    proxy = {
        'http': 'http://127.0.0.1:1080',
        'https': 'http://127.0.0.1:1080'
    }
    s = requests.Session()
    s.mount('http://', HTTPAdapter(max_retries = 5))
    s.mount('https://', HTTPAdapter(max_retries = 5))
    r = s.get('https://wwwapi.kugou.com/yy/index.php', params = {'r': 'play/getdata', 'hash': song_hash, 'mid': '1'}, timeout = None, proxies = proxy)
    resp = r.json()
    
    try:
        return resp['data']['lyrics']
    except Exception as e:
        return False

def search_from_qq(song_full_name):
    cc = opencc.OpenCC('t2s')

    try:
        singer, song = song_full_name.split(' - ')
    except Exception as e:
        singer = False
        song = False

    headers = {
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
        'Referer': 'https://y.qq.com/portal/search.html'
    }
    s = requests.Session()
    s.mount('http://', HTTPAdapter(max_retries = 5))
    s.mount('https://', HTTPAdapter(max_retries = 5))
    r = s.get('https://c.y.qq.com/soso/fcgi-bin/client_search_cp', params = {'w': song_full_name, 'format': 'json'}, timeout = None, headers = headers)
    resp = r.json()
    try:
        if singer:
            if resp['data']['song']['list']:
                for songinfo in resp['data']['song']['list']:
                    for singer_r in songinfo['singer']:
                        if (cc.convert(singer_r['name'].lower()) in cc.convert(singer.lower())) or (cc.convert(singer.lower()) in cc.convert(singer_r['name'].lower())):
                            return songinfo['songmid']
                return False
            return False
        return resp['data']['song']['list'][0]['songmid']
    except Exception as e:
        return False

def get_lrc_from_qq(songmid):
    headers = {
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
        'Referer': 'https://y.qq.com/portal/player.html',
        'Host': 'c.y.qq.com'
    }
    s = requests.Session()
    s.mount('http://', HTTPAdapter(max_retries = 5))
    s.mount('https://', HTTPAdapter(max_retries = 5))
    r = s.get('https://c.y.qq.com/lyric/fcgi-bin/fcg_query_lyric_new.fcg', params = {'songmid': songmid, 'format': 'json'}, timeout = None, headers = headers)
    resp = r.json()
    try:
        return base64.b64decode(resp['lyric']).decode('utf-8')
    except Exception as e:
        return False

def from_netease(song_full_name):
    lrc_text = ''
    song_id = search_from_netease(song_full_name)
    if song_id:
        lrc_text = get_lrc_from_netease(song_id)
        if lrc_text:
            with open('lrc\\' + song_full_name + '.lrc', 'w', encoding = 'utf-8') as f:
                f.write(lrc_text)
            return True
        return False
    return False

def from_kugou(song_full_name):
    song_hash = search_from_kugou(song_full_name)
    if song_hash:
        lrc_text = get_lrc_from_kugou(song_hash)
        if lrc_text:
            with open('lrc\\' + song_full_name + '.lrc', 'w', encoding = 'utf-8') as f:
                f.write(lrc_text)
            return True
        return False
    return False

def from_qq(song_full_name):
    songmid = search_from_qq(song_full_name)
    if songmid:
        lrc_text = get_lrc_from_qq(songmid)
        if lrc_text:
            with open('lrc\\' + song_full_name + '.lrc', 'w', encoding = 'utf-8') as f:
                f.write(lrc_text)
            return True
        return False
    return False

def main(file_list):
    all_count = str(len(file_list))

    for i, song in enumerate(file_list):
        song_full_name = os.path.splitext(song)[0]

        print('[INFO][' + str(i) + '/' + all_count + ']:' + song_full_name + '\tdownloading...')

        if from_netease(song_full_name):
            print('[INFO][' + str(i) + '/' + all_count + ']:' + song_full_name + '\tdown')
            continue
        elif from_kugou(song_full_name):
            print('[INFO][' + str(i) + '/' + all_count + ']:' + song_full_name + '\tdown')
            continue
        elif from_qq(song_full_name):
            print('[INFO][' + str(i) + '/' + all_count + ']:' + song_full_name + '\tdown')
            continue
        else:
            with open('fail.txt', 'a', encoding = 'utf-8') as f:
                f.write(song + '\n')

if __name__ == '__main__':
    with open('filename.txt', 'r', encoding = 'utf-8') as f:
        file_list = f.read().split('\n')

    length = len(file_list)
    n = math.ceil(length/1000)
    thread_list = []

    for x in range(n):
        thread_list.append(threading.Thread(target = main, args = (file_list[math.floor(x / n * length):math.floor((x + 1) / n * length)], )))
    for thread in thread_list:
        thread.start()
