#!usr/bin/env python
# --coding:utf-8--
# @Author: MillerD
# @Date:   2016-09-07T15:35:52+08:00
# @Last modified by:   MillerD
# @Last modified time: 2016-09-07T15:39:16+08:00



# 参考链接：https://www.zhihu.com/question/36081767/answer/65820705
# 来源：知乎
# 著作权归作者所有，转载请联系作者获得授权。
import requests
import json
import os
import base64
from Crypto.Cipher import AES
from pprint import pprint
import time
import sys
from math import *
import redis

r = redis.Redis(host="127.0.0.1", port=6379);
userId = '';
results = [];
playList_ids = [];
url = 'http://music.163.com/weapi/v1/resource/comments/R_SO_4_29393669/?csrf_token=';

def aesEncrypt(text, secKey):
    pad = 16 - len(text) % 16;
    text = text + pad * chr(pad);
    encryptor = AES.new(secKey, 2, '0102030405060708');
    ciphertext = encryptor.encrypt(text);
    ciphertext = base64.b64encode(ciphertext);
    return ciphertext;


def rsaEncrypt(text, pubKey, modulus):
    text = text[::-1];
    rs = int(text.encode('hex'), 16)**int(pubKey, 16) % int(modulus, 16);
    return format(rs, 'x').zfill(256);


def createSecretKey(size):
    return (''.join(map(lambda xx: (hex(ord(xx))[2:]), os.urandom(size))))[0:16];

def dataGenerator(limit, offset):

    text = {
        'limit': limit,
        'offset': offset
    };
    modulus = '00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7';
    nonce = '0CoJUm6Qyw8W8jud';
    pubKey = '010001';
    text = json.dumps(text);
    secKey = createSecretKey(16);
    encText = aesEncrypt(aesEncrypt(text, nonce), secKey);
    encSecKey = rsaEncrypt(secKey, pubKey, modulus);
    data = {
        'params': encText,
        'encSecKey': encSecKey
    };
    return data;

def pre_steps(userId):
    headers = {
        'Accept': '*/*',
        'Accept-Language': 'zh-CN,zh;q=0.8,gl;q=0.6,zh-TW;q=0.4',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Referer': 'http://music.163.com',
        'Host': 'music.163.com',
        'Cookie': 'appver=1.5.0.75771;',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.152 Safari/537.36'
    };
    text = {
        'offset': '0',
        'limit': 30,
        'order': True
    };
    modulus = '00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7';
    nonce = '0CoJUm6Qyw8W8jud';
    pubKey = '010001';
    text = json.dumps(text);
    secKey = createSecretKey(16);
    encText = aesEncrypt(aesEncrypt(text, nonce), secKey);
    encSecKey = rsaEncrypt(secKey, pubKey, modulus);
    data = {
        'params': encText,
        'encSecKey': encSecKey
    };
    req = requests.post('http://music.163.com/weapi/user/getfollows/{}?csrf_token='.format(userId), headers=headers, data=data);
    content = req.text.encode('utf-8', 'ignore');
    content = json.loads(content);
    for user in content['follow']:
        r.hmset(user['userId'], user);


userId = raw_input("Please enter user ID: ");
pre_steps(userId);
