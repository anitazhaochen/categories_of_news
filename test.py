#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import time
import jieba
import pymongo
import pandas as pd

client = pymongo.MongoClient('localhost',27017)
db  = client['yyq']
pk10 = db['sina_test']
data = pd.DataFrame(list(pk10.find()))
del data['_id']
data.dropna()
data = data[['title','url','content']]
#print(len(data))
content = data.content.values.tolist()
content_S = []
for line in content:
    current_segment = jieba.lcut(line)
    if len(current_segment) > 1 and current_segment != '\r\n':
        content_S.append(current_segment)
#print(content_S[0])

df_content = pd.DataFrame({"content_S": content_S})
#print(df_content.head())

#stopwords = pd.read_csv('./baidu_stopwords.txt', index_col=False, sep='\n',names=['stopword'],header=None)
#stopwords = pd.read_fwf('./baidu_stopwords.txt')
stopwords = pd.read_csv('./baidu_stopwords.txt', sep="\n", header=None,
                        names=["stopword"])

def clean_stopwords(contents, stopwords):
    contents_clean = []
    all_words = []
    for line in contents:
        line_clean = []
        for word in line:
            if word in stopwords:
                #print(word)
                continue
            line_clean.append(word)
            all_words.append(str(word))
        contents_clean.append(line_clean)
    return contents_clean, all_words


a,b = clean_stopwords(df_content.content_S.values.tolist(), stopwords.stopword.values.tolist())
print(a[0])
