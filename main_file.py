#!usr/bin/env python
# --coding:utf-8--
# @Author: MillerD
# @Date:   2016-09-07T15:35:52+08:00
# @Last modified by:   MillerD
# @Last modified time: 2016-09-07T15:39:16+08:00



# 参考链接：https://www.zhihu.com/question/36081767/answer/65820705
import requests
import json
import os
import base64
from Crypto.Cipher import AES
import redis

r = redis.Redis(host="127.0.0.1", port=6379);
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

def dataEncode(data):

    modulus = '00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7';
    nonce = '0CoJUm6Qyw8W8jud';
    pubKey = '010001';
    data = json.dumps(data);
    secKey = createSecretKey(16);
    encText = aesEncrypt(aesEncrypt(data, nonce), secKey);
    encSecKey = rsaEncrypt(secKey, pubKey, modulus);
    _data = {
        'params': encText,
        'encSecKey': encSecKey
    };
    return _data;

def getFollows(userId, offset=0, limit=5):
    flesh = 0;
    repeatEl = [];
    _data = {
        'offset': offset,
        'limit': limit,
        'order': True
    };
    req = requests.post('http://music.163.com/weapi/user/getfollows/{}'.format(userId), headers=headers, data=dataEncode(_data));
    content = req.text.encode('utf-8', 'ignore');
    content = json.loads(content);
    for user in content['follow']:
        # print(r.hget(user['userId'], 'nickname'));
        if not r.hget(user['userId'], 'userId'):
            r.hmset(user['userId'], user);
            flesh += 1;
        else:
            repeatEl.append(user['userId']);
    print('get follows {}, flesh {}, repeat {}:{}'.format(offset+limit, flesh, len(repeatEl), repeatEl));
    if content['more'] == True:
        offset += limit;
        getFollows(userId, offset, limit);

def getFolloweds(userId, offset=0, limit=5):
    flesh = 0;
    repeatEl = [];
    _data = {
        'userId': userId,
        'offset': offset,
        'limit': limit,
        'csrf_token': ''
    };
    req = requests.post('http://music.163.com/weapi/user/getfolloweds?csrf_token=', headers=headers, data=dataEncode(_data));
    content = req.text.encode('utf-8', 'ignore');
    content = json.loads(content);
    for user in content['followeds']:
        # print(r.hget(user['userId'], 'nickname'));
        if not r.hget(user['userId'], 'userId'):
            r.hmset(user['userId'], user);
            flesh += 1;
        else:
            repeatEl.append(user['userId']);
    print('get followeds {}, flesh {}, repeat {}:{}'.format(offset+limit, flesh, len(repeatEl), repeatEl));
    # 接口会返回前1100条数据
    if content['more'] == True and len(repeatEl) != limit:
        offset += limit;
        getFolloweds(userId, offset, limit);

def mainly():
    userId = raw_input("Please enter starter ID: ");
    getFolloweds(userId, 0, 100);
    getFollows(userId, 0, 100) ;

mainly();
