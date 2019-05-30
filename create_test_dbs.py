#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pymongo

if __name__ == "__main__":
    dbs = pymongo.MongoClient(host="localhost", port=27017).yyj
    news_test = dbs.news_test
    news_test.drop()
    sina_add_url = dbs.sina_add_url
    sina_all_news = sina_add_url.find()
    i = 0
    line = [0,0,0,0,0]
    for news in sina_all_news:
        del news['_id']
        if news['category'] == 'news' and line[0] < 10:
            news_test.insert_one(news)
            line[0] += 1
        if news['category'] == 'tech' and line[1] < 10:
            news_test.insert_one(news)
            line[1] += 1
        if news['category'] == 'finance' and line[2] < 10:
            news_test.insert_one(news)
            line[2] += 1
        if news['category'] == 'mil' and line[3] < 10:
            news_test.insert_one(news)
            line[3] += 1
        if news['category'] == 'sports' and line[4] < 10:
            news_test.insert_one(news)
            line[4] += 1
        if sum(line) > 50:
            break
