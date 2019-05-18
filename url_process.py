#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pymongo
import redis

client = pymongo.MongoClient(host='localhost', port=27017)
db = client.yyj
#sina_test = db.sina_test
sina_test = db.sina
result = sina_test.find()
s = set()
tech = 0
news = 0
mil = 0
finance = 0
sports = 0
i = 0
for url in result:
    url_1 = url['url']
    cate = url_1.split('.')[0]
    cate = cate.split(":")
    cate = cate[1][2:]
    if cate == "tech":
        tech += 1
    if cate == "news":
        news += 1
    if cate == "mil":
        mil += 1
    if cate == "finance":
        finance += 1
    if cate == "sports":
        sports += 1
    s.add(cate)
print("总数为："+ str(i))
print(s)
print(len(s))

print("tech" + str(tech))
print("news" + str(news))
print("mil" + str(mil))
print("finance" + str(finance))
print("sports" + str(sports))


def category():
    client = pymongo.MongoClient(host='localhost', port=27017)
    db = client.yyj
    result = db.sina.find()
    for record in result:
        url_1 = record['url']
        cate = url_1.split('.')[0]
        cate = cate.split(":")
        cate = cate[1][2:]
        record['category'] = cate
        print(cate)
        db.sina_add_url.insert_one(record)



